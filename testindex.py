import pandas as pd
from pyspark.sql import SparkSession
import re
from operator import add

#   Indexing program for etymology.py
#   Output is file index.csv, which is needed for etymology.py
#   Required data: enwictionary

def f(inp): # Finds translations of words and returns them
    """Mapper for spark

    :param inp: one line in enwictionary
    :returns: all translations in that line
    """
    linecount,line = inp
    data = []   # array, because one word can have multiple translations in the same language
    if dictionaryPattern.findall(line): # identifies only lines with translations
        language = re.search("[A-Z][a-z]+ ?[A-Z]?[a-z]*",line).group()
        titles = re.findall("(?<=\|[a-z]{2}\|)[^{},|]+(?=[\|}])",line, re.DOTALL)   # saves data
        for title in titles:
            data.append((title, language, str(linecount-1)))    # appends data to array
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
transPattern = re.compile("(?<=\|[a-z]{2}\|)([^{},|]*)(?=(\|[a-z])|(}}))")  # regexes to search in the data

datafile = open("/home/enwiktionary-20220920-pages-articles-multistream.xml", 'r')
#enwiktionary-20220920-pages-articles-multistream
spark = SparkSession\
        .builder\
        .appName("PythonPi")\
        .getOrCreate()

data = spark.sparkContext.parallelize(enumerate(datafile), 10).map(f).reduce(add) # spark function

inPage = 0
page = 0
datafile = open("/home/enwiktionary-20220920-pages-articles-multistream.xml", 'r')
for line in datafile:   # finds titles of pages (they can also be translations)
    if inPage and page > 4: # starts from page 4
        if pageEnd.findall(line): inPage = 0
        elif anyTitle.findall(line) and not capitalLetter.findall(line): # looks only for those titles that don't start with: Translations:word
            titlefound = 1
            saveline = linecount - 1
            title = re.search("(?<=<title>)(.*)(?=<\/title>)",line).group() # finds word from title using regex
        elif titlefound and ogLanguage.findall(line):   # immediatly after word we need to find the language
            titlefound = 0
            if title:
                language = re.search("(?<===)(.*)(?===)",line).group() # getting language for the title word
                if '=' not in language: 
                    data.append((title, re.search("(?<===)(.*)(?===)",line).group(), str(saveline)))  # saving data and languages
    if pageStart.findall(line): inPage = 1

df = pd.DataFrame(data, columns=['Word', 'Language', 'Locations'])
df.to_csv("/home/index.csv", index=False)   # saving to index.csv


