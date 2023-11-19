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
        
        if orgWebScrapperLink.nowDepth > orgWebScrapperLink.maxDepth:
            return
        
        prisma = self.databaseProvider.getPrisma()
        await prisma.connect()
        isAlreadyScrappedWebDocs = await prisma.websitedocument.find_first(
            where={
                'routinId': orgWebScrapperLink.routinId,
                'originUrl': orgWebScrapperLink.originUrl,
                'nowUrl': orgWebScrapperLink.nowUrl,
                'parentUrl': {
                    'not': orgWebScrapperLink.parentUrl
                },
                'OR': [
                    { 'isScrapped': True },
                    { 'isAlreadyScrapped': True },
                ],

                # 'isScrapped': True,
                # 'isAlreadyScrapped': True
            }
        )
        if isAlreadyScrappedWebDocs is not None:
            await prisma.websitedocument.update(
                where={
                    'routinId': orgWebScrapperLink.routinId,
                    'originUrl': orgWebScrapperLink.originUrl,
                    'nowUrl': orgWebScrapperLink.nowUrl,
                    'parentUrl': orgWebScrapperLink.parentUrl 
                },
                data={
                    'isAlreadyScrapped': True
                }
            )
        await prisma.disconnect()
        
        # parentUrl은 다른데 nowUrl이 같은 경우,
        # isAlreadyScrapped 값을 1로 올리고 탐색 대상에서 제외하는 것이 합당해 보인다...
        
        routinId = orgWebScrapperLink.routinId
        originUrl = orgWebScrapperLink.originUrl
        parentUrl = orgWebScrapperLink.parentUrl
        nowUrl = orgWebScrapperLink.nowUrl
        nowDepth = orgWebScrapperLink.nowDepth
        maxDepth = orgWebScrapperLink.maxDepth
        originDomain = orgWebScrapperLink.originDomain
        domainOption = orgWebScrapperLink.domainOption
        
        driver.get(nowUrl)
        driver.implicitly_wait(3)
        
        originHtml = driver.page_source
                
        titles, internalLinks, externalLinks = self.webScrapperRegexpParser.convertUsableMetaData(originHtml=originHtml)
        filteredHtml = self.webScrapperRegexpParser.convertUsableHtmlFormat(originHtml=originHtml)
        
        orgWebScrapperLink.setScrappedHtml(scrappedHtml=filteredHtml)
        # print('[🤔🤔]', orgWebScrapperLink.convertDict())
        print('[🤔🤔]', orgWebScrapperLink.routinId, orgWebScrapperLink.parentUrl, orgWebScrapperLink.nowUrl, orgWebScrapperLink.nowDepth)
        
        # [RECORD] 현재 페이지 탐색 결과 저장
        prisma = self.databaseProvider.getPrisma()
        await prisma.connect()
        async with prisma.tx() as txPrisma:
            await prisma.websitedocument.upsert(
                where={
                    'routinId_originUrl_parentUrl_nowUrl':  {
                        'routinId': orgWebScrapperLink.routinId,
                        'originUrl': orgWebScrapperLink.originUrl,
                        'parentUrl': orgWebScrapperLink.parentUrl,
                        'nowUrl': orgWebScrapperLink.nowUrl,
                    }
                },
                data={
                    'create': orgWebScrapperLink.convertDict(),
                    'update': {                        
                        'nowDepth': orgWebScrapperLink.nowDepth,
                        'maxDepth': orgWebScrapperLink.maxDepth,
                        
                        'originDomain': orgWebScrapperLink.originDomain,
                        
                        'domainType': orgWebScrapperLink.domainType.value,
                        'domainOption': orgWebScrapperLink.domainOption,
                        
                        'isScrapped': orgWebScrapperLink.isScrapped,
                        'scrappedHtml': orgWebScrapperLink.scrappedHtml
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
            # print('[CHLID]', len(webScrapperLinks))
            for wLink in webScrapperLinks:
                # print('[❌❌]', wLink.convertDict())
                print('[❌❌]', wLink.routinId, wLink.parentUrl, wLink.nowUrl, wLink.nowDepth)
                await txPrisma.websitedocument.upsert(
                    where={
                        'routinId_originUrl_parentUrl_nowUrl':  {
                            'routinId': routinId,
                            'originUrl': wLink.originUrl,
                            'parentUrl': wLink.parentUrl,
                            'nowUrl': wLink.nowUrl,
                        }
                    },
                    data={
                        'create': wLink.convertDict(),
                        'update': {
                            'nowDepth': wLink.nowDepth,
                            'maxDepth': wLink.maxDepth,
                            
                            'originDomain': wLink.originDomain,
                            
                            'domainType': wLink.domainType.value,
                            'domainOption': wLink.domainOption,
                            
                            # 중복 탐색에 걸릴 경우 어떻게 할 건지 모르곘음...
                            # 'isScrapped': False,
                            # 'scrappedHtml': None
                        },
                    }
                )
        await prisma.disconnect()
        
        
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
            