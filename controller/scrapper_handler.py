from utils import db_operations
from components.selenium import selenium_handler
from components.aws import manager as aws_manager
import config
import json
import time
from config import logger
import traceback
import aiohttp
import copy
from dateutil.tz import gettz
from datetime import datetime

# initialize session
async def startSession(cred=None):
    if not cred:
        cred = await db_operations.getSessionCredentials()
    sessionId = await selenium_handler.initiateSession(username=cred['username'],password=cred['password'])
    return sessionId

async def initilalizeSessions():
    for cred in config.CREDENTIAL_CONFIG_LIST:
       await publishStartSessionMessage(cred)

async def initializeService():
    await db_operations.resetCache()
    await initilalizeSessions()

async def handlePage(sessionId,sessionMetadata):
    await selenium_handler.resetPage(sessionId)
    await db_operations.updateSessionMetadata(sessionId,sessionMetadata)

async def verifyCloseSession(sessionId):
    status=True
    while status:
        sessionMetada = await db_operations.getSessionMetadata(sessionId)
        if sessionMetada:
            status = sessionMetada['inUse']
        else:
            return
        
    await db_operations.removeSessionMetadata(sessionId)
    await selenium_handler.closeSession(sessionId)


async def fetchRcDetails(rcNumber):
    start=time.time()

    sessionId, sessionMetadata = await db_operations.getSession()

    sessionMetadata['inUse']=True
    await db_operations.updateSessionMetadata(sessionId,sessionMetadata,updateMetdataOnly=True)

    try:
        data = await selenium_handler.execute(rcNumber,sessionId)
    except Exception as e:
        logger.error({"message":"Error in Executing","error":str(e),"stacktrace":traceback.format_exc()})
        data=None
    end=time.time()
    logger.debug({"message":"Time to fetch data","time":end-start})

    sessionMetadata['inUse']=False
    await db_operations.updateSessionMetadata(sessionId,sessionMetadata,updateMetdataOnly=True)

    return {
        'data':data,
        'sessionMetadata':sessionMetadata,
        'sessionId':sessionId
    }

async def handleSession(data,sessionId,sessionMetadata):
    if data:
        sessionMetadata['count'] = sessionMetadata['count'] +1
        if sessionMetadata['count']<5:
            await publishResetPageMessage(sessionId,sessionMetadata)
        else:
            await publishCloseSessionMessage(sessionId)

            await publishStartSessionMessage()
    else:
        await publishCloseSessionMessage(sessionId)

        await publishStartSessionMessage()


async def scrapeRcDetails(rcNumber,backgroundTasks):
    rcDetails = None
    async with aiohttp.ClientSession() as session:
        data={
            'operation':'EXECUTE_SESSION',
            'data':{
                'registration_number':rcNumber
            }
        }
        async with session.post(config.LAMBDA_HANDLER_URL,json=data) as response:
            if response.status==200:
                data = await response.text()
                data = json.loads(data)
                if data['success']:
                    rcDetails = data['data']['data']
                    sessionMetadata = data['data']['sessionMetadata']
                    sessionId = data['data']['sessionId']

                    backgroundTasks.add_task(handleSession,rcDetails,sessionId,copy.deepcopy(sessionMetadata))
                else:
                    logger.error({"message":"Error in Lambda Response","data":data})
            else:
                logger.error({"message":"Error In lambda call","response":await response.text(),"status_code":response.status})

    return rcDetails

async def publishStartSessionMessage(cred=None):
    message={
        'operation':'CREATE_SESSION',
        'data':None
    }
    if cred:
        message['data']={
            'username':cred['username'],
            'password':cred['password']
        }
    message=json.dumps(message)
    await aws_manager.publishMessage(config.AWS_REGION_NAME,message=message)

async def publishResetPageMessage(sessionId,sessionMetadata):
    message={
        'operation':'RESET_PAGE',
        'data':{
            'sessionId':sessionId,
            'sessionMetadata':sessionMetadata
        }
    }
    message=json.dumps(message)
    start=time.time()
    await aws_manager.publishMessage(config.AWS_REGION_NAME,message=message)
    end=time.time()


async def publishCloseSessionMessage(sessionId):
    message={
        'operation':'CLOSE_SESSION',
        'data':{
            'sessionId':sessionId,
        }
    }
    message=json.dumps(message)
    start=time.time()
    await aws_manager.publishMessage(config.AWS_REGION_NAME,message=message)
    end=time.time()
