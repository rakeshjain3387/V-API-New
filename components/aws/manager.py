import sys
sys.path.append('.')

import aioboto3
from aiobotocore.config import AioConfig
import time
import asyncio
from uuid import uuid4

from config import logger
import config
from alert_manager import slack_notification

boto_config = AioConfig(retries = {'max_attempts':5,'mode':'adaptive'})

async def publishMessage(region_name,message):
    try:
        async with aioboto3.client("sns",aws_access_key_id=config.AWS_PRIMARY_ACCESS_ENV_KEY,
                            aws_secret_access_key=config.AWS_PRIMARY_SECRET_ENV_KEY,
                            region_name=region_name
                            ) as client:
            response=await client.publish(TopicArn=config.SNS_HANDLER_TOPIC,Message=message)
            logger.debug({"task":"publish_message","message":response})
    except Exception as e:
        logger.error({"task":"publish_message","error":str(e),"stacktrace":traceback.format_exc()})
        slack_notification({"task":"publish_message","error":str(e)})