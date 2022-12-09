import pandas as pd
from pyspark.sql import SparkSession
import re
from operator import add

def f(inp):
    linecount,line = inp
    data = []
    if dictionaryPattern.findall(line):
        language = re.search("[A-Z][a-z]+ ?[A-Z]?[a-z]*",line).group()
        titles = re.findall("(?<=\|[a-z]{2}\|)[^{},|]+(?=[\|}])",line, re.DOTALL)
        for title in titles:
            data.append((title, language, str(linecount-1)))
    return data

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

datafile = open("/home/enwiktionary-20220920-pages-articles-multistream.xml", 'r')
#enwiktionary-20220920-pages-articles-multistream
spark = SparkSession\
        .builder\
        .appName("PythonPi")\
        .getOrCreate()

data = spark.sparkContext.parallelize(enumerate(datafile), 10).map(f).reduce(add)

inPage = 0
page = 0
datafile = open("/home/enwiktionary-20220920-pages-articles-multistream.xml", 'r')
print("halo")
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
                    data.append((title, re.search("(?<===)(.*)(?===)",line).group(), str(saveline)))
    if pageStart.findall(line): inPage = 1

df = pd.DataFrame(data, columns=['Word', 'Language', 'Locations'])
df.to_csv("/home/index.csv", index=False)


