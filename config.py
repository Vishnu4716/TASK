import os
from dotenv import load_dotenv

load_dotenv()

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "").rstrip("/")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen3-6-27b-fp8")

HTTP_PROXY = os.getenv("HTTP_PROXY", "")
HTTPS_PROXY = os.getenv("HTTPS_PROXY", "")

AUTO_RESOLUTION_THRESHOLD = float(os.getenv("AUTO_RESOLUTION_THRESHOLD", "50.00"))
MAX_RERIDE_CREDITS_30D = int(os.getenv("MAX_RERIDE_CREDITS_30D", "3"))

DB_PATH = os.getenv("DB_PATH", "fare_agent.db")

PROXIES = {}
if HTTP_PROXY:
    PROXIES["http"] = HTTP_PROXY
if HTTPS_PROXY:
    PROXIES["https"] = HTTPS_PROXY
