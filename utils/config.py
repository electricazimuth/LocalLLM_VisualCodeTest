# config.py
import datetime
from pathlib import Path

# --- General Configuration ---
MAIN_START_TIME = datetime.datetime.now()
# Directory where your models (.gguf) are stored
MODEL_DIR = Path("/home/david/data/Models").expanduser().resolve()
# Directory where your prompts (.md) are stored
PROMPT_DIR = Path("/home/david/Documents/LocalLLM_VisualCodeTest/prompts").expanduser().resolve()
# Directory to save the results
RESULTS_DIR = Path("/home/david/Documents/LocalLLM_VisualCodeTest/results/2025.08.06/results").expanduser().resolve()

# --- Model Filtering ---
# Set max/min size to None to disable filtering by size
MAX_SIZE_BYTES = 31 * (1024**3)  # 46 GiB (using 1024^3)
MIN_SIZE_BYTES = 1 * (1024**3)   # 1 GiB

# --- Server/API Configuration ---
DEFAULT_HOST = "127.0.0.1" # Changed from localhost for consistency
DEFAULT_PORT = 5000
SERVER_STARTUP_WAIT = 120  # Increased default wait time slightly
SERVER_COOLDOWN_WAIT = 5
PRIMARY_API_TIMEOUT = 1200 # Timeout for the main generation request (seconds)

# --- Common Generation Parameters (will be translated by backends) ---
# These provide a common ground, backends adapt them or use defaults if not applicable
COMMON_GEN_PARAMS = {
    "max_tokens": 24576, # Max tokens to generate
    "temperature": 0.7,
    "top_k": 64,
    "top_p": 0.95,
    "presence_penalty": 0.0,    # OpenAI style penalty
    "frequency_penalty": 0.0,   # OpenAI style penalty
    #"repeat_penalty": 1.0,
    "seed": -1, # Use random seed
    "stop": [],                 # Stop sequences (OAI style)
    # Add other common parameters you might want to control centrally
    # "stop_sequences": ["{{[INPUT]}}", "{{[OUTPUT]}}"] # Moved to backend defaults potentially
}

# --- Backend Specific Paths ---
KOBOLDCPP_SCRIPT_PATH = Path("/home/david/Documents/koboldcpp/koboldcpp.py").resolve()
LLAMA_CPP_SERVER_PATH = Path("/home/david/Documents/llama.cpp/build/bin/llama-server").resolve() # Adjust if llama-server is elsewhere

# --- Backend Specific Arguments (Defaults) ---
# These are BASE arguments, model path and port/host will be added/overridden
KOBOLDCPP_DEFAULT_ARGS = [
    "python3", str(KOBOLDCPP_SCRIPT_PATH),
    "--usecublas", "normal",
    "--contextsize", "16384",
    "--gpulayers", "96"
]

LLAMA_CPP_DEFAULT_ARGS = [
    str(LLAMA_CPP_SERVER_PATH),
    "-ngl", "99",
    "--ctx-size", "16384",
    # "--chat-template", "llama3", # Optional: Force a specific template if needed
    # Add other common llama.cpp flags like --flash-attn if desired
]