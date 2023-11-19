import numpy as np
from bs4 import Tag
from typing import List, Tuple
from injector import singleton, inject
from prisma.models import WebsiteDocument

# Core Dependencies
from core.web_indexing_core.web_dom_tree import WebDomTree
from core.web_indexing_core.web_indexing_bs4_parser import WebIndexingBs4Parser


# Module Dependencies
from modules.providers.database_provider import DatabaseProvider

@singleton
class WebIndexingCore:
    
    @inject
    def __init__(self,
                 databaseProvider: DatabaseProvider,
                 webIndexingBs4Parser: WebIndexingBs4Parser) -> None:
        self.databaseProvider = databaseProvider
        self.webIndexingBs4Parser = webIndexingBs4Parser
    
    async def __predictIntersectionGroupList__(self,
                            *,
                            targetWebDomTree: np.ndarray,
                            compareWebDomTree: np.ndarray) -> np.ndarray:
        
        # targetDomTree = targetWebDomTree.domTree
        # compareDomTree = compareWebDomTree.domTree
        
        # [STEP 1] 구간별 교집합 찾기
        # intersectionForParentIdx  [ True True True]
        # intersectionForDepth      [ True True False]
        # intersectionForTagType    [ True True False ]
        intersectionForParentIdx = np.intersect1d(ar1=targetWebDomTree[:, 1],
                                                  ar2=compareWebDomTree[:, 1])
        intersectionForDepth = np.intersect1d(ar1=targetWebDomTree[:, 2],
                                              ar2=compareWebDomTree[:, 2])
        intersectionForTagType = np.intersect1d(ar1=targetWebDomTree[:, 3],
                                                ar2=compareWebDomTree[:, 3])
        
        # [STEP 2] 파편화된 교집합 찾기 (True, True, ...)
        # intersectionBoolean [ True False True True]
        # intersection [0 2 3]
        intersectionBoolean = np.isin(targetWebDomTree[:, 1], intersectionForParentIdx) & \
                              np.isin(targetWebDomTree[:, 2], intersectionForDepth) & \
                              np.isin(targetWebDomTree[:, 3], intersectionForTagType)
        intersection = np.where(intersectionBoolean)[0]
        
        # [STEP 3] 파편화된 교집합을 연속성 교집합으로 변경
        # intersection [0 2 3]이라면, 다음과 같습니다.
        # intersectionDiff [2 1]        -> 0은 2와 2차이가 나고, 2는 3과 1차이가 남
        # intersectionBoundary [1]      -> idx 1번부터 새로운 np.ndarray로 자를 것임
        # intersectionGroup [0] [2, 3]  
        intersectionDiff = np.diff(intersection)
        intersectionBoundary = np.where(intersectionDiff != 1)[0] + 1
        
        intersectionGroupList = np.split(intersection, intersectionBoundary)
        
        return intersectionGroupList
    
    async def __predictLayout__(self,
                               *,
                               webDomTreeList: List[WebDomTree]) -> np.ndarray:
        # 각자 배열
        # aArray = np.array([
        #     [1, 2, 3, 4],
        #     [2, 3, 4, 5],
        #     [5, 6, 7, 8],
        #     [9, 10, 11, 12],
        #     [9, 11, 11, 12]
        # ])
        # bArray = np.array([
        #     [1, 2, 3, 4],
        #     [2, 3, 4, 5],
        #     [9, 10, 11, 12]
        # ])
        # aArray = webDomTreeList[0].domTree
        # bArray = webDomTreeList[1].domTree
        # intersectionGroupList = await self.__predictIntersectionGroupList__(webDomTreeA=aArray,
        #                                                 webDomTreeB=bArray)
        # print(max(intersectionGroupList, key=len))
        
        prevTargetDomTree = webDomTreeList[0].domTree
        for idx in range(len(webDomTreeList) - 1):
            compareWebDomTree = webDomTreeList[idx + 1].domTree
            
            intersectionGroupList = await self.__predictIntersectionGroupList__(
                targetWebDomTree=prevTargetDomTree,
                compareWebDomTree=compareWebDomTree
            )
            prevTargetDomTree = prevTargetDomTree[max(intersectionGroupList, key=len)]
            
            # [SAMPLE CODE]
            # 전체 HTML Tags들을 꺼내는 코드얌
            # 주석 풀고 실행해보렴
            for domTag in webDomTreeList[idx].domTagForTree:
                if domTag and domTag.name and domTag.string:
                    print(domTag.name, domTag.string)
                    
            # print(webDomTreeList[idx].websiteDocument.nowUrl)
            break
            
        return prevTargetDomTree
        
    async def recursiveIndexing(self,
                                *,
                                websiteDocument: WebsiteDocument,
                                layoutDomTree: np.ndarray = None):
        
        # [STEP 1] 재귀호출 중단점 설정
        print('=' * 200)
        print('작업 대상 : ', websiteDocument.routinId, websiteDocument.originUrl, websiteDocument.parentUrl, websiteDocument.nowUrl, websiteDocument.nowDepth, websiteDocument.maxDepth)
        print('=' * 200)
        print('[STEP 1] 재귀호출 중단점 설정')
        if (websiteDocument.nowDepth > websiteDocument.maxDepth):
            print('[STEP 1] 재귀호출 중단점 설정 중단')
            return
        
        print('[STEP 1] 재귀호출 중단점 설정 통과')
        
        # [STEP 2] 중복 Indexing 작업 중단점 설정
        print('[STEP 2] 중복 Indexing 작업 중단점 설정')
        prisma = self.databaseProvider.getPrisma()
        await prisma.connect()
        isAlreadyIndexedWebDocs = await prisma.websitedocument.find_first(
            where={
                'routinId': websiteDocument.routinId,
                'originUrl': websiteDocument.originUrl,
                'nowUrl': websiteDocument.nowUrl,
                # 'parentUrl': {
                #     'not': websiteDocument.parentUrl
                # },
                'OR': [
                    { 'isIndexed': True },
                    { 'isAlreadyIndexed': True },
                ],
            }
        )
        if isAlreadyIndexedWebDocs is not None:
            await prisma.websitedocument.update(
                where={
                    'routinId_originUrl_parentUrl_nowUrl':  {
                        'routinId': websiteDocument.routinId,
                        'originUrl': websiteDocument.originUrl,
                        'parentUrl': websiteDocument.parentUrl,
                        'nowUrl': websiteDocument.nowUrl,
                    }
                },
                data={
                    'isAlreadyScrapped': True
                }
            )
        await prisma.disconnect()
        print(f'[STEP 2] 중복 Indexing 작업 중단점 결과 (isAlreadyIndexedWebDocs : {type(isAlreadyIndexedWebDocs)})')
        
        # [STEP 3] Indexing 작업 처리
        if (
            isAlreadyIndexedWebDocs is None
            and not websiteDocument.isIndexed
            and not websiteDocument.isAlreadyIndexed
        ):
            print('Indexing 작업 처리')
            
            # [STEP 3-1] WebDomTree로 변환
            html = self.webIndexingBs4Parser.getBeautifulSoup(websiteDocument.scrappedHtml)
            
            bodyTag = html.body            
            self.webIndexingBs4Parser.delStyleTag(bsTag=bodyTag)
            self.webIndexingBs4Parser.delScriptTag(bsTag=bodyTag)
            self.webIndexingBs4Parser.delCommentTag(bsTag=bodyTag)
            
            webDomTree = WebDomTree(websiteDocument=websiteDocument)
            webDomTree.recursiveAddTree(domTag=bodyTag)

            # [STEP 3-2] a, img, vid 태그 추출   
            aTagDtoList = webDomTree.findATags()
            
            imgTagDtoList = webDomTree.findImgTags()
            
            vidTagDtoList = webDomTree.findVidTags(name='video')
            vidTagDtoList.extend(webDomTree.findVidTags(name='lite-iframe'))
            
            # [STEP 3] a, img, vid 태그 기록
            prsima = self.databaseProvider.getPrisma()
            await prsima.connect()
            async with prsima.tx() as txPrisma:
                print('AA')
                await txPrisma.websitedocument.update(
                    data={
                        'isIndexed': True
                    },
                    where={
                        'routinId_originUrl_parentUrl_nowUrl':  {
                            'routinId': websiteDocument.routinId,
                            'originUrl': websiteDocument.originUrl,
                            'parentUrl': websiteDocument.parentUrl,
                            'nowUrl': websiteDocument.nowUrl,
                        }
                    },
                )
                
                print('BB')
                websiteIndexingDocument = await txPrisma.websiteindexingdocument.find_first(
                    where={
                        'routinId': websiteDocument.routinId,
                        
                        'originUrl':websiteDocument.originUrl,
                        'parentUrl': websiteDocument.parentUrl,
                        'nowUrl': websiteDocument.nowUrl,
                    }
                )
                print('CC')
                if websiteIndexingDocument is None:
                    websiteIndexingDocument = await txPrisma.websiteindexingdocument.create(
                        data={
                            'routinId': websiteDocument.routinId,
                            
                            'originUrl':websiteDocument.originUrl,
                            'parentUrl': websiteDocument.parentUrl,
                            'nowUrl': websiteDocument.nowUrl
                        }
                    )
                    
                print('DD')
                for aTagDto in aTagDtoList:
                    await txPrisma.websitelink.create(
                        data={
                            'indexId': websiteIndexingDocument.id,
                            
                            'linkType': str(aTagDto.linkType),
                            'linkValue': aTagDto.linkValue   
                            # 'indexId_linkType_linkValue': {
                            #     'indexId': websiteIndexingDocument.id,
                                
                            #     'linkType': str(aTagDto.linkType),
                            #     'linkValue': aTagDto.linkValue   
                            # }
                        }
                    )
                    
                print('EE')
                for imgTagDto in imgTagDtoList:
                    await txPrisma.websiteimage.create(
                        data={
                            'indexId': websiteIndexingDocument.id,
                            
                            'imageSrc': imgTagDto.imageSrc,
                            'imageType': imgTagDto.imageType,
                            
                            'linkType': str(imgTagDto.linkType),
                            'linkValue': imgTagDto.linkValue
                        }
                    )
                    
                print('FF')
                for vidTagDto in vidTagDtoList:
                    await txPrisma.websitevideo.create(
                        data={
                            'indexId': websiteIndexingDocument.id,
                            
                            'videoSrc': vidTagDto.videoSrc,
                            'videoType': vidTagDto.videoType
                        }
                    )
                print('GG')
                    
            await prsima.disconnect()

        # [STEP 4] 다음 Indexing 작업 대상 탐색
        print('[STEP 4] 다음 Indexing 작업 대상 탐색')
        await prisma.connect()
        
        nextWebsiteDocument = await prisma.websitedocument.find_first(
            where={
                'routinId': websiteDocument.routinId,
                
                'originUrl': websiteDocument.originUrl,
                'parentUrl': { 'not': websiteDocument.parentUrl },
                'nowUrl': { 'not': websiteDocument.nowUrl },
                
                'isIndexed': False,
                'isAlreadyIndexed': False,
                
                'isScrapped': True,
                'isAlreadyScrapped': False,
                'scrappedHtml': { 'not': None }
            },
            order=[ { 'nowDepth': 'asc' } ]
        )
    
        print(f'[STEP 4] 다음 Indexing 작업 대상 탐색 결과 (nextWebsiteDocument : {type(nextWebsiteDocument)})')
        if nextWebsiteDocument is None:
            print('[STEP 4] 다음 Indexing 작업 대상 없음')
            return
        await prisma.disconnect()
        
        
        # [STEP 5] 추가 중단점 설정 (재귀 호출 전)
        if nextWebsiteDocument.nowDepth > nextWebsiteDocument.maxDepth:
            return
        
        return await self.recursiveIndexing(websiteDocument=nextWebsiteDocument)
        
    async def recursiveIndexingWrapper(self,
                                *,
                                originUrl: str,
                                originDomain: str):
        
        prisma = self.databaseProvider.getPrisma()
        
        await prisma.connect()
        async with prisma.tx() as txPrisma:
            # [STEP 1] 탐색 대상 존재 있나요?
            latestWebSite = await txPrisma.websitedocument.find_first(
                where={
                    'originUrl': originUrl,
                    'parentUrl': 'null22',
                    'nowUrl': originUrl,
                    
                    'nowDepth': 1,
                    
                    'originDomain': originDomain,
                    'isScrapped': True,
                    'scrappedHtml': {
                        'not': None
                    }
                    # 'AND': [
                    #     { 'isIndexed': False },
                    #     { 'isAlreadyIndexed': False }
                    # ]
                },
                order=[
                    { 'routinId': 'desc' }
                ]
            )
            if latestWebSite is None:
                raise Exception([
                    '해당 URL은 탐색되지 않았습니다.',
                    originUrl
                ])
            
            # [STEP 2] 탐색 대상의 레이아웃 탐색 (이 대상은 제외할듯...?)
            # webDocList = await txPrisma.websitedocument.find_many(
            #     where={
            #         'originUrl': originUrl,
            #         # 'parentUrl': 'null22',
            #         # 'nowUrl': originUrl,
                    
            #         'routinId': latestWebSite.routinId,
            #         'originDomain': originDomain,
            #         'OR': [
            #             { 'isScrapped': True },
            #             { 'isAlreadyScrapped': True }
            #         ],
            #         'nowDepth': { 'gte': 1, 'lte': 2 }
            #     },
            #     order=[
            #         { 'nowDepth': 'asc' },
            #         { 'nowUrl': 'asc' },
            #     ],
            #     take=3
            # )
            
            # webDomTreeList: List[WebDomTree] = []
            # for webDoc in webDocList:
            #     print(webDoc.nowUrl, webDoc.isScrapped, webDoc.isAlreadyScrapped)
            #     if webDoc.scrappedHtml is None:
            #         continue
            #     bsSoup = self.webIndexingBs4Parser.getBeautifulSoup(webDoc.scrappedHtml)
                
            #     bodyTag = bsSoup.body
                
            #     self.webIndexingBs4Parser.delStyleTag(bsTag=bodyTag)
            #     self.webIndexingBs4Parser.delScriptTag(bsTag=bodyTag)
            #     self.webIndexingBs4Parser.delCommentTag(bsTag=bodyTag)
                
            #     webDomTree = WebDomTree(websiteDocument=webDoc)
            #     webDomTree.recursiveAddTree(domTag=bodyTag)
            #     webDomTreeList.append(webDomTree)
                
            #     # fileName = webDoc.nowUrl.replace('//', '') \
            #     #     .replace('/', '') \
            #     #     .replace(':', '') \
            #     #     .replace('.com', '') \
            #     #     .replace('?', '') \
            #     #     .replace('&', '') \
            #     #     .replace(';', '')
            #     # with open(fileName + '.html', 'w', encoding='utf-8') as file:
            #     #     file.write(webDoc.scrappedHtml)
                    
            #     # with open(fileName + '.tags', 'w', encoding='utf-8') as file:
            #     #     file.write(str(webDomTree.domTagNameList))
                
            # layoutDomTree = await self.__predictLayout__(webDomTreeList=webDomTreeList)
            
        await prisma.disconnect()
        await self.recursiveIndexing(websiteDocument=latestWebSite,
                                    layoutDomTree=None)