from fastapi import APIRouter,BackgroundTasks,UploadFile,File,Form,Body
import time

from controller import scrapper_handler
from config import logger
from typing import Union,Optional
import aiohttp
import json
import traceback
import requests
import config
from models.exceptions import *

router=APIRouter()

@router.post("/startSession")
async def startSession(request_body : dict = Body(...)):
    try:
        count = int(request_body['count'])
        for i in range(count):
            await scrapper_handler.publishStartSessionMessage()
        return {"data":None,"message":"Initiated Session","success":True,"error":None,"response_code":101}
    except HandledExceptions as e:
        logger.error({"message":"Error in startSession","error":str(e),"stacktrace":traceback.format_exc()})
        return {"data":None,"message":None,"success":False,"error":e.error,"response_code":e.response_code}
    except Exception as e:
        logger.error({"message":"Error in startSession","error":str(e),"stacktrace":traceback.format_exc()})
        return {"data":None,"message":None,"success":False,"error":"Internal Server Error","response_code":500}

@router.post("/initialize")
async def initializeService():
    try:
        #await clear_sessions(None)
        await scrapper_handler.initializeService()
        return {"data":None,"message":"Service Initialization Initiated","success":True,"error":None,"response_code":101}
    except HandledExceptions as e:
        logger.error({"message":"Error in initialize","error":str(e),"stacktrace":traceback.format_exc()})
        return {"data":None,"message":None,"success":False,"error":e.error,"response_code":e.response_code}
    except Exception as e:
        logger.error({"message":"Error in initialize","error":str(e),"stacktrace":traceback.format_exc()})
        return {"data":None,"message":None,"success":False,"error":"Internal Server Error","response_code":500}

@router.post("/fetchRcDetails")
async def initializeService(backgroundTasks:BackgroundTasks,request_body : dict = Body(...)):
    try:
        rcNumber=request_body['rcNumber']
        api_key=request_body['api_key']
        if api_key == "4a0bd6b4-b54f-4f1e-b7dd-9e48f3f9dc59":
            data = await scrapper_handler.scrapeRcDetails(rcNumber,backgroundTasks)
            if "rc_number" in data:
                return {"data":data,"message":"Fetched RC Details","success":True,"error":None,"response_code":101}
            else:
                return {"data":data,"message":"Fetched RC Details","failure":True,"error":None,"response_code":110}
        else:
            return {"data":None,"message":"Check API Key","failure":True,"error":None,"response_code":110}
    except HandledExceptions as e:
        logger.error({"message":"Error in fetchRcDetails","error":str(e),"stacktrace":traceback.format_exc()})
        return {"data":None,"message":None,"failure":False,"error":e.error,"response_code":e.response_code}
    except Exception as e:
        logger.error({"message":"Error in fetchRcDetails","error":str(e),"stacktrace":traceback.format_exc()})
        return {"data":None,"message":None,"failure":False,"error":"Internal Server Error","response_code":500}

@router.post("/clearSession")
async def clear_sessions(session_id=None):
    """
    Here we query and delete orphan sessions
    docs: https://www.selenium.dev/documentation/grid/advanced_features/endpoints/
    :return: None
    """
    url = config.SELENIUM_HUB_URL
    if not session_id:
        # delete all sessions
        r = requests.get("{}/status".format(url))
        data = json.loads(r.text)
        for node in data['value']['nodes']:
            for slot in node['slots']:
                if slot['session']:
                    id = slot['session']['sessionId']
                    r = requests.delete("{}/session/{}".format(url, id))
    else:
        # delete session from params
        r = requests.delete("{}/session/{}".format(url, session_id))
