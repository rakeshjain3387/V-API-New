import config
from utils import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from .constants import *
from utils import db_operations,webdriver
from config import logger

async def verifyCaptcha(driver):
    count=0
    while True:
        driver.find_element(By.XPATH,EMPTY_XPATH).click()
        time.sleep(0.5)
        text=driver.find_element(By.XPATH,CAPTCHA_IMG_XPATH).get_property('value').strip()
        logger.debug({"message":"Verifying Captcha","verify_count":count})
        if text=='':
            logger.debug({"message":"Resetting Captcha","verify_count":count})
            await resetPage(driver=driver)
            count=count+1
            if count>6:
                raise Exception("Cannot solve captcha")
        else:
            break

async def initiateSession(username,password):
    driver = await webdriver.getRemoteWebDriver(
        commandExecutor=config.SELENIUM_HUB_URL
    )
    logger.debug({"message":"Remote driver attached","session_id":driver.session_id})

    start = time.time()
    driver.get(config.LOGIN_URL)
    logger.debug({"message":"Fetched login URL","time":time.time()-start})

    driver.find_element(By.XPATH,MOBILE_NO_XPATH).send_keys(username)
    logger.debug({"message":"Sent Username"})
    time.sleep(0.05)

    driver.find_element(By.XPATH,LOGIN_BUTTON_XPATH).click()
    logger.debug({"message":"Clicked Login Button"})
    time.sleep(0.05)

    driver.find_element(By.XPATH,PASSWORD_XPATH).send_keys(password)
    logger.debug({"message":"Sent Password"})
    time.sleep(0.05)

    driver.find_element(By.XPATH,LOGIN_BUTTON_XPATH).click()
    logger.debug({"message":"Clicked Login Button"})

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, RC_STATUS_LOGIN_XPATH)))

    webdriver.enterCaptcha(driver=driver)
    logger.debug({"message":"Captcha Entered"})

    await verifyCaptcha(driver)
    logger.debug({"message":"Captcha Verified"})

    await db_operations.insertSessionCache(sessionId=driver.session_id)
    logger.debug({"message":"Session Created"})

    return driver.session_id

async def execute(rcNumber,sessionId): 
    logger.debug({"message":"Executing Session"})

    driver =await webdriver.attach_to_session(commandExecutor=config.SELENIUM_HUB_URL,sessionId=sessionId)
    logger.debug({"message":"Session Attached"})

    driver.find_element(By.XPATH,REGISTRATION_NO_TEXTBOX_XPATH).send_keys(rcNumber)
    logger.debug({"message":"Sent Rc Number"})
    time.sleep(0.05)

    driver.find_element(By.XPATH,VAHAN_SEARCH_BUTTON_XPATH).click()
    logger.debug({"message":"Clicked Vahan Search"})

    start=time.time()
    WebDriverWait(driver, config.VAHAN_DETAILS_WAIT_TIME).until(EC.visibility_of_element_located((By.XPATH, RC_STATUS_SEARCH_PAGE_XPATH)))
    logger.debug({"message":"Got Vahan Page","time":time.time()-start})


    registration_number=driver.find_element(By.XPATH,REGISTRATION_NO_XPATH).text.strip()
    vehicle_class=driver.find_element(By.XPATH,VEHICLE_CLASS_XPATH).text.strip()
    fuel=driver.find_element(By.XPATH,FUEL_XPATH).text.strip()
    model_name=driver.find_element(By.XPATH,MODEL_XPATH).text.strip()
    make=driver.find_element(By.XPATH,MANUFACTURER_XPATH).text.strip()
    rto_office=driver.find_element(By.XPATH,REGISTERING_AUTHORITY_XPATH).text.strip()
    rc_status=driver.find_element(By.XPATH,RC_STATUS_XPATH).text.strip()
    owner_name=driver.find_element(By.XPATH,OWNER_NAME).text.strip()
    registration_date = driver.find_element(By.XPATH,REGISTRATION_DATE).text.strip() if driver.find_elements(By.XPATH, REGISTRATION_DATE) else "NA"
    fitness_regn = driver.find_element(By.XPATH,FITNESS_REGN).text.strip() if driver.find_elements(By.XPATH, FITNESS_REGN) else "NA"
    pucc = driver.find_element(By.XPATH,PUCC).text.strip() if driver.find_elements(By.XPATH, PUCC) else "NA"
    mv_tax = driver.find_element(By.XPATH,MV_TAX).text.strip() if driver.find_elements(By.XPATH, MV_TAX) else "NA"
    insurance_company = driver.find_element(By.XPATH,INSURANCE_COMPANY).text.strip() if driver.find_elements(By.XPATH, INSURANCE_COMPANY) else "NA"
    insurance_policy = driver.find_element(By.XPATH,INSURANCE_POLICY).text.strip() if driver.find_elements(By.XPATH, INSURANCE_POLICY) else "NA"
    insurance_validity = driver.find_element(By.XPATH,INSURANCE_VALIDITY).text.strip() if driver.find_elements(By.XPATH, INSURANCE_VALIDITY) else "NA"
    permit_no = driver.find_element(By.XPATH,PERMIT_NO).text.strip() if driver.find_elements(By.XPATH, PERMIT_NO) and 'Owner Name' in driver.find_element(By.XPATH,DUPLICATE_DATA_CHECK).text.strip() else "NA"
    permit_valid = driver.find_element(By.XPATH,PERMIT_VALID).text.strip() if driver.find_elements(By.XPATH, PERMIT_VALID) else "NA"
    np_auth_no = driver.find_element(By.XPATH,NP_AUTH_NO).text.strip() if driver.find_elements(By.XPATH, NP_AUTH_NO) else "NA"
    np_auth_up_to = driver.find_element(By.XPATH,NP_AUTH_UP_TO).text.strip() if driver.find_elements(By.XPATH, NP_AUTH_UP_TO) else "NA"
    financed = driver.find_element(By.XPATH,FINANCED).text.strip() if driver.find_elements(By.XPATH, FINANCED) else "NA"

    data = {
        'rc_number':registration_number,
        'vehicle_category':vehicle_class.split("(")[-1].split(")")[0] if "(" in vehicle_class else vehicle_class,
        'vehicle_category_description':vehicle_class,
        'fuel_type':fuel,
        'maker_model':model_name,
        'maker_description':make,
        'registered_at':rto_office,
        'rc_status':rc_status,
        'owner_name':owner_name,
        'registration_date':registration_date,
        'fit_up_to':fitness_regn,
        'pucc_upto':pucc,
        'tax_upto':mv_tax,
        'tax_paid_upto':mv_tax,
        'insurance_company':insurance_company,
        'insurance_policy_number':insurance_policy,
        'insurance_upto':insurance_validity,
        'permit_number':permit_no,
        'permit_valid_upto':permit_valid,
        'national_permit_number':np_auth_no,
        'national_permit_upto':np_auth_up_to,
        'financed':financed,
        'norms_type':"",
        'blacklist_status':"",
    }
    return data

async def resetPage(sessionId=None,driver=None):
    if driver:
        pass
    elif sessionId:
        driver =await webdriver.attach_to_session(commandExecutor=config.SELENIUM_HUB_URL,sessionId=sessionId)
        logger.debug({"message":"Session Attached"})
    
    driver.get(SEARCH_PAGE_URL)
    logger.debug({"message":"Page Refreshed"})

    webdriver.enterCaptcha(driver=driver)
    logger.debug({"message":"Captcha Entered"})

    await verifyCaptcha(driver=driver)
    logger.debug({"message":"Captcha Verified"})

async def closeSession(sessionId):
    driver =await webdriver.attach_to_session(commandExecutor=config.SELENIUM_HUB_URL,sessionId=sessionId)
    driver.quit()
    logger.debug({"message":"Session Closed"})
