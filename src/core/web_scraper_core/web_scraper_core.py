from injector import singleton, inject

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
        
    def recursiveScrapping(self,
                       *,
                       originUrl: str,
                       parentUrl: str,
                       nowUrl: str,
                       nowDepth: int = 0,
                       maxDepth: WebScrapperDepthOption,
                       domain: WebScrapperDomainOption):
        
        with self.chromeCore.getChromeDriver() as driver:
            driver.get(nowUrl)
            driver.implicitly_wait(10)
            
            originHtml = driver.page_source
                    
            titles, internalLinks, externalLinks = self.webScrapperRegexpParser.convertUsableMetaData(originHtml=originHtml)
            filteredHtml = self.webScrapperRegexpParser.convertUsableHtmlFormat(originHtml=originHtml)
            
            hasLink, targetLinks, nonTargetLinks = self.webScrapperLinkFilter.filter(originUrl=originUrl,
                                                                            nowDepth=nowDepth,
                                                                            maxDepth=maxDepth,
                                                                            domain=domain,
                                                                            internalLinks=internalLinks,
                                                                            externalLinks=externalLinks)
            
            
