import pandas as pd
from difflib import SequenceMatcher
import re

index = pd.read_csv("/home/index.csv")

def searching(inp):
    
    searchRes = index[index['Word']==inp]   # Vyhladavanie slova v indexe
    if len(searchRes) == 0:
        print("\nWord not found")
        return 0
        
    uniqueLang = []
    for i in range(len(searchRes)):
        if searchRes["Language"].values[i] not in uniqueLang:
            uniqueLang.append(searchRes["Language"].values[i])

    print("\nChoose language by typing in number\n--------------------------")

    for i in range(len(uniqueLang)):
        print(str(i+1) + ") " + uniqueLang[i])    # Listovanie moznych jazykov
    print("--------------------------")
    
    try:
        temp = int(input())
    except:
        print("Input is not a number")
        return 0 

    try:
        language = uniqueLang[temp-1] # Vyberanie jazyka podla inputu
    except:
        print("Invalid number chosen")
        return 0 
    
    findPages = []
    for i in range(len(searchRes)):
        if searchRes["Language"].values[i] == language:
            findPages.append(searchRes["Locations"].values[i])

    # Prerekvizity hotove, nasleduje search
    # Z prerekvizit mame slovo, jazyk a strany, kde sa nachadza
    
    dataFile = open("/home/enwiktionary-20220920-pages-articles-multistream.xml", 'r', encoding="utf8")
    linecount = 0
    page = 0
    inPage = False
    results = []
    numOfPages = 0
    pageEnd = re.compile("</page>")
    pageStart = re.compile("<page>")
    for line in dataFile:
        if linecount > findPages[numOfPages] - 3000:
            inPage = True
        if inPage:
            if pageStart.findall(line):
                temppage = linecount
            if (searchRes["Word"].values[numOfPages] in line) and (language in line):
                findPages[numOfPages] = temppage
                inPage = False
                numOfPages += 1
                if numOfPages == len(findPages):
                    break
        linecount+=1

    findPages = list(dict.fromkeys(findPages))
    numOfPages = 0
    dataFile = open("/home/enwiktionary-20220920-pages-articles-multistream.xml", 'r', encoding="utf8")
    linecount = 0
    page = 0
    numOfPages = 0
    inPage = False
    for line in dataFile:
        if linecount == findPages[numOfPages]:
            inPage = True
            temp = ""
        if inPage:
            if pageEnd.findall(line):
                inPage = False
                numOfPages += 1
                results.append(temp)
                if numOfPages == len(findPages):
                    break
            else:
                temp += line
                temp += "\n"
        linecount+=1
    oglanguages = []
    ogtranslations = []
    for page in results:
        oglanguages.append(re.search("(?<===)([A-Z][a-z]+)(?===)",page).group())
        ogtranslations.append(re.search("(?<=<title>)(.*)(?=<\/title>)",page).group())
    
    if len(results) > 1:
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

    etymo = []
    i=0

    inPage=False
    if "translations" in ogtranslations[chosen]:
        print(re.search(".*(?=\/)",ogtranslations[chosen]).group())
        return searching(re.search(".*(?=\/)",ogtranslations[chosen]).group())
    else:
        for line in results[chosen].splitlines():
            if line:
                if inPage:
                    if re.compile("==").findall(line):
                        print("--------------------------")
                        inPage=False
                    else:
                        print(line)
                else:
                    if re.compile("==[A-Z][a-z]+ ?[A-Z]?[a-z]* ?[A-Z]?[a-z]*==$").findall(line):
                        temp = ("In language " + re.search("(?<===)[A-Z][a-z]+ ?[A-Z]?[a-z]* ?[A-Z]?[a-z]*(?===)",line).group() + ":")
                    if re.compile("===Etymology ?[1-9]?===$").findall(line):
                        inPage=True
                        print(temp)
        print("==========================\nSearch for simillar words?\n--------------------------\n1: Yes\n2: No\n--------------------------")
        if input() == '1':
            treshold = 0.60 # Tu zmenit podobnost slov
            simwords = set()
            for i in index["Word"]:
                if len(str(i)) == len(inp):
                    matchMetric = SequenceMatcher(None, i, inp).ratio()
                    if matchMetric > treshold and matchMetric < 1:
                        simwords.add(i)
            print("--------------------------")
            temp = 0
            arr = []
            for i in simwords:
                temp+=1
                arr.append(i)
                print(str(temp) + ": " + i)
                if temp == 10: break
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
            searching(arr[temp-1])
            return etymo
        else:
            return etymo

if __name__ == "__main__":
    print("Enter word...")

    inp = input()
    result = searching(inp)
    if result != 0:
        for i in result:
            print(i + "--------------------------\n")
    