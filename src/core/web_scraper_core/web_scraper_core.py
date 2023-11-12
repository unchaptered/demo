from injector import singleton, inject
from selenium.webdriver.chrome.webdriver import WebDriver

# Module Dependencies
from core.chrome.chrome_core import ChromeCore
from core.web_scraper_core.web_scarpper_regexp_parser import WebScrapperRegexpParser
from core.web_scraper_core.web_scrapper_link_filter import WebScrapperLinkFilter


import core.web_scraper_core.options.depth_option as WebScrapperDepthOption
import core.web_scraper_core.options.domain_option as WebScrapperDomainOption

@singleton
class WebScraperCore():
    
    @inject
    def __init__(self,
                 chromeCore: ChromeCore,
                 webScrapperRegexpParser: WebScrapperRegexpParser,
                 webScrapperLinkFilter: WebScrapperLinkFilter) -> None:
        self.chromeCore = chromeCore
        self.webScrapperRegexpParser = webScrapperRegexpParser
        self.webScrapperLinkFilter = webScrapperLinkFilter

    def recursiveScrap(self,
              *,
              driver: WebDriver,
              originUrl: str,
              parentUrl: str,
              nowUrl: str,
              nowDepth: int = 0,
              maxDepth: WebScrapperDepthOption,
              
              originDomain: str,
              domainOption: WebScrapperDomainOption):
        
        # print('[CHECK]', nowUrl, nowDepth, maxDepth)         
        driver.get(nowUrl)
        driver.implicitly_wait(3)
        
        originHtml = driver.page_source
                
        titles, internalLinks, externalLinks = self.webScrapperRegexpParser.convertUsableMetaData(originHtml=originHtml)
        filteredHtml = self.webScrapperRegexpParser.convertUsableHtmlFormat(originHtml=originHtml)
        
        # FILE_NAME = nowUrl
        # FILE_NAME = FILE_NAME.replace('//', '')
        # FILE_NAME = FILE_NAME.replace('/', '_')
        # FILE_NAME = FILE_NAME.replace(':', '')
        # with open(f'{FILE_NAME}.html', 'w', encoding='utf-8') as file:
        #     print('[WRITE]', titles, internalLinks, externalLinks)
        #     file.write(filteredHtml)
        
        webScrapperLinks = self.webScrapperLinkFilter.filter(originUrl=originUrl,
                                                                parentUrl=parentUrl,
                                                                nowUrl=nowUrl,
                                                                
                                                                nowDepth=nowDepth,
                                                                maxDepth=maxDepth,
                                                                
                                                                originDomain=originDomain,
                                                                domainOption=domainOption,
                                                                
                                                                internalLinks=internalLinks,
                                                                externalLinks=externalLinks)
        
        
        if nowDepth > maxDepth:
            print('[BREAK]', nowUrl, nowDepth, maxDepth)
            return
        
        for webScrapperLink in webScrapperLinks:
            # NEXT_URL = f'{originUrl}/{tarLink}'
            # print(, webScrapperLink.domainType.value, webScrapperLink.nextUrl)
            
            # DB에 기록하는 구문이 필요한데? (작업 대상을 기록)
            
            # DB에서 확인하는 구문도 필요함 (이미 작업한 대상인지)
            
            if webScrapperLink.isValidTarget():
                self.recursiveScrap(driver=driver,
                            originUrl=originUrl,
                            parentUrl=parentUrl,
                            nowUrl=webScrapperLink.nextUrl,
                            nowDepth=nowDepth + 1,
                            maxDepth=maxDepth,
                            originDomain=webScrapperLink.originDomain,
                            domainOption=domainOption)
                
            # print(webScrapperLink, webScrapperLink.nowUrl)
        
    def recursiveScrapWrapper(self,
                       *,
                       originUrl: str,
                       parentUrl: str,
                       nowUrl: str,
                       nowDepth: int = 0,
                       maxDepth: WebScrapperDepthOption,
                       originDomain: str,
                       domainOption: WebScrapperDomainOption):
        
        with self.chromeCore.getChromeDriver() as driver:
            self.recursiveScrap(driver=driver,
                        originUrl=originUrl,
                        parentUrl=parentUrl,
                        nowUrl=nowUrl,
                        
                        nowDepth=nowDepth,
                        maxDepth=maxDepth,
                        
                        originDomain=originDomain,
                        domainOption=domainOption)