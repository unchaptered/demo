from typing import Optional
from injector import singleton, inject
from selenium.webdriver.chrome.webdriver import WebDriver

# Core Dependencies
from core.chrome.chrome_core import ChromeCore
from core.web_scraper_core.web_scarpper_regexp_parser import WebScrapperRegexpParser
from core.web_scraper_core.web_scrapper_link_filter import WebScrapperLinkFilter, WebScrapperLink

import core.web_scraper_core.options.depth_option as WebScrapperDepthOption
import core.web_scraper_core.options.domain_option as WebScrapperDomainOption

# Module Dependencies
from modules.providers.database_provider import DatabaseProvider

@singleton
class WebScraperCore():
    
    @inject
    def __init__(self,
                 chromeCore: ChromeCore,
                 webScrapperRegexpParser: WebScrapperRegexpParser,
                 webScrapperLinkFilter: WebScrapperLinkFilter,
                 databaseProvider: DatabaseProvider) -> None:
        self.chromeCore = chromeCore
        self.webScrapperRegexpParser = webScrapperRegexpParser
        self.webScrapperLinkFilter = webScrapperLinkFilter
        self.databaseProvider = databaseProvider

    async def recursiveScrap(self,
              *,
              driver: WebDriver,
              orgWebScrapperLink: WebScrapperLink):
        
        routinId = orgWebScrapperLink.routinId
        originUrl = orgWebScrapperLink.originUrl
        parentUrl = orgWebScrapperLink.parentUrl
        nowUrl = orgWebScrapperLink.nowUrl
        nowDepth = orgWebScrapperLink.nowDepth
        maxDepth = orgWebScrapperLink.maxDepth
        originDomain = orgWebScrapperLink.originDomain
        domainOption = orgWebScrapperLink.domainOption
        
        print('[🤔🤔]', orgWebScrapperLink.convertDict())
        
        driver.get(nowUrl)
        driver.implicitly_wait(3)
        
        import time
        time.sleep(5)
        
        originHtml = driver.page_source
                
        titles, internalLinks, externalLinks = self.webScrapperRegexpParser.convertUsableMetaData(originHtml=originHtml)
        filteredHtml = self.webScrapperRegexpParser.convertUsableHtmlFormat(originHtml=originHtml)
        
        # [RECORD] 현재 페이지 탐색 결과 저장
        prisma = self.databaseProvider.getPrisma()
        await prisma.connect()
        async with prisma.tx() as txPrisma:
            await txPrisma.websitedocument.upsert(
                where={
                    'routinId_originUrl_parentUrl_nowUrl':  {
                        'routinId': routinId,
                        'originUrl': orgWebScrapperLink.originUrl,
                        'parentUrl': orgWebScrapperLink.parentUrl,
                        'nowUrl': orgWebScrapperLink.nowUrl,
                    }
                },
                data={
                    'create': orgWebScrapperLink.convertDict(isScrapped=True,
                                                             scrappedHtml=filteredHtml),
                    'update': {                        
                        'nowDepth': orgWebScrapperLink.nowDepth,
                        'maxDepth': orgWebScrapperLink.maxDepth,
                        
                        'originDomain': orgWebScrapperLink.originDomain,
                        
                        'domainType': orgWebScrapperLink.domainType.value,
                        'domainOption': orgWebScrapperLink.domainOption,
                        
                        'isScrapped': True,
                        'scrappedHtml': filteredHtml
                    },
                }
            )
        await prisma.disconnect()

        webScrapperLinks = self.webScrapperLinkFilter.filter(routinId=routinId,
                                                             
                                                                originUrl=originUrl,
                                                                parentUrl=parentUrl,
                                                                nowUrl=nowUrl,
                                                                
                                                                nowDepth=nowDepth,
                                                                maxDepth=maxDepth,
                                                                
                                                                originDomain=originDomain,
                                                                domainOption=domainOption,
                                                                
                                                                internalLinks=internalLinks,
                                                                externalLinks=externalLinks)
        
        webScrapperLinks = [
            wLink
            for wLink in webScrapperLinks   
            if wLink.isValidTarget()
        ]
        
        # [RECORD] 현재 페이지에서 파생된 페이지 기록
        await prisma.connect()
        async with prisma.tx() as txPrisma:
            # await txPrisma.websitedocument.create_many(
            #     data=[
            #         wLink.convertDict()
            #         for wLink in webScrapperLinks
            #     ],
            #     skip_duplicates=True
            # )
            print('[CHLID]', len(webScrapperLinks))
            for wLink in webScrapperLinks:

                await txPrisma.websitedocument.upsert(
                    where={
                        'routinId_originUrl_parentUrl_nowUrl':  {
                            'routinId': routinId,
                            'originUrl': orgWebScrapperLink.originUrl,
                            'parentUrl': orgWebScrapperLink.parentUrl,
                            'nowUrl': orgWebScrapperLink.nowUrl,
                        }
                    },
                    data={
                        'create': wLink.convertDict(isScrapped=False,
                                                    scrappedHtml=None),
                        'update': {
                            'nowDepth': orgWebScrapperLink.nowDepth,
                            'maxDepth': orgWebScrapperLink.maxDepth,
                            
                            'originDomain': orgWebScrapperLink.originDomain,
                            
                            'domainType': orgWebScrapperLink.domainType.value,
                            'domainOption': orgWebScrapperLink.domainOption,
                            
                            'isScrapped': False,
                            'scrappedHtml': None
                        },
                    }
                )
        await prisma.disconnect()
        
        if nowDepth > maxDepth:
            return
        
        for wLink in webScrapperLinks:
            await self.recursiveScrap(driver=driver,
                                        orgWebScrapperLink=wLink)
        
    async def recursiveScrapWrapper(self,
                       *,
                       originUrl: str,
                       parentUrl: Optional[str] = 'null',
                       nowUrl: str,
                       nowDepth: int = 0,
                       maxDepth: WebScrapperDepthOption,
                       originDomain: str,
                       domainOption: WebScrapperDomainOption):
        
        
        routinId: int = 1
        
        prisma = self.databaseProvider.getPrisma()
        await prisma.connect()
        async with prisma.tx() as txPrisma:
            prismaWebScrapperLink = await txPrisma.websitedocument.find_first(
                where={
                    'originUrl': originUrl,
                    'parentUrl': parentUrl,
                    'nowUrl': nowUrl
                },
                order={ 'routinId': 'desc' }
            )
            if prismaWebScrapperLink:
                routinId = routinId + prismaWebScrapperLink.routinId
        await prisma.disconnect()
        
        webScrapperList = WebScrapperLink(routinId=routinId,
                        originUrl=originUrl,
                        parentUrl=parentUrl,
                        nowUrl=nowUrl,
                        
                        nowDepth=nowDepth,
                        maxDepth=maxDepth,
                        
                        originDomain=originDomain,
                        domainOption=domainOption)

        with self.chromeCore.getChromeDriver() as driver:
            await self.recursiveScrap(driver=driver,
                                      orgWebScrapperLink=webScrapperList)
            