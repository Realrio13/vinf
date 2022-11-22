import pandas as pd
import re

data=set()

datafile = open("C:\VINF\data\enwiktionary-20220920-pages-articles-multistream.xml", 'r', encoding="utf8")
inPage = 0
page = 0
titlefound = 0
pageStart = re.compile("<page>")
pageEnd = re.compile("</page>")
anyTitle = re.compile("<title>")
ogLanguage = re.compile("===[^=]+===")
capitalLetter = re.compile("[A-Z]")
dictionaryPattern = re.compile("^[*]:? [A-Z][a-z]+ ?[A-Z]?[a-z]*: {{")
transPattern = re.compile("(?<=\|[a-z]{2}\|)([^{},|]*)(?=(\|[a-z])|(}}))")

linecount = 0
for line in datafile:
    if inPage and page > 4:
        if pageEnd.findall(line): inPage = 0
        elif anyTitle.findall(line) and not capitalLetter.findall(line): 
            titlefound = 1
            saveline = linecount - 1
            title = re.search("(?<=<title>)(.*)(?=<\/title>)",line).group()
        elif titlefound and ogLanguage.findall(line):
            titlefound = 0
            if title:
                language = re.search("(?<===)(.*)(?===)",line).group()
                if '=' not in language: 
                    data.add((title, re.search("(?<===)(.*)(?===)",line).group(), str(saveline)))
        elif dictionaryPattern.findall(line):
            language = re.search("[A-Z][a-z]+ ?[A-Z]?[a-z]*",line).group()
            titles = re.findall("(?<=\|[a-z]{2}\|)[^{},|]+(?=[\|}])",line, re.DOTALL)
            for title in titles:
                data.add((title, language, str(saveline)))
    if pageStart.findall(line):
        page+=1
        if page%5000 == 0: 
            print(page)
        inPage = 1
    linecount+=1

df = pd.DataFrame(data, columns=['Word', 'Language', 'Locations'])
df.to_csv("C:\VINF\index.csv", index=False)

    
