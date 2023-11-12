import asyncio
from injector import singleton
from typing import Generator, AsyncGenerator
# from django.db import transaction
from prisma import Prisma
from contextlib import contextmanager

@singleton
class DatabaseProvider:
    
    prisma: Prisma
    
    def __init__(self) -> None:
        self.prisma = Prisma()
    
    def getPrisma(self):
        return self.prisma
        
        # print('============================' * 50)
        # try:
        #     print('BEF CONNECT')
        #     self.prisma.connect()
        #     print('AFT CONNECT')
            
        #     print('BEF YIELD')
        #     print('AFT YIELD')
        # finally:
        #     print('FINALLY')
        #     self.prisma.disconnect()