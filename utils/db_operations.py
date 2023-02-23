from db_utils.redis import AsyncRedis
import config
import random
from datetime import datetime
from dateutil.tz import gettz

redis_client=AsyncRedis()

async def getSessionCredentials():
    return random.choice(config.CREDENTIAL_CONFIG_LIST)

async def insertSessionCache(sessionId):
    # for sessionId in sessionIds:
    key = 'session_'+sessionId
    value = {
        'count':0,
        'createdAt':datetime.now(tz=gettz('Asia/Kolkata')).isoformat(),
        'inUse':False
    }
    await redis_client.put(key=config.SESSION_LIST_KEY,value=sessionId)
    await redis_client.setValue(key=key,value=value,value_type='json')

async def resetCache():
    await redis_client.deleteKeys(prefix='session_')
    await redis_client.deleteKey(key=config.SESSION_LIST_KEY)
    await redis_client.deleteKey(key=config.CREDENTIALS_CONFIG_KEY)

async def getSession():
    sessionId = await redis_client.getQueue(key=config.SESSION_LIST_KEY,batch=1)
    if len(sessionId):
        sessionId=sessionId[0]
    else:
        raise Exception("No session left")
    data = await getSessionMetadata(sessionId)
    return sessionId, data

async def getSessionMetadata(sessionId):
    data = await redis_client.getValue(key='session_'+sessionId,value_type='json')
    return data

async def updateSessionMetadata(sessionId,value,updateMetdataOnly=False):
    await redis_client.setValue(key='session_'+sessionId,value=value,value_type='json')
    if not updateMetdataOnly:
        await redis_client.put(key=config.SESSION_LIST_KEY,value=sessionId)
    

async def removeSessionMetadata(sessionId):
    await redis_client.removeListMember(config.SESSION_LIST_KEY,sessionId)
    await redis_client.deleteKey(key='session_'+sessionId)

async def getSessionList():
    data = await redis_client.getListValues(key=config.SESSION_LIST_KEY)
    return data


