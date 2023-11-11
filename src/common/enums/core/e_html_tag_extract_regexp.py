from enum import Enum
    
class EHTML_TAG_EXTRACT_REGEXP(Enum):
    VALID_TITLE = r'<title>.*?</title>'
    
    VALID_INTERNAL_LINK = r'<a href="/+.*?>'
    
    VALID_EXTERNAL_LINK = r'<a href="http://+.*?>'