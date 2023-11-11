import requests
from typing import List

# Cores
import core.recursive_parser as RecursiveParser
import core.regexp_parser as RegexpParser

response = requests.get('http://wfwf297.com/')
    
originHtml = response.text

siteMetaData = RegexpParser.convertUsableMetaData(originHtml)
siteBodyFormat = RegexpParser.convertUsableHtmlFormat(originHtml)

RecursiveParser.executeRecursiveParser(originHtml=siteBodyFormat)
# print('=' * 80)

# for iLink in siteMetaData['internalLinks']:
#     print(iLink)
    
# print('=' * 80)
    
# for eLink in siteMetaData['externalLinks']:
#     print(eLink)


with open('result.html', 'w', encoding='utf-8') as file:
    file.write(response.text)
    
with open('others.html', 'w', encoding='utf-8') as file:
    file.write(siteBodyFormat)