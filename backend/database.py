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
    "funding": {"en": "Funding", "te": "\u0C2B\u0C02\u0C21\u0C3F\u0C02\u0C17\u0C4D"},
    "startup": {"en": "Startups", "te": "\u0C38\u0C4D\u0C1F\u0C3E\u0C30\u0C4D\u0C1F\u0C2A\u0C4D\u0C38\u0C4D"},
    "startups": {"en": "Startups", "te": "\u0C38\u0C4D\u0C1F\u0C3E\u0C30\u0C4D\u0C1F\u0C2A\u0C4D\u0C38\u0C4D"},
    "vc": {"en": "Venture Capital", "te": "\u0C35\u0C46\u0C02\u0C1A\u0C30\u0C4D \u0C15\u0C4D\u0C2F\u0C3E\u0C2A\u0C3F\u0C1F\u0C32\u0C4D"},
    "ipo": {"en": "IPO & Markets", "te": "\u0C10\u0C2A\u0C40\u0C13 & \u0C2E\u0C3E\u0C30\u0C4D\u0C15\u0C46\u0C1F\u0C4D\u0C38\u0C4D"},
    "tech": {"en": "Tech", "te": "\u0C1F\u0C46\u0C15\u0C4D"},
    "fintech": {"en": "Fintech", "te": "\u0C2B\u0C3F\u0C28\u0C4D\u200C\u0C1F\u0C46\u0C15\u0C4D"},
    "saas": {"en": "SaaS", "te": "\u0C38\u0C3E\u0C38\u0C4D"},
    "deeptech": {"en": "Deep Tech", "te": "\u0C21\u0C40\u0C2A\u0C4D \u0C1F\u0C46\u0C15\u0C4D"},
    "d2c": {"en": "D2C", "te": "\u0C21\u0C3F2\u0C38\u0C3F"},
    "climate": {"en": "Climate", "te": "\u0C35\u0C3E\u0C24\u0C3E\u0C35\u0C30\u0C23\u0C02"},
    "policy": {"en": "Policy", "te": "\u0C2A\u0C3E\u0C32\u0C38\u0C40"},
    "business": {"en": "Business", "te": "\u0C35\u0C4D\u0C2F\u0C3E\u0C2A\u0C3E\u0C30\u0C02"},
}
