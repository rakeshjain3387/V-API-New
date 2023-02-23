import requests
import json

from config import logger
import config

def slack_notification(data):
    '''
        Will send a slack notification For Error and Logs
    '''
    # payload = {'text':  json.dumps(data)}
    # slack_app_url = config.SLACK_APP_URL
    # headers = {'content-type': 'application/json'}
    # response = requests.request('POST',
    #                             slack_app_url,
    #                             json=payload,
    #                             headers=headers)
    # logger.debug(response.text)
    pass