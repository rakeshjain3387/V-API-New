import time
import json

from fastapi import FastAPI,Request,Header,Response
# from starlette.middleware import Middleware
# from starlette.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from routers import route
from config import logger
import config

app=FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

app = FastAPI()

limiter = Limiter(key_func=get_remote_address, default_limits=[str(config.TPS)+"/second"], storage_uri=config.REDIS_BROKER_URL)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

@app.on_event("startup")
def startup_event():
    logger.info({"message":"Started Scrapper service"})

@app.on_event("shutdown")
def shutdown_event():
    logger.info({"message":"Shutting down Scrapper Service"})

@app.get("/")
def read_root():
    return {"message":"ok"}


app.include_router(
    route.router,
    prefix="/scrapper"
)

if __name__=='__main__':
    uvicorn.run("main:app",host="0.0.0.0",port=8000,reload=False,workers=1)