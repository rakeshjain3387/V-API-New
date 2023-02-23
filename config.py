import os

from custom_logger import getLogger

from dotenv import load_dotenv
load_dotenv()


logger = getLogger('vahan-scrapper-service')

# Selenium grid
SELENIUM_HUB_URL = os.environ['SELENIUM_HUB_URL']

REDIS_BROKER_URL = os.environ['REDIS_BROKER_URL']

LAMBDA_HANDLER_URL = os.environ['LAMBDA_HANDLER_URL']

# Portal
LOGIN_URL = os.environ['LOGIN_URL']
SESSION_LIST_KEY = 'ACTIVE_SESSION_LIST'
CREDENTIALS_CONFIG_KEY = 'CREDENTIALS_CONFIG'
VAHAN_DETAILS_WAIT_TIME = os.environ['VAHAN_DETAILS_WAIT_TIME']

AWS_PRIMARY_ACCESS_ENV_KEY =  os.environ['AWS_PRIMARY_ACCESS_ENV_KEY']
AWS_PRIMARY_SECRET_ENV_KEY = os.environ['AWS_PRIMARY_SECRET_ENV_KEY']
SNS_HANDLER_TOPIC = os.environ['SNS_HANDLER_TOPIC']
AWS_REGION_NAME = os.environ['AWS_REGION_NAME']

SESSION_TIMEOUT_THRESHOLD = int(os.environ['SESSION_TIMEOUT_THRESHOLD'])

TPS = 500

CREDENTIAL_CONFIG=[
    {
        'username':'7040712154',
        'password':'Manit@2010',
        'config':{
            'max_sessions':5
        }
    }
]

CREDENTIAL_CONFIG_LIST = []
for cred in CREDENTIAL_CONFIG:
    CREDENTIAL_CONFIG_LIST.extend(
        [
            {'username':cred['username'],'password':cred['password']} for i in range(cred['config']['max_sessions'])
        ]
    )

