# Selenium 모듈 설치
# pip install selenium
from core.chrome.chrome_core import ChromeCore
from core.web_scraper_core.web_scrapper_link_filter import WebScrapperLinkFilter
from core.web_scraper_core.web_scarpper_regexp_parser import WebScrapperRegexpParser

from core.web_scraper_core.web_scraper_core import WebScraperCore, WebScrapperDepthOption, WebScrapperDomainOption

# import core.web_scraper_core.parser.recursive_parser as RecursiveParser
# import core.web_scraper_core.parser.regexp_parser as RegexpParser

webScrapperCore = WebScraperCore(ChromeCore(),
                                 WebScrapperRegexpParser(),
                                 WebScrapperLinkFilter())
webScrapperCore.recursiveScrapping(**{
    'originUrl':'http://wfwf297.com',
    'parentUrl': 'http://wfwf297.com',
    'nowUrl': 'http://wfwf297.com',
    'domain': WebScrapperDomainOption.ONLY_DOMAIN,
    'maxDepth': WebScrapperDepthOption.THREE
})

# chromeCore= WebScraperCore()
# with chromeCore.executeChromeDriver() as driver:
#     driver.get('https://wfwf297.com/')
#     driver.implicitly_wait(10)
    
#     originHtml = driver.page_source
#     with open('result.html', 'w', encoding='utf-8') as file:
#         file.write(originHtml)
        
#     RegexpParser.convertUsableMetaData(originHtml=originHtml)
#     filteredHtml = RegexpParser.convertUsableHtmlFormat(originHtml=originHtml)
    
#     with open('others.html', 'w', encoding='utf-8') as file:
#         file.write(filteredHtml)