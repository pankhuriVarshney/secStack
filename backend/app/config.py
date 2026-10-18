import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "secstack")
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
SEED_SIZE = int(os.getenv("SEED_SIZE", "600"))
K_CLUSTERS = int(os.getenv("K_CLUSTERS", "8"))

# Agentic AI layer
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

AGENT_WORKSPACE = os.getenv("AGENT_WORKSPACE", "agent_workspace")
