import logging
import os

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: %(levelname)s: %(message)s')


# FastAPI configuration
HOST = os.environ.get('FASTAPI_HOST', '0.0.0.0')
PORT = os.environ.get('FASTAPI_PORT', '8000')

# MongoManager configuration
MONGO_URI = os.environ['MONGO_URI']
DB_NAME = os.environ['DB_NAME']

SERVICE_URL = os.environ['SERVICE_URL']
PARSER_COLLECTION_NAME = os.environ['PARSER_COLLECTION_NAME']


# Token configuration
SECRET_KEY = os.environ['SECRET_KEY']
JWT_ALGORITHM = os.environ['JWT_ALGORITHM']
JWT_ACCESS_TTL = int(os.environ.get('JWT_ACCESS_TTL', 60))
JWT_REFRESH_TTL = int(os.environ.get('JWT_REFRESH_TTL', 120))
REFRESH_TOKEN_JWT_SUBJECT: str = 'refresh'
ACCESS_TOKEN_JWT_SUBJECT: str = 'access'
TOKEN_TYPE: str = "Bearer"

# Redis configuration
REDIS_HOST: str = os.environ['REDIS_HOST']
REDIS_PORT: str = os.environ['REDIS_PORT']
REDIS_URI: str = f'redis://{REDIS_HOST}:{REDIS_PORT}'
# REDIS_URI = f'0.0.0.0:{REDIS_PORT}'

# Email configuration
EMAIL_HOST_USER: str = os.environ['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD: str = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_HOST: str = os.environ['EMAIL_HOST']

# Fns api
API_FNS_KEY: str = os.environ['API_FNS_KEY']

# Test
USER_EMAIL: str = os.environ.get("USER_EMAIL", 'some_mail@mail.ru')
USER_INN: str = os.environ.get("USER_INN", '123123')

# Rabbit
RABBIT_PORT = os.environ.get("RABBIT_PORT", 5672)
RABBIT_HOST = os.environ.get("RABBIT_HOST", 'localhost')
