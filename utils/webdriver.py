from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
import requests
import os
import json
from components.selenium.constants import *

async def getDriverOptions():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    return options

async def getRemoteWebDriver(commandExecutor,sessionId=None):
    if sessionId:
        return await attach_to_session(commandExecutor=commandExecutor,sessionId=sessionId)
    else:
        driver = webdriver.Remote(
            command_executor=commandExecutor,
            options=await getDriverOptions()
        )
        return driver

async def attach_to_session(commandExecutor, sessionId):
    original_execute = WebDriver.execute
    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': sessionId}
        else:
            return original_execute(self, command, params)
    # Patch the function before creating the driver object
    WebDriver.execute = new_command_execute
    driver = webdriver.Remote(command_executor=commandExecutor, desired_capabilities={})
    driver.session_id = sessionId
    # Replace the patched function with original function
    WebDriver.execute = original_execute
    return driver

def enterCaptcha(driver:webdriver.Remote):
    img = driver.find_element(By.XPATH,CAPTCHA_BOX_XPATH).screenshot_as_png
    captcha_image_name = '/tmp/captcha_'+driver.session_id+".png"
    with open(captcha_image_name, 'wb') as f:
        f.write(img)
    
    url = 'http://35.207.247.66:7000/captcha_ocr'
    with open(captcha_image_name, 'rb') as image:
        name_img = os.path.basename(captcha_image_name)
        files= {'image': (name_img,image,'multipart/form-data',{'Expires': '0'}) }
        with requests.Session() as s:
            response = s.post(url,files=files)
            res= json.loads(response.text)
            captcha = res['output']['captcha']['prediction']
            driver.find_element(By.XPATH,CAPTCHA_INPUT_XPATH).send_keys(captcha)
    
    os.remove(captcha_image_name)
    