import sys
sys.path.append('.')

import json
import asyncio
from utils import db_operations
from datetime import datetime
import config
from controller import scrapper_handler
from dateutil.tz import gettz
import time
import requests

async def main():
    '''
        - get active session list
        - check if session is valid
        - if not remove the session and trigger new session
    '''
    while True:
        time.sleep(2)
        sessionIds = await db_operations.getSessionList()
        for sessionId in sessionIds:
            print("Checking Session Validity")
            sessionMetadata = await db_operations.getSessionMetadata(sessionId=sessionId)
            if sessionMetadata:
                createdAt = sessionMetadata['createdAt']
                createdAt = datetime.fromisoformat(createdAt)
                totalSeconds = (datetime.now(tz=gettz('Asia/Kolkata'))-createdAt).total_seconds()
                if totalSeconds>config.SESSION_TIMEOUT_THRESHOLD:
                    print("Session Expired. Creating New session",totalSeconds)
                    # await db_operations.removeSessionMetadata(sessionId)
                    await scrapper_handler.publishCloseSessionMessage(sessionId)

                    await scrapper_handler.publishStartSessionMessage()



if __name__=='__main__':
    asyncio.get_event_loop().run_until_complete(main())