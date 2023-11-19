# Selenium 모듈 설치
# pip install selenium
import asyncio

# Core Dependencies
from core.web_indexing_core.web_indexing_core import WebIndexingCore
from core.web_indexing_core.web_indexing_bs4_parser import WebIndexingBs4Parser

# Module Dependencies
from modules.providers.database_provider import DatabaseProvider

# import core.web_scraper_core.parser.recursive_parser as RecursiveParser
# import core.web_scraper_core.parser.regexp_parser as RegexpParser

webIndexingCore = WebIndexingCore(DatabaseProvider(),
                                  WebIndexingBs4Parser())
asyncio.run(webIndexingCore.recursiveIndexingWrapper(
    originUrl='http://wfwf297.com',
    originDomain='wfwf297.com'
))