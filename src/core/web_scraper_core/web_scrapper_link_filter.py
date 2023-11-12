import re
from injector import singleton
from typing import List, Optional

from common.enums.core.e_html_tag_extract_regexp import EHTML_TAG_EXTRACT_REGEXP
from common.enums.core.e_domain_type import EDOMAIN_TYPE

import core.web_scraper_core.options.depth_option as WebScrapperDepthOption
import core.web_scraper_core.options.domain_option as WebScrapperDomainOption

class WebScrapperLink:
    originUrl: str
    parentUrl: str
    nowUrl: str
    
    nowDepth: int
    maxDepth: WebScrapperDomainOption
    
    originDomain: str
    domainType: EDOMAIN_TYPE
    domainOption: WebScrapperDomainOption
    
    def __init__(self,
                 *,
                 originUrl: str,
                 parentUrl: str,
                 nowUrl: str,
                 nextUrl: str,
                 
                 nowDepth: int,
                 maxDepth: WebScrapperDomainOption,
                
                 originDomain: str, 
                 domainOption: WebScrapperDomainOption) -> None:
        
        self.originUrl = originUrl
        self.parentUrl = parentUrl
        self.nowUrl = nowUrl
        self.nextUrl = nextUrl
        
        self.nowDepth = nowDepth
        self.maxDepth = maxDepth
        
        self.originDomain = originDomain
        self.domainOption = domainOption
        
        self.__evaluateDomainType__()
        
        # self.domainType 
    def __evaluateDomainType__(self) -> None:
        search = re.search(pattern=rf'({self.originDomain})', string=self.nextUrl[7:])
        if search is None:
            self.domainType = EDOMAIN_TYPE.OTHER_DOMAIN
            return
            
        startIdx, endIdx = search.span()
        if startIdx == 0:
            self.domainType = EDOMAIN_TYPE.ROOT_DOAMIN
            return
        
        self.domainType = EDOMAIN_TYPE.SUB_DOMAIN
        
    def isValidTarget(self):
        
        if self.domainOption == WebScrapperDomainOption.CONTAIN_LINKED_DOMAIN:
            return True
        
        if self.domainOption == WebScrapperDomainOption.CONTAIN_SUBDOMAIN:
            if self.domainType in [EDOMAIN_TYPE.SUB_DOMAIN, EDOMAIN_TYPE.ROOT_DOAMIN]:
                return True
            return False
            
        if self.domainOption == WebScrapperDomainOption.ONLY_DOMAIN:
            if self.domainType in [EDOMAIN_TYPE.ROOT_DOAMIN]:
                return True
            return False
        
        return False

@singleton
class WebScrapperLinkFilter:
    
    def __isRootDomain__(self, link: str, originUrl: str) -> bool:
        return True
    
    def __isSubDomain__(self, link: str, originUrl: str) -> bool:
        return True
    
    def __extractPureLink__(self, link: str) -> str:
        """ '/', '#', '?' 등의 식별자 후행 제거"""
        identifierIndexList = []
        # identifierIndexList.append(link.find('/'))
        # identifierIndexList.append(link.find('#'))
        # identifierIndexList.append(link.find('?'))
        identifierIndexList = list(filter(lambda x: x >= 0, identifierIndexList))
        
        if len(identifierIndexList) == 0:
            return link
        
        return link[:min(identifierIndexList)]
    
    def __extractValidLink__(self,
                             link: str,
                             originUrl: str,
                             domainOption: WebScrapperDomainOption) -> Optional[str]:
        
        isValid: bool = False
        if domainOption == WebScrapperDomainOption.ONLY_DOMAIN:
            isValid = self.__isRootDomain__(link, originUrl)
            
        if domainOption == WebScrapperDomainOption.CONTAIN_SUBDOMAIN:
            isValid = self.__isSubDomain__(link, originUrl)
            
        if domainOption == WebScrapperDomainOption.CONTAIN_LINKED_DOMAIN:
            isValid = True
        
        if isValid:
            return link
        
        else:
            return link
    
    
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
                            domainOption: WebScrapperDomainOption) -> str:
        httpLink = re.findall(pattern=EHTML_TAG_EXTRACT_REGEXP.VALID_INTERNAL_HTTP_HREF_LINK.value,
                    string=link)
        httpsLink = re.findall(pattern=EHTML_TAG_EXTRACT_REGEXP.VALID_INTERNAL_HTTPS_HREF_LINK.value,
                    string=link)
        
        httpLink.extend(httpsLink)
        
        if len(httpLink) > 0:
            if httpLink[0] != '':
                pureLink = self.__extractPureLink__(link=httpLink[0])
                validLink = self.__extractValidLink__(link=pureLink,
                                                      originUrl=originUrl,
                                                      domainOption=domainOption)
                
                return validLink
            return None
        return None
    
    def __extractInternalLinks__(self,
                             allLinks: List[str]):
        internalLinks = [self.__extractInternalLink__(aLink) for aLink in allLinks]
        return list(filter(lambda x: x is not None, internalLinks))
    
    def __extractExternalLinks__(self,
                        allLinks: List[str],
                        originUrl: str,
                        domainOption: WebScrapperDomainOption) -> str:
        externalLinks = [self.__extractExternalLink__(aLink, originUrl, domainOption) for aLink in allLinks]
        return list(filter(lambda x: x is not None, externalLinks))
    
    def filter(self,
               *,
               originUrl: str,
               parentUrl: str,
               nowUrl: str,
               
               nowDepth: int,
               maxDepth: WebScrapperDepthOption,
               
               originDomain: str,
               domainOption: WebScrapperDomainOption,
               
               internalLinks: List[str],
               externalLinks: List[str]) -> List[WebScrapperLink]:
        
        allLinks = []
        allLinks.extend(internalLinks)
        allLinks.extend(externalLinks)
        
        extInternalLinks = self.__extractInternalLinks__(allLinks)
        extExternalLinks = self.__extractExternalLinks__(allLinks, originUrl, domainOption)
        
        pureInternalLinks = list(set(extInternalLinks))
        pureExternalLinks = list(set(extExternalLinks))
        
        webScrapperLinks: List[WebScrapperLink] = []
        for link in pureInternalLinks:
            nextUrl=f'{originUrl}/{link}'
            webScrapperLinks.append(WebScrapperLink(originUrl=originUrl,
                                                    parentUrl=parentUrl,
                                                    nowUrl=nowUrl,
                                                    nextUrl=nextUrl,
                                                    
                                                    nowDepth=nowDepth,
                                                    maxDepth=maxDepth,
                                                    
                                                    originDomain=originDomain,
                                                    domainOption=domainOption))
        for link in pureExternalLinks:
            nextUrl = f'http://{link}'
            webScrapperLinks.append(WebScrapperLink(originUrl=originUrl,
                                                    parentUrl=parentUrl,
                                                    nowUrl=nowUrl,
                                                    nextUrl=nextUrl,
                                                    
                                                    nowDepth=nowDepth,
                                                    maxDepth=maxDepth,
                                                    
                                                    originDomain=originDomain,
                                                    domainOption=domainOption))
        webScrapperLinks.append(WebScrapperLink(originUrl=originUrl,
                                    parentUrl=parentUrl,
                                    nowUrl=nowUrl,
                                    nextUrl='http://web.wfwf297.com/hllo',
                                    
                                    nowDepth=nowDepth,
                                    maxDepth=maxDepth,
                                    
                                    originDomain=originDomain,
                                    domainOption=domainOption))
        
        return webScrapperLinks