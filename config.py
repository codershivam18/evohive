import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configuration for EvoHive
class Config:
    # --- LLM Settings (Optimized for Lightning Speed on RTX 3050) ---
    # We use 3b for EVERYTHING to avoid VRAM swapping
    MAIN_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b") 
    FAST_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")
    # Embedding model for memory
    EMBEDDING_MODEL = "nomic-embed-text"
    
    # Cloud API Settings (For public deployment)
    API_KEY = os.getenv("LLM_API_KEY", None)
    BASE_URL = os.getenv("LLM_BASE_URL", None) # e.g. https://api.groq.com/openai/v1
    
    # --- Evolution Parameters ---
    POPULATION_SIZE = 12          # Balanced for quality and speed
    NUM_GENERATIONS = 6           # Optimal rate for deep refinement
    MUTATION_RATE = 0.3           # Slightly lower for more stability
    ELITE_PERCENTAGE = 0.25        # Keep more of the best prompts
    
    # --- Agent Hive Settings ---
    ROLES = ["researcher", "critic", "coder", "synthesizer"]
    
    # --- UI & Aesthetics ---
    APP_TITLE = "🧬 EvoHive AI Lab"
    THEME_COLORS = {
        "primary": "#6366f1",     # Indigo
        "secondary": "#a855f7",   # Purple
        "background": "#0f172a",  # Slate Dark
        "text": "#f8fafc"
    }
    
    # --- Paths ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    BEST_PROMPTS_DIR = os.path.join(BASE_DIR, "best_prompts")
    MEMORY_DIR = os.path.join(BASE_DIR, "evohive_memory")
    
    # Ensure directories exist
    os.makedirs(BEST_PROMPTS_DIR, exist_ok=True)
    os.makedirs(MEMORY_DIR, exist_ok=True)

config = Config()