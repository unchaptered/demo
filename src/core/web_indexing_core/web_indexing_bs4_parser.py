from bs4 import BeautifulSoup, Tag, Comment

class WebIndexingBs4Parser:

    def getBeautifulSoup(self,
                          htmlStr: str) -> BeautifulSoup:
        return BeautifulSoup(htmlStr, 'html.parser')
    
    
    def delScriptTag(self,
                        bsTag: Tag) -> None:
        scrTags = bsTag.find_all('script')
        for scrTag in scrTags:
            scrTag.decompose()
            
    def delStyleTag(self,
                    bsTag: Tag) -> None:
        styleTags = bsTag.find_all('style')
        for styleTag in styleTags:
            styleTag.decompose()

    def delCommentTag(self,
                      bsTag: Tag) -> None:
        commentTags = bsTag.find_all(text=lambda text: isinstance(text, Comment))
        for commentTag in commentTags:
            commentTag.extract()
            
    # def delAttr(self,
    #             bsTag: Tag) -> None:
    #     for child in bsTag.children:
            
    #         if child.name:
    #             child.attrs = {}
                
    #         for grandchild in child.descendants:
    #             # 속성 삭제
    #             if grandchild.name:
    #                 grandchild.attrs = {}
