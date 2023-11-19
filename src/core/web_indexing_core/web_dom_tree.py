import re
import numpy as np
from bs4 import Tag
from typing import List, Optional, Literal, Union, Tuple
from prisma.models import WebsiteDocument

# models
from common.dtos.core.a_tag_dto import ATagDto
from common.dtos.core.img_tag_dto import ImgTagDto
from common.dtos.core.vid_tag_dto import VidTagDto
from common.enums.core.e_domain_type import EDOMAIN_TYPE


class WebDomTree:
    
    # related to WebScrapperLink
    websiteDocument: WebsiteDocument

    # WebDomTree    
    domIdx: int
    """DomTree 구성을 위해 필요한 값들"""
    domTree: np.ndarray
    """DomTree 구성을 위해 필요한 값들"""
    domTagNameList: List[str]
    """DomTree 구성을 위해 필요한 값들"""
    
    domTagForTree: List[Tag]
    
    def __init__(self,
                 *,
                 websiteDocument: WebsiteDocument) -> None:
        
        self.websiteDocument = websiteDocument
        
        self.domIdx = 0
        self.domTree = np.array([], dtype=np.int32).reshape(0, 4)
        self.domTagNameList = []
        
        self.domTagForTree = []
        
        self.addTree(nowIdx=0,
                     parentIdx=-1,
                     depth=0,
                     tagName='body')

    def addTree(self,
                *,
                nowIdx: int,
                parentIdx: int,
                depth: int,
                tagName: str,
                tagOrigin: Optional[Tag] = None):
        
        isRecoredDomTag = tagName in self.domTagNameList
        if isRecoredDomTag:
            domTagNameIdx = self.domTagNameList.index(tagName)
        else:
            self.domTagNameList.append(tagName)
            domTagNameIdx = len(self.domTagNameList) - 1
                
        newDomTree = np.array(
            [[ nowIdx, parentIdx, depth, domTagNameIdx ]],
            dtype=np.int32
        )
        
        self.domTree = np.vstack(
            [ self.domTree, newDomTree ],
            dtype=np.int32
        )
        self.domTagForTree.append(tagOrigin)
        
        self.increaseDomIdx()
        
    def increaseDomIdx(self):
        self.domIdx += 1
        
    def recursiveAddTree(self,
                      *,
                      domTag: Tag,
                      domDepth: int = 1,
                      parentDomIdx: int = 0):
        
        for domChild in domTag.children:
            if domChild.name:
                self.addTree(nowIdx=self.domIdx,
                            parentIdx=parentDomIdx,
                            depth=domDepth,
                            tagName=domChild.name,
                            tagOrigin=domChild)
                
                self.recursiveAddTree(domTag=domChild,
                                      domDepth=domDepth + 1,
                                      parentDomIdx=self.domIdx -1)
    
    def __convertATagDto__(self,
                           *,
                           aTreePartial: np.ndarray
    ) -> Optional[ATagDto]:
        aTagIndex = aTreePartial[0]
        aTag = self.domTagForTree[aTagIndex]
        aHrefOrg = aTag.get('href')
        if aHrefOrg is None:
            return None
        
        aHref: str = aHrefOrg
        if aHrefOrg.startswith('#'):
            return None
        
        if aHrefOrg.startswith('/'):
            aHref = self.websiteDocument.originUrl + aHrefOrg
        
        search = re.search(
            pattern=rf'({self.websiteDocument.originDomain})',
            string=aHref[7:]
        )
        if search is None:
            domainType = EDOMAIN_TYPE.OTHER_DOMAIN
            # return
        else:
            startIdx, endIdx = search.span()
            if startIdx == 0:
                domainType = EDOMAIN_TYPE.ROOT_DOAMIN
            else:
                domainType = EDOMAIN_TYPE.SUB_DOMAIN
        
        return ATagDto(href=aHref, domainType=domainType)
            
    def __convertImgTagDto__(self,
                            *,
                            imgTreePartial: np.ndarray
    ) -> Optional[ImgTagDto]:
    
        imgTagIndex = imgTreePartial[0]
        imgTag = self.domTagForTree[imgTagIndex]
        imgSrc = imgTag.get('src')
        if imgSrc is None:
            return None
        
        hasATag = 'a' in self.domTagNameList
        if not hasATag:
            return ImgTagDto(type='CONTENT_IMAGE',
                             src=imgSrc,
                             href=None)
        
        A_TAG_CODE = self.domTagNameList.index('a')
        
        isParentATag = False
        
        loopCount = 0
        loopLimitation = 1000
        domTreeIndex = imgTreePartial[1]
        while loopCount < loopLimitation:
            parentTag = self.domTree[domTreeIndex]
            if parentTag[3] == A_TAG_CODE:
                isParentATag = True
                break
            
            domTreeIndex = parentTag[1]
            if domTreeIndex == 0:
                break
            loopCount+=1
        
        if not isParentATag:
            return ImgTagDto(imageType='CONTENT_IMAGE',
                             imageSrc=imgSrc,
                             linkType=None,
                             linkValue=None)
        
        parentATag: Tag = self.domTagForTree[self.domTree[domTreeIndex][0]]
        parentATagHref = parentATag.get('href')
        if parentATagHref.startswith('#'):
            return None
        
        search = re.search(
            pattern=rf'({self.websiteDocument.originDomain})',
            string=parentATagHref[7:]
        )
        if search is None:
            domainType = EDOMAIN_TYPE.OTHER_DOMAIN
            # return
        else:
            startIdx, endIdx = search.span()
            if startIdx == 0:
                domainType = EDOMAIN_TYPE.ROOT_DOAMIN
            else:
                domainType = EDOMAIN_TYPE.SUB_DOMAIN
                
        if parentATagHref.startswith('/'):
            return ImgTagDto(imageType='THUMBNAIL_IMAGE',
                             imageSrc=imgSrc,
                             linkType=domainType,
                             linkValue=self.websiteDocument.originUrl + parentATagHref)
        
        return ImgTagDto(imageType='AD_BANNER_IMAGE',
                        imageSrc=imgSrc,
                        linkType=domainType,
                        linkValue=parentATagHref)

    def findATags(self) -> List[ATagDto]:
        if 'a' not in self.domTagNameList:
            return []
        
        aTagCode = self.domTagNameList.index('a')
        aTagTreeIndex = np.where(self.domTree[:, 3] == aTagCode)    
        
        aTagDtoList: List[ATagDto] = []
        for aTreePartial in self.domTree[aTagTreeIndex]:
            aTagDto = self.__convertATagDto__(aTreePartial=aTreePartial)
            if aTagDto: aTagDtoList.append(aTagDto)
            
        return aTagDtoList
        
    def findImgTags(self) -> List[ImgTagDto]:
        if 'img' not in self.domTagNameList:
            return []
        
        imgTagCode = self.domTagNameList.index('img')
        imgTagTreeIndex = np.where(self.domTree[:, 3] == imgTagCode)
        
        imgTagDtoList: List[ImgTagDto] = []
        for imgTreePartial in self.domTree[imgTagTreeIndex]:
            
            imgTagIndex = imgTreePartial[0]
            imgTag = self.domTagForTree[imgTagIndex]
            imgSrc = imgTag.get('src')
            
            imgTagDto = self.__convertImgTagDto__(imgTreePartial=imgTreePartial)
            if imgTagDto: imgTagDtoList.append(imgTagDto)
        
        return imgTagDtoList
    
    def findVidTags(self, name: Literal['video', 'lite-iframe']) -> List[VidTagDto]:
        if name not in self.domTagNameList:
            return []
        
        vidTagCode = self.domTagNameList.index(name)
        vidTagTreeIndex = np.where(self.domTree[:, 3] == vidTagCode)
        
        vidTagDtoList: List[VidTagDto] = []
        for vidTreePartial in self.domTree[vidTagTreeIndex]:
            
            vidTagIndex = vidTreePartial[0]
            vidTag = self.domTagForTree[vidTagIndex]
            vidSrc = vidTag.get('src')
            if vidSrc is None:
                continue
            
            vidTagDto = VidTagDto(name=name, src=vidSrc)
            vidTagDtoList.append(vidTagDto)
        
        return vidTagDtoList
            
    def save(self, saveName: str = 'kevin'):
        
        with open(saveName + '.tree', 'w', encoding='utf-8') as file:
            
            texts = ''
            for hh in self.domTree:
                texts += str(hh) + '\n'
                
            file.write(texts)
            
        with open(saveName + '.tags', 'w', encoding='utf-8') as file:
            
            texts = ''
            for idx, hh in enumerate(self.domTagNameList):
                texts += f'{idx} : {hh} \n'
                
            file.write(texts)
            
        with open(saveName + '.html', 'w', encoding='utf-8') as file:
                
            file.write(self.websiteDocument.scrappedHtml)
                
if __name__ == '__main__':
    webDomTree = WebDomTree()

    print('DOM : ', webDomTree.domTree)
    webDomTree.addTree(nowIdx=0,
                    parentIdx=-1,
                    depth=0,
                    tagType=1)
    print('DOM : ', webDomTree.domTree)
    webDomTree.addTree(nowIdx=1,
                    parentIdx=0,
                    depth=1,
                    tagType=1)
    print('DOM : ', webDomTree.domTree)
    webDomTree.addTree(nowIdx=2,
                    parentIdx=0,
                    depth=1,
                    tagType=1)
    print('DOM : ', webDomTree.domTree)