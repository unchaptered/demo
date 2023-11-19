from typing import Literal, Optional

class VidTagDto:
    
    def __init__(self,
                 *,
                 name: Literal['video', 'lite-iframe'],
                 src: str) -> None:
        
        self.videoType = name
        self.videoSrc = src
        
    def __str__(self) -> str:
        return f'{self.tagName} {self.videoSrc}'
    
    def convertDict(self) -> dict:
        return {
            'videoType': self.videoType,
            'videoSrc': self.videoSrc,
        }