import re
from injector import singleton
from typing import List

from common.enums.core.e_html_tag_extract_regexp import EHTML_TAG_EXTRACT_REGEXP
import core.web_scraper_core.options.depth_option as WebScrapperDepthOption
import core.web_scraper_core.options.domain_option as WebScrapperDomainOption

@singleton
class WebScrapperLinkFilter:
    
    
    def __isRootDomain__(self, link: str, originUrl: str) -> bool:
        return True
    
    def __isSubDomain__(self, link: str, originUrl: str) -> bool:
        return True
    
    
    def __extractPureLink__(self, link: str) -> str:
        """ '/', '#', '?' 등의 식별자 후행 제거"""
        identifierIndexList = []
        identifierIndexList.append(link[0].find('/'))
        identifierIndexList.append(link[0].find('#'))
        identifierIndexList.append(link[0].find('?'))
        identifierIndexList = list(filter(lambda x: x >= 0, identifierIndexList))
        
        if len(identifierIndexList) == 0:
            return link[0]
        
        return link[0][:min(identifierIndexList)]

    
    def __extractInternalLink__(self,
                            link: str) -> str:
        
        iLink = re.findall(pattern=EHTML_TAG_EXTRACT_REGEXP.VALID_INTERNAL_HREF_LINK.value,
                            string=link)
        
        if len(iLink) > 0:
            if iLink[0] != '':
                return iLink[0]
            return None
        return None
    
    def __extractExternalLink__(self,
                            link: str,
                            originUrl: str,
                            domain: WebScrapperDomainOption) -> str:
        httpLink = re.findall(pattern=EHTML_TAG_EXTRACT_REGEXP.VALID_INTERNAL_HTTP_HREF_LINK.value,
                    string=link)
        httpsLink = re.findall(pattern=EHTML_TAG_EXTRACT_REGEXP.VALID_INTERNAL_HTTPS_HREF_LINK.value,
                    string=link)
        
        httpLink.extend(httpsLink)
        
        if len(httpLink) > 0:
            if httpLink[0] != '':
                identifierIndexList = []
                identifierIndexList.append(httpLink[0].find('/'))
                identifierIndexList.append(httpLink[0].find('#'))
                identifierIndexList.append(httpLink[0].find('?'))
                identifierIndexList = list(filter(lambda x: x >= 0, identifierIndexList))
                
                if len(identifierIndexList) == 0:
                    return httpLink[0]
                
                return httpLink[0][:min(identifierIndexList)]
            return None
        return None
    
    def __extractInternalLinks__(self,
                             allLinks: List[str]):
        internalLinks = [self.__extractInternalLink__(aLink) for aLink in allLinks]
        return list(filter(lambda x: x is not None, internalLinks))
    
    def __extractExternalLinks__(self,
                        allLinks: List[str],
                        originUrl: str,
                        domain: WebScrapperDomainOption) -> str:
        externalLinks = [self.__extractExternalLink__(aLink, originUrl, domain) for aLink in allLinks]
        return list(filter(lambda x: x is not None, externalLinks))
    
    def filter(self,
               *,
               originUrl: str,
               nowDepth: int,
               maxDepth: WebScrapperDepthOption,
               domain: WebScrapperDomainOption,
               internalLinks: List[str],
               externalLinks: List[str]):
        
        if nowDepth >= maxDepth:
            return False, None, None
        
        allLinks = []
        allLinks.extend(internalLinks)
        allLinks.extend(externalLinks)
        
        extractedInternalLinks = self.__extractInternalLinks__(allLinks)
        extractedExternalLinks = self.__extractExternalLinks__(allLinks, originUrl, domain)
        
        print(extractedInternalLinks, extractedExternalLinks)
        targetLinks: List[str] = []
        nonTargetLinks: List[str] = []
        
        return True, targetLinks, nonTargetLinks