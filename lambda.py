import json
import asyncio

from config import logger
# from alert_manager import slack_notification
from controller import scrapper_handler
from components.selenium import selenium_handler
import time
import traceback

async def handler(operation,data):
    if operation=='CREATE_SESSION':
        try:
            cred=None
            if data:
                username = data['username']
                password = data['password']
                cred={
                    'username':username,
                    'password':password
                }
            await scrapper_handler.startSession(cred=cred)
        except Exception as e:
            logger.error({"message":"Error in creating session, retrying...","error":str(e),"stacktrace":traceback.format_exc()})
            await scrapper_handler.publishStartSessionMessage(data)
    elif operation=='EXECUTE_SESSION':
        registration_number =  data['registration_number']
        data = await scrapper_handler.fetchRcDetails(rcNumber=registration_number)
        return data
    elif operation=='RESET_PAGE':
        sessionId =  data['sessionId']
        sessionMetadata = data['sessionMetadata']
        await scrapper_handler.handlePage(sessionId,sessionMetadata)
    elif operation=='CLOSE_SESSION':
        sessionId =  data['sessionId']
        await scrapper_handler.verifyCloseSession(sessionId)
        

def main(event, context):
    start = time.time()
    finalResponse={
        "statusCode":200,
        "body":""
    }
    response = {
        "data":None,
        "success":False,
        "error":None
    }
    if 'Records' in event:
        request_json = json.loads(event['Records'][0]['Sns']['Message'])        
    elif 'body' in event:
        request_json = json.loads(event['body'])
    else:
        response['error']='Invalid Method Call'
        finalResponse['statusCode']=500
        finalResponse['body']=response
        request_json=None

    if request_json:
        operation = request_json['operation']
        data = request_json.get('data',None)
        
        try:
            data = asyncio.get_event_loop().run_until_complete(handler(operation,data))
            response['data']=data
            response['success']=True
        except Exception as e:
            logger.error({"Lambda Error":str(e),"stacktrace":traceback.format_exc()})
            response['success']=False
            response['error']=str(e)

    end = time.time()
    logger.debug({"message":"Lambda Time taken","time":end-start,"response":response,"request_json":request_json})

    return {
        "statusCode":200,
        "body":json.dumps(response)
    }