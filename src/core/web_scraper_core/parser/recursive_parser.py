def findBodyArea(originHtml: str):
    startPoint = originHtml.find('<body>')
    endPoint = originHtml.find('</body>')
    
    print(originHtml[startPoint:endPoint])

def executeRecursiveParser(originHtml: str):
    findBodyArea(originHtml)