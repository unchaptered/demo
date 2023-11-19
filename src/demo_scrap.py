# Selenium 모듈 설치
# pip install selenium
import asyncio

from core.chrome.chrome_core import ChromeCore
from core.web_scraper_core.web_scrapper_link_filter import WebScrapperLinkFilter
from core.web_scraper_core.web_scarpper_regexp_parser import WebScrapperRegexpParser

from core.web_scraper_core.web_scraper_core import WebScraperCore, WebScrapperDepthOption, WebScrapperDomainOption

from modules.providers.database_provider import DatabaseProvider

# import core.web_scraper_core.parser.recursive_parser as RecursiveParser
# import core.web_scraper_core.parser.regexp_parser as RegexpParser

webScrapperCore = WebScraperCore(ChromeCore(),
                                WebScrapperRegexpParser(),
                                WebScrapperLinkFilter(),
                                DatabaseProvider())
asyncio.run(webScrapperCore.recursiveScrapWrapper(**{
    'originUrl':'http://wfwf298.com',
    'parentUrl': 'null22',
    'nowUrl': 'http://wfwf298.com',
    
    'nowDepth': 1,
    'maxDepth': WebScrapperDepthOption.TWO,
    
    'originDomain': 'wfwf298.com',
    'domainOption': WebScrapperDomainOption.ONLY_DOMAIN,
}))



# chromeCore= WebScraperCore()
# with chromeCore.executeChromeDriver() as driver:
#     driver.get('https://wfwf298.com/')
#     driver.implicitly_wait(10)
    
#     originHtml = driver.page_source
#     with open('result.html', 'w', encoding='utf-8') as file:
#         file.write(originHtml)
        
#     RegexpParser.convertUsableMetaData(originHtml=originHtml)
#     filteredHtml = RegexpParser.convertUsableHtmlFormat(originHtml=originHtml)
    
#     with open('others.html', 'w', encoding='utf-8') as file:
#         file.write(filteredHtml)