
# Enums
from common.enums.core.e_html_tag_sub_regexp import EHTML_TAG_SUB_REGEXP
from common.enums.core.e_html_tag_extract_regexp import EHTML_TAG_EXTRACT_REGEXP

# Functions
import utilities.regexp_utils as regexpUtils

def convertUsableHtmlFormat(originHtml: str) -> str:
    
    copiedHtml = originHtml
    # Comment
    copiedHtml = regexpUtils.substitute(EHTML_TAG_SUB_REGEXP.VALID_COMMENT_TAG, copiedHtml)

    # Meta
    copiedHtml = regexpUtils.substitute(EHTML_TAG_SUB_REGEXP.VALID_META_TAG, copiedHtml)
    copiedHtml = regexpUtils.substitute(EHTML_TAG_SUB_REGEXP.INVALID_META_TAG, copiedHtml)

    # Link
    copiedHtml = regexpUtils.substitute(EHTML_TAG_SUB_REGEXP.VALID_LINK_TAG, copiedHtml)
    copiedHtml = regexpUtils.substitute(EHTML_TAG_SUB_REGEXP.INVALID_LINK_TAG, copiedHtml)

    # Script
    copiedHtml = regexpUtils.substitute(EHTML_TAG_SUB_REGEXP.VALID_SCRIPT_TAG, copiedHtml)
    copiedHtml = regexpUtils.substitute(EHTML_TAG_SUB_REGEXP.VALID_SCRIPT_TAG_WITH_MULTILINE, copiedHtml)
    
    copiedHtml = regexpUtils.substitute(EHTML_TAG_SUB_REGEXP.VALID_STYLE_TAG, copiedHtml)
    copiedHtml = regexpUtils.substitute(EHTML_TAG_SUB_REGEXP.VALID_STYLE_TAG_WITH_MULTILIUNE, copiedHtml)

    # Unnecessary Keyword
    copiedHtml = regexpUtils.substitute(EHTML_TAG_SUB_REGEXP.UNNECESSARY_KEYWORDS, copiedHtml)
    copiedHtml = regexpUtils.substitute(EHTML_TAG_SUB_REGEXP.UNNECESSARY_ENTER, copiedHtml,
                            REPL='\n')
    
    copiedHtml = regexpUtils.substitute(EHTML_TAG_SUB_REGEXP.INVALID_COMMENT_TAG, copiedHtml)
    
    return copiedHtml

def convertUsableMetaData(originHtml: str) -> str:
    titles = regexpUtils.extract(EHTML_TAG_EXTRACT_REGEXP.VALID_TITLE, originHtml)
    
    internalLinks = regexpUtils.extract(EHTML_TAG_EXTRACT_REGEXP.VALID_INTERNAL_LINK, originHtml)
    externalLinks = regexpUtils.extract(EHTML_TAG_EXTRACT_REGEXP.VALID_EXTERNAL_LINK, originHtml)
    
    return {
        'titles': titles,
        'internalLinks': internalLinks,
        'externalLinks': externalLinks,
    }
