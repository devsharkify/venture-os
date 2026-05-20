from motor.motor_asyncio import AsyncIOMotorClient
from imagekitio import ImageKit
from pathlib import Path
from dotenv import load_dotenv
import os
import logging

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# API Keys
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')
AUTHKEY_API_KEY = os.environ.get('AUTHKEY_API_KEY', '')

# ImageKit
imagekit = ImageKit(private_key=os.environ.get('IMAGEKIT_PRIVATE_KEY', ''))
IMAGEKIT_PUBLIC_KEY = os.environ.get('IMAGEKIT_PUBLIC_KEY', '')

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Categories \u2014 Startup & Funding focused
CATEGORIES = {
    "funding": {"en": "Funding"},
    "startup": {"en": "Startups"},
    "startups": {"en": "Startups"},
    "vc": {"en": "Venture Capital"},
    "ipo": {"en": "IPO & Markets"},
    "tech": {"en": "Tech"},
    "fintech": {"en": "Fintech"},
    "saas": {"en": "SaaS"},
    "deeptech": {"en": "Deep Tech"},
    "d2c": {"en": "D2C"},
    "climate": {"en": "Climate"},
    "policy": {"en": "Policy"},
    "business": {"en": "Business"},
}
