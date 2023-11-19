from typing import Literal, Optional

# common
from common.enums.core.e_domain_type import EDOMAIN_TYPE

class ImgTagDto:
    """_summary_

    Returns:
        imageType: 
        imageSrc: 
        
        linkType: EDOMAIN_TYPE.*.value
        linkValue: str
    """
    
    imageType: Literal['CONTENT_IMAGE', 'THUMBNAIL_IMAGE', 'AD_BANNER_IMAGE']
    imageSrc: str
    
    linkType: Optional[str]
    linkValue: Optional[str]

    def __init__(self,
                 *,
                 imageType: Literal['CONTENT_IMAGE', 'THUMBNAIL_IMAGE', 'AD_BANNER_IMAGE'],
                 imageSrc: str,
                 
                 linkValue: Optional[str] = None,
                 linkType: Optional[EDOMAIN_TYPE] = None) -> None:
        self.imageType = imageType
        self.imageSrc = imageSrc
        
        self.linkType = linkType.value if linkType else None
        self.linkValue = linkValue
        
    def __str__(self) -> str:
        
        return f'{self.imageType} {self.imageSrc} {self.linkType} {self.linkValue}'
    
    def convertDict(self) -> dict:
        return {
            'imageType': self.imageType,
            'imageSrc': self.imageSrc,
            'linkType': self.linkType,
            'linkValue': self.linkValue,
        }