# Selenium 모듈 설치
# pip install selenium
from core.selenium_core import ChromeCore

import core.recursive_parser as RecursiveParser
import core.regexp_parser as RegexpParser

chromeCore= ChromeCore()
with chromeCore.executeChromeDriver() as driver:
    driver.get('https://wfwf297.com/')
    driver.implicitly_wait(10)
    
    originHtml = driver.page_source
    with open('result.html', 'w', encoding='utf-8') as file:
        file.write(originHtml)
        
    RegexpParser.convertUsableMetaData(originHtml=originHtml)
    filteredHtml = RegexpParser.convertUsableHtmlFormat(originHtml=originHtml)
    
    with open('others.html', 'w', encoding='utf-8') as file:
        file.write(filteredHtml)