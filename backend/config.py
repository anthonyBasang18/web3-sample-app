"""Application configuration"""
import os
from dotenv import load_dotenv
from web3 import Web3
import redis

load_dotenv()

# Environment variables
ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
ALCHEMY_URL = f"https://eth-sepolia.g.alchemy.com/v2/{ALCHEMY_API_KEY}"

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))

# Initialize Redis (with fallback)
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
except:
    redis_client = None
    print("Redis not available, caching disabled")
