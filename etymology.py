import pandas as pd
from difflib import SequenceMatcher
import re

index = pd.read_csv("index.csv")

def searching(inp):
    """Main function for searching

    :param inp: user inputted word
    :returns: the etymologies of the word in a string 
    """
    searchRes = index[index['Word']==inp]   # Searching for word in index
    if len(searchRes) == 0:
        print("\nWord not found")
        return 0
        
    uniqueLang = []
    for i in range(len(searchRes)):
        if searchRes["Language"].values[i] not in uniqueLang:   # Finding possible anguages for the word
            uniqueLang.append(searchRes["Language"].values[i])

    print("\nChoose language by typing in number\n--------------------------")

    for i in range(len(uniqueLang)):
        print(str(i+1) + ") " + uniqueLang[i])    # Listing possible languages
    print("--------------------------")
    
    try:
        temp = int(input())
    except:
        print("Input is not a number")
        return 0 

    try:
        language = uniqueLang[temp-1] # Choosing a language based on input
    except:
        print("Invalid number chosen")
        return 0 
    
    findPages = []
    for i in range(len(searchRes)):
        if searchRes["Language"].values[i] == language:
            findPages.append(searchRes["Locations"].values[i])

    # Prereqisites done followed by search
    # Right now we have the word, it's languages and it's locations
    
    #  Update for consultation 5, we need to get the correct page from the word's location
    dataFile = open("data/enwiktionary-20220920-pages-articles-multistream.xml", 'r', encoding="utf8")
    linecount = 0
    page = 0
    inPage = False
    results = []
    numOfPages = 0
    pageEnd = re.compile("</page>")
    pageStart = re.compile("<page>")
    for line in dataFile:   # Finds line about 3000 lines before entry in index
        if linecount > findPages[numOfPages] - 3000:
            inPage = True
        if inPage:  # When within 3000 lines, starts search for page start
            if pageStart.findall(line): # Found page start
                temppage = linecount
            if (searchRes["Word"].values[numOfPages] in line) and (language in line):   # When the word in found inside the page, line of page is saved
                findPages[numOfPages] = temppage
                inPage = False
                numOfPages += 1
                if numOfPages == len(findPages):
                    break
        linecount+=1
    # With the starts of the pages we continue as we were before

    findPages = list(dict.fromkeys(findPages))
    numOfPages = 0
    dataFile = open("data/enwiktionary-20220920-pages-articles-multistream.xml", 'r', encoding="utf8")
    linecount = 0
    page = 0
    numOfPages = 0
    inPage = False
    for line in dataFile: # We find the begining of the page
        if linecount == findPages[numOfPages]:
            inPage = True
            temp = ""
        if inPage:
            if pageEnd.findall(line):
                inPage = False
                numOfPages += 1
                results.append(temp)    # Append the entire page until the end in results
                if numOfPages == len(findPages):
                    break
            else:
                temp += line
                temp += "\n"
        linecount+=1
    oglanguages = []
    ogtranslations = []
    for page in results:    # We find the translation of the word and language for each found page
        oglanguages.append(re.search("(?<===)([A-Z][a-z]+)(?===)",page).group())
        ogtranslations.append(re.search("(?<=<title>)(.*)(?=<\/title>)",page).group())
    
    if len(results) > 1:    # The word can have multiple translations, we ask user, which one they mean
        print("\nDo you mean?\n--------------------------")
        for i in range(len(results)):
            print(str(i+1) + ") " + ogtranslations[i] + "  -  " + oglanguages[i])
        print("--------------------------")
        try:
            chosen = int(input())
        except:
            print("Input is not a number")
            return 0
        if (chosen < 1) or (chosen > len(results)):
            print("Invalid number chosen")
            return 0 
        else: chosen -= 1
    else:
        chosen = 0 
        print("Found page: "  + ogtranslations[0] + "  -  " + oglanguages[0])
    print("==========================")
    # We have finally chosen only one word
    # Time to find etymology
    etymo = []
    i=0

    inPage=False
    if "translations" in ogtranslations[chosen]:    # Some pages are just translations, then we have to search for the original page
        print(re.search(".*(?=\/)",ogtranslations[chosen]).group()) # This doesn't happen often, but it can make search a bit longer
        return searching(re.search(".*(?=\/)",ogtranslations[chosen]).group())
    else:
        for line in results[chosen].splitlines():
            if line:    # Search for etymologies in the chosen page
                if inPage:
                    if re.compile("==").findall(line):
                        print("--------------------------")
                        inPage=False
                    else:
                        print(line)
                else: # Found etymologies
                    if re.compile("==[A-Z][a-z]+ ?[A-Z]?[a-z]* ?[A-Z]?[a-z]*==$").findall(line):
                        temp = ("In language " + re.search("(?<===)[A-Z][a-z]+ ?[A-Z]?[a-z]* ?[A-Z]?[a-z]*(?===)",line).group() + ":")  # Language of etymology
                    if re.compile("===Etymology ?[1-9]?===$").findall(line):
                        inPage=True
                        print(temp) # Prints all etymologies
        print("==========================\nSearch for similar words?\n--------------------------\n1: Yes\n2: No\n--------------------------")
        if input() == '1':  # Bonus functionality, finds similar words
            treshold = 0.60 # Here change difference treshold
            simwords = set()
            for i in index["Word"]:
                if len(str(i)) == len(inp):
                    matchMetric = SequenceMatcher(None, i, inp).ratio()
                    if matchMetric > treshold and matchMetric < 1:
                        simwords.add(i) # Finds similar words in index of the same length
            print("--------------------------")
            temp = 0
            arr = []
            for i in simwords:
                temp+=1
                arr.append(i)
                print(str(temp) + ": " + i)
                if temp == 10: break   # Prints 10 of the found words
            print("--------------------------")
            try:
                temp = int(input())
            except:
                print("Input is not a number")
                return 0 
            if temp > 10 or temp < 1: 
                print("Input is out of range")
                return 0
            print("Starting search for word " + arr[temp-1] + "...")
            searching(arr[temp-1])  # Searches again for chosen word
            return etymo
        else:
            return etymo

if __name__ == "__main__":
    print("Enter word...")  # Main function, here it all begins

    inp = input()
    result = searching(inp)
    if result != 0:
        for i in result:
            print(i + "--------------------------\n")
    