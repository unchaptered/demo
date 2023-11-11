from enum import Enum

class EHTML_TAG_SUB_REGEXP(Enum):
    
    VALID_META_TAG = r'<meta\s+.*?/>'
    INVALID_META_TAG = r'<meta\s+.*?>'
    
    VALID_LINK_TAG = r'<link\s+.*?/>'
    INVALID_LINK_TAG = r'<link\s+.*?>'
    
    VALID_COMMENT_TAG = r'(<!--)\s+.*?(-->)'
    INVALID_COMMENT_TAG = r'(<!--)(-->)'
    
    VALID_SCRIPT_TAG = r'<script\s+.*?</script>'
    VALID_SCRIPT_TAG_WITH_MULTILINE = r'<script[\s|\.]*?>[\w|\s|\.|=|\[|\]|\;|\(|\)|\{|\}|\'|\"|\,|\-|\#]*<\/script>'
    
    VALID_STYLE_TAG = r'<style\s+.*?</style>'
    VALID_STYLE_TAG_WITH_MULTILIUNE = r'<style[\/|\w|\s|\.|=|\[|\]|\;|\(|\)|\{|\}|\'|\"|\,|\-|\#|\:|\@|\>]*<\/[\s]?style>'
    
    UNNECESSARY_ENTER = r'\n'
    UNNECESSARY_KEYWORDS = r'\r'