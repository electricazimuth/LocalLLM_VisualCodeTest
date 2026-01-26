# -*- coding: utf-8 -*-
import argparse
import sys
import time
import datetime
import signal
import re
from pathlib import Path

# --- Import New Config Logic ---
try:
    from config_loader import ConfigLoader
    from backend import KoboldBackend, LlamaCppBackend
except ImportError as e:
    print(f"[FATAL] Import Error: {e}")
    print("Ensure you are running this from the parent directory or have set PYTHONPATH.")
    sys.exit(1)

# --- Load Configuration ---
try:
    # Looks for config.yaml in current dir or parent dir
    cfg = ConfigLoader("config.yaml") 
except Exception as e:
    print(f"[FATAL] Configuration Load Error: {e}")
    sys.exit(1)

# --- Helper Functions ---
def print_with_timestamp(message: str, start_time: datetime.datetime):
    """Prints a message along with the time elapsed."""
    now = datetime.datetime.now()
    elapsed_time = now - start_time
    print(f"[{elapsed_time}] {message}")

def wait_for_server(backend, startup_wait_time: int, check_interval: int = 3):
    """Waits for the server to become ready."""
    print(f"  Waiting up to {startup_wait_time}s for {backend.get_backend_name()}...")
    start_wait = time.time()
    
    while time.time() - start_wait < startup_wait_time:
        if backend.is_server_ready():
            print(f"  Server is ready (took {time.time() - start_wait:.1f}s).")
            return True
        time.sleep(check_interval)

    print(f"  [ERROR] Server did not become ready within {startup_wait_time}s.")
    print(f"  Stderr glimpse:\n---\n{backend.get_process_stderr()[-2000:]}\n---") 
    return False

def check_if_output_exists(results_dir: Path, model_stem: str, prompt_stem: str) -> bool:
    """Checks if an output file exists for the given model/prompt combo."""
    safe_model = model_stem.replace('/', '_').replace('\\', '_').replace(':','_')
    safe_prompt = prompt_stem.replace('/', '_').replace('\\', '_').replace(':','_')
    pattern = f"{safe_model}_{safe_prompt}_*.md"
    try:
        return any(results_dir.glob(pattern))
    except Exception:
        return False

def get_backend_instance(backend_name: str, config_loader: ConfigLoader, host: str, port: int):
    if backend_name == "koboldcpp":
        return KoboldBackend(config_loader, host, port)
    elif backend_name == "llamacpp":
        return LlamaCppBackend(config_loader, host, port)
    else:
        raise ValueError(f"Unknown backend: {backend_name}")

# --- Argument Parsing ---
# Defaults are now pulled from config.yaml
available_backends = list(cfg.get_backend_names()) if hasattr(cfg, 'get_backend_names') else ["llamacpp", "koboldcpp"]

parser = argparse.ArgumentParser(description="Run LLM Benchmarks via YAML Config.")
parser.add_argument(
    "--backend",
    type=str,
    default=cfg.server_config.get('default_backend', "llamacpp"),
    choices=available_backends,
    help="The LLM backend to use (must be defined in config.yaml). llamacpp | koboldcpp"
)
parser.add_argument(
    "--port",
    type=int,
    default=cfg.server_config.get('port', 5000),
    help="Port for the backend server."
)
parser.add_argument(
    "--host",
    type=str,
    default=cfg.server_config.get('host', '127.0.0.1'),
    help="Host IP for the backend server."
)

args = parser.parse_args()

# --- Main Execution ---
start_time = datetime.datetime.now()
print_with_timestamp(f"Starting Benchmark (Backend: {args.backend})", start_time)

# 1. Setup Directories
model_dir = cfg.paths.get('models')
prompt_dir = cfg.paths.get('prompts')
results_dir = cfg.paths.get('results')

# filter by size
max_size_gigs = cfg.server_config.get('max_size_gigs')
min_size_gigs = cfg.server_config.get('min_size_gigs')
max_size_bytes = max_size_gigs * (1024**3)  
min_size_bytes = min_size_gigs * (1024**3)   # 1 GiB



if not model_dir or not model_dir.exists():
    print(f"[ERROR] Model directory not found: {model_dir}")
    sys.exit(1)
if not prompt_dir or not prompt_dir.exists():
    print(f"[ERROR] Prompt directory not found: {prompt_dir}")
    sys.exit(1)

results_dir.mkdir(parents=True, exist_ok=True)

# 2. Discover Files
print(f"Scanning models in: {model_dir}")
# Filter for .gguf, ignore hidden, ignore multi-part parts > 1

potential_paths = model_dir.glob('*.gguf')
filtered_model_paths = []
for path in potential_paths:
    model_filename = path.name
    if not path.is_file(): continue
    if model_filename.startswith('.') or model_filename.startswith('._'):
        # print(f"  [INFO] Skipping hidden/system file: {model_filename}")
        continue
    # --- Add any specific model filename filtering here if needed ---
    # if 'exclude_this' in model_filename.lower(): continue

    # --- Filter out subsequent parts of multi-file models ---
    # This regex looks for the pattern "-<part_num>-of-<total_parts>.gguf" at the end of the filename.
    match = re.search(r'-(\d+)-of-(\d+)\.gguf$', model_filename)
    if match:
        part_number = int(match.group(1))
        # If it's a multi-part file, only include the first part (e.g., -00001-of-...).
        if part_number > 1:
            # print(f"  [INFO] Skipping subsequent model part: {model_filename}")
            continue

    try:
        file_size = path.stat().st_size
        if max_size_bytes is not None and file_size > max_size_bytes:
            print(f"  [INFO] Skipping model: {model_filename} (Size {file_size / (1024**3):.2f} GiB > {max_size_bytes / (1024**3):.0f} GiB)")
            continue
        if min_size_bytes is not None and file_size < min_size_bytes:
            print(f"  [INFO] Skipping model: {model_filename} (Size {file_size / (1024**3):.2f} GiB < {min_size_bytes / (1024**3):.0f} GiB)")
            continue
    except OSError as e:
        print(f"  [WARN] Cannot access file stats for {model_filename} (skipped): {e}")
        continue
    filtered_model_paths.append(path)

all_models = sorted(filtered_model_paths)



print(f"Scanning prompts in: {prompt_dir}")
all_prompts = sorted([p for p in prompt_dir.glob('*.md') if not p.name.startswith('.')])

if not all_models:
    print("[ERROR] No models found.")
    sys.exit(1)
if not all_prompts:
    print("[ERROR] No prompts found.")
    sys.exit(1)

print(f"Found {len(all_models)} models and {len(all_prompts)} prompts.")

# 3. Initialize Backend
try:
    backend = get_backend_instance(args.backend, cfg, args.host, args.port)
except Exception as e:
    print(f"[FATAL] Failed to initialize backend: {e}")
    sys.exit(1)

# 4. Signal Handling
def signal_handler(sig, frame):
    print("\nCtrl+C detected. Shutting down...")
    backend.stop_server()
    sys.exit(1)
signal.signal(signal.SIGINT, signal_handler)

# --- Run Loop ---
run_counter = 0
failed_runs = []

for i, model_path in enumerate(all_models):
    model_name = model_path.name
    model_stem = model_path.stem
    
    # --- CONFIGURATION MATCHING ---
    # This is where the magic happens. We get the specific config for this model
    # from the YAML file (merged with defaults).
    model_config = cfg.get_model_config(model_name)
    
    print("\n" + "="*60)
    print(f"Model {i+1}/{len(all_models)}: {model_name}")
    print("="*60)
    # Debug print to verify config loaded
    # print(f"  [Config] Startup Args: {model_config.get('startup_args')}")
    # print(f"  [Config] Gen Params: {model_config.get('generation_params')}")

    # Check if we should skip this model entirely (if all outputs exist)
    existing_outputs = sum(1 for p in all_prompts if check_if_output_exists(results_dir, model_stem, p.stem))
    if existing_outputs == len(all_prompts):
        print(f"  [SKIP] All {len(all_prompts)} outputs exist. Skipping model.")
        continue

    # Start Server
    if not backend.start_server(model_path, model_config):
        print("  [ERROR] Failed to start server. Skipping model.")
        failed_runs.append((model_name, "ALL", "Server Start Failed"))
        continue

    # Wait for Ready
    if not wait_for_server(backend, cfg.server_config.get('startup_wait', 420)):
        backend.stop_server()
        failed_runs.append((model_name, "ALL", "Server Timeout"))
        continue

    # Process Prompts
    for j, prompt_path in enumerate(all_prompts):
        prompt_name = prompt_path.name
        
        if check_if_output_exists(results_dir, model_stem, prompt_path.stem):
            print(f"    [SKIP] Output exists for {prompt_name}")
            continue

        print(f"    Running Prompt {j+1}/{len(all_prompts)}: {prompt_name}")
        
        try:
            # Read Prompt
            raw_text = prompt_path.read_text(encoding='utf-8', errors='replace')
            # Sanitize BOM if present
            if raw_text.startswith('\ufeff'): raw_text = raw_text[1:]
            
            # GENERATE
            # We pass the YAML-derived configs directly to the backend
            generated_text, gen_time, success, fallback = backend.generate(
                prompt=raw_text,
                generation_params=model_config['generation_params'],
                prompt_template=model_config['prompt_template']
            )

            if success and generated_text:
                # Save
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_model = model_stem.replace('/', '_').replace('\\', '_').replace(':', '_')
                safe_prompt = prompt_path.stem.replace('/', '_').replace('\\', '_').replace(':', '_')
                suffix = '_fallback' if fallback else ''
                out_filename = f"{safe_model}_{safe_prompt}_{timestamp}{suffix}.md"
                
                meta_comment = (
                    f"\n\n<!-- Benchmark Info -->\n"
                    f"<!-- Backend: {backend.get_backend_name()} -->\n"
                    f"<!-- Model: {model_name} -->\n"
                    f"<!-- Prompt: {prompt_name} -->\n"
                    f"<!-- Time: {gen_time:.2f}s -->\n"
                    f"<!-- Fallback: {fallback} -->"
                )
                
                (results_dir / out_filename).write_text(generated_text + meta_comment, encoding='utf-8')
                print(f"      Saved ({gen_time:.2f}s)")
                run_counter += 1
            else:
                print("      [FAIL] Generation failed or returned empty.")
                failed_runs.append((model_name, prompt_name, "Generation Failed"))

        except Exception as e:
            print(f"      [ERROR] Unexpected error: {e}")
            failed_runs.append((model_name, prompt_name, f"Exception: {e}"))

    # Cleanup Model
    backend.stop_server()
    
    if i < len(all_models) - 1:
        cooldown = cfg.server_config.get('cooldown_wait', 5)
        print(f"  Cooldown {cooldown}s...")
        time.sleep(cooldown)

# --- Summary ---
print("\n" + "="*60)
print("Benchmark Finished")
print(f"Total Successful Runs: {run_counter}")
print(f"Failures: {len(failed_runs)}")
if failed_runs:
    for m, p, r in failed_runs:
        print(f"  - {m} | {p} : {r}")
print("="*60)