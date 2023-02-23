import re
from aredis import StrictRedis, pipeline
import config
import json

class AsyncRedis:
    def __init__(self):
        self.getConnection()

    def getConnection(self):
        self.client=StrictRedis().from_url(config.REDIS_BROKER_URL,decode_responses=True)

    async def checkExists(self,key):
        return await self.client.exists(key)

    async def setValue(self,key,value,value_type=None):
        if value_type=='json':
            value=json.dumps(value)
        return await self.client.set(key,value)

    async def getValue(self,key,value_type=None):
        value= await self.client.get(key)
        if value is None:
            return {}
        if value_type=='json':
            value=json.loads(value)
        return value
    
    async def getListValues(self,key):
        values = await self.client.lrange(key,0,-1)
        return values

    async def deleteKey(self,key):
        return await self.client.delete(key) 

    async def deleteKeys(self,prefix):
        prefix=prefix+"*"
        keys=await self.client.keys(prefix)
        async with await self.client.pipeline() as pipe:
            for key in keys:
                await pipe.delete(key)
            await pipe.execute()

    async def getQueue(self,key,batch):
        async with await self.client.pipeline(transaction=True) as pipe:
            await pipe.lrange(key, 0, batch - 1)
            await pipe.ltrim(key, batch, -1)
            datas, _ = await pipe.execute()

        return datas

    async def getRoundRobinQueue(self,key):
        data = await self.client.rpoplpush(key,key)

        return data

    async def put(self,key,value,value_type=None,mode="right"):
        if value_type=='json':
            value=json.dumps(value)

        if mode=="right":
            await self.client.rpush(key,value)
        else:
            await self.client.lpush(key,value)
            
    async def isMember(self,set_key,member):
        return await self.client.sismember(set_key,member)

    async def addMember(self,set_key,member):
        return await self.client.sadd(set_key,member)

    async def removeMember(self,set_key,member):
        return await self.client.srem(set_key,member)
    
    async def removeListMember(self,key,member):
        await self.client.lrem(key,1,member)