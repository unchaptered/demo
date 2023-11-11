# pip install selenium
# selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

# webdriver
from webdriver_manager.chrome import ChromeDriverManager

# contextmanager
from typing import Generator
from contextlib import contextmanager

class ChromeCore():    
    
    __chromeOption: Options
    __chromeService: ChromeService
    chromeDriver: WebDriver
    
    def __init__(self) -> None:
        self.__chromeOption = Options()
        self.__chromeOption.add_argument('--incognito')
        # chrome_options.add_argument('--headless')  # 브라우저 창을 띄우지 않고 실행 (백그라운드 실행)

        chromeDriverPath = ChromeDriverManager().install()
        
        self.__chromeService = ChromeService(executable_path=chromeDriverPath)
    
    @contextmanager
    def executeChromeDriver(self) -> Generator[WebDriver, None, None]:
        self.chromeDriver = webdriver.Chrome(service=self.__chromeService,
                                options=self.__chromeOption)
        try:
            
            yield self.chromeDriver
        finally:
            if (
                self.chromeDriver is not None
                and isinstance(self.chromeDriver, WebDriver)
            ):
                self.chromeDriver.quit()
                
# with ChromeCore().executeChromeDriver() as driver:
#     print(driver)