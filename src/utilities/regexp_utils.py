import re
from typing import List

# Enums
from enums.e_html_tag_sub_regexp import EHTML_TAG_SUB_REGEXP
from enums.e_html_tag_extract_regexp import EHTML_TAG_EXTRACT_REGEXP

def extract(HTML_TAG_EXTRACT_REGEXP: EHTML_TAG_EXTRACT_REGEXP,
             INPUT: str,
             FLAGS: int = re.MULTILINE) -> List[str]:
    
    return re.findall(pattern=HTML_TAG_EXTRACT_REGEXP.value,
                flags=FLAGS,
                string=INPUT)

def substitute(HTML_TAG_SUB_REGEXP: EHTML_TAG_SUB_REGEXP,
               INPUT: str,
               REPL = '',
               FLAGS = re.MULTILINE) -> str:
    
    return re.sub(pattern=HTML_TAG_SUB_REGEXP.value,
                             repl=REPL,
                             string=INPUT,
                             flags=FLAGS)