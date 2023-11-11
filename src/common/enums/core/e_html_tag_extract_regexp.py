from enum import Enum
    
class EHTML_TAG_EXTRACT_REGEXP(Enum):
    VALID_TITLE = r'<title>.*?</title>'
    
    VALID_INTERNAL_LINK = r'<a href="/+.*?>'
    VALID_INTERNAL_HREF_LINK = r'href="\/([^"]*)"'
    """
    <a href="/auth?"> -> auth
    <a href="/auth/sign-up"> -> auth/sign-up
    """
    
    VALID_EXTERNAL_LINK = r'<a href="http://+.*?>'
    VALID_INTERNAL_HTTP_HREF_LINK = r'href="http:\/\/([^"]*)"'
    """
    <a href="http://example.com" target="_blank"> -> example.com
    <a href="http://example.com/auth" target="_blank"> -> example.com/auth
    <a href="http://example.com?auth=" target="_blank"> -> example.com?auth=
    <a href="http://example.com#auth=" target="_blank"> -> example.com#auth=
    """
    VALID_INTERNAL_HTTPS_HREF_LINK = r'href="https:\/\/([^"]*)"'
    """
    <a href="https://example.com" target="_blank"> -> example.com
    <a href="https://example.com/auth" target="_blank"> -> example.com/auth
    <a href="https://example.com?auth=" target="_blank"> -> example.com?auth=
    <a href="https://example.com#auth=" target="_blank"> -> example.com#auth=
    """