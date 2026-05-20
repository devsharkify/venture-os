from motor.motor_asyncio import AsyncIOMotorClient
from imagekitio import ImageKit
from pathlib import Path
from dotenv import load_dotenv
import os
import logging

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection. If MONGO_URL is unset OR contains .env.example
# placeholder values, fall back to mongomock-motor so the server boots
# locally without Atlas. The fallback is process-local and resets on every
# restart - set MONGO_URL for real persistence.
mongo_url = os.environ.get('MONGO_URL', '').strip()
db_name = os.environ.get('DB_NAME', 'mint_street').strip() or 'mint_street'

_PLACEHOLDER_HINTS = ('your-cluster', 'USER:PASSWORD', 'YOUR_PASSWORD', 'your-mongo-uri')
_is_placeholder = any(hint in mongo_url for hint in _PLACEHOLDER_HINTS)

if mongo_url and not _is_placeholder:
    client = AsyncIOMotorClient(mongo_url)
else:
    try:
        from mongomock_motor import AsyncMongoMockClient
        client = AsyncMongoMockClient()
        reason = "MONGO_URL contains placeholder values" if _is_placeholder else "MONGO_URL unset"
        print(f"[database] {reason} - using in-memory mongomock (db_name={db_name})")
    except ImportError:
        raise RuntimeError(
            "MONGO_URL is not set / is placeholder and mongomock-motor is "
            "not installed. Either set a real MONGO_URL in backend/.env or "
            "`pip install mongomock-motor`."
        )

db = client[db_name]

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
