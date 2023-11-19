from typing import Literal, Optional

# common
from common.enums.core.e_domain_type import EDOMAIN_TYPE

class ATagDto:
    """prisma.websitelink 기록용 dto

    Returns:
        linkType: EDOMAIN_TYPE.*.value
        linkValue: str
    """
    
    linkValue: str
    linkType: str
    
    def __init__(self,
                 *,
                 href: Optional[str],
                 domainType: EDOMAIN_TYPE) -> None:
        self.linkType = domainType.value
        self.linkValue = href
        
    def __str__(self) -> str:
        
        return f'{self.linkType} {self.linkValue}'
    
    def convertDict(self) -> dict:
        return {
            'linkType': self.linkType,
            'linkValue': self.linkValue
        }