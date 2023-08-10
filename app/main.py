from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import v1_router
from app.config import logger
from app.database import MongoManager
# from app.database.rabbit_mq import RabbitManager
from app.middlewares.auth_middleware import ApiKeyMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000', 'https://brandboost-demo.web.app',
                   'https://auth-and-login-app.herokuapp.com', 'http://93.125.18.46'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ApiKeyMiddleware)


@app.on_event("startup")
async def on_startup():
    await MongoManager.connect()
    # await RabbitManager.connect()
    # await RedisManager.connect()
    logger.info('Startup event - connecting to the database')


app.include_router(v1_router)
