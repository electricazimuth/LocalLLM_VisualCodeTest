# -*- coding: utf-8 -*- # Ensure UTF-8 encoding for potential special chars
# nohup python run_benchmarks.py > runbench.01.log 2>&1 &
import subprocess
import time
import json
import requests
import os
import signal
import sys
import datetime
from pathlib import Path
import glob # Import glob for pattern matching

# --- Configuration ---
main_start_time = datetime.datetime.now()
# Path to your koboldcpp.py script
KOBOLDCPP_SCRIPT = Path("/path_to_koboldcpp/koboldcpp/koboldcpp.py") #.resolve() # Adjust if needed

# Directory where your models (.gguf) are stored
MODEL_DIR = Path("/path_to_gguf/Models/") #.expanduser().resolve() # Adjust to your actual model path
MAX_SIZE_BYTES = 46 * (1024**3) # 50 GiB (using 1024^3)
MIN_SIZE_BYTES = 1 * (1024**3) # 50 GiB (using 1024^3)
# Directory where your prompts (.md) are stored
PROMPT_DIR = Path("/path_to/bench/prompts") #.expanduser().resolve() # Adjust to your actual prompt path

# Directory to save the results
RESULTS_DIR = Path("/path_to/bench/results") #.expanduser().resolve()

# KoboldCpp launch arguments (model path will be added automatically)
# Make sure the port is consistent
# To run on a specific GPU: "--usecublas", "normal", "1",
KOBOLDCPP_ARGS = [
    "python3", str(KOBOLDCPP_SCRIPT),
    "--usecublas", "normal",
    "--port", "5000",
    "--contextsize", "8192",
    "--gpulayers", "96" # Adjust GPU layers if needed per model, or keep common value
    # Add any other common flags you always want to use
]

# API request endpoint
API_URL = "http://localhost:5000/api/v1/generate"
GRAB_DATA_URL = "http://localhost:5000/api/extra/generate/check"

# API request payload (prompt will be inserted)
# Use the structure you provided
API_PAYLOAD_TEMPLATE = {
    "n": 1,
    "max_context_length": 8192,
    "max_length": 6192, # Reduced max_length for faster testing, adjust as needed
    "rep_pen": 1.00,
    "temperature": 0.7, # Slightly lower temp for more deterministic benchmark? Adjust as needed
    "top_p": 0.95,
    "top_k": 64,
    "top_a": 0,
    "typical": 1,
    "tfs": 1,
    "rep_pen_range": 160,
    "rep_pen_slope": 0.7,
    "sampler_order": [6, 0, 1, 3, 4, 2, 5],
    "memory": "",
    "trim_stop": True,
    "genkey": "KCPP_BENCH", # Ensure this is unique enough if running multiple concurrently
    "min_p": 0,
    "dynatemp_range": 0,
    "dynatemp_exponent": 1,
    "smoothing_factor": 0,
    "nsigma": 0,
    "banned_tokens": [],
    "render_special": False,
    "logprobs": False,
    "replace_instruct_placeholders": True,
    "presence_penalty": 0,
    "logit_bias": {},
    "prompt": "{{{{[INPUT]}}}} {prompt} {{{{[OUTPUT]}}}}", # Placeholder - will be formatted later
    "quiet": True, # Keep koboldcpp quiet in the subprocess terminal
    "stop_sequence": ["{{[INPUT]}}", "{{[OUTPUT]}}"], # Add common stop sequences
    "use_default_badwordsids": False,
    "bypass_eos": False
}

# Time to wait for koboldcpp server to start (seconds)
SERVER_STARTUP_WAIT = 90 # Adjust if your models load slower/faster

# Time to wait after terminating koboldcpp before starting next (seconds)
SERVER_COOLDOWN_WAIT = 5

# --- Timeout configuration ---
PRIMARY_API_TIMEOUT = 1200   # Timeout for the main generation request (seconds)
FALLBACK_API_TIMEOUT = 10 # Timeout for the fallback data grab request (seconds)


def model_payload_filter(model_name: str, payload: dict) -> dict:
    """Applies model-specific payload adjustments."""
    if 'qwen' in model_name.lower(): # Check substring for flexibility
        print(f"    Applying Qwen filter to payload.")
        payload["temperature"] = 0.4
        payload["top_k"] = 30
        # payload["min_p"] = 0 # Ensure min_p is handled if needed
    # Add other model-specific adjustments here
    # elif 'mistral' in model_name.lower():
    #    payload["temperature"] = 0.6
    return payload

def model_prompt_filter(model_name: str, prompt: str) -> str:
    """Applies model-specific prompt additions."""
    #if 'qwq' in model_name.lower(): # Example filter
    #    print(f"    Applying 'qwq' filter to prompt.")
    #    prompt += "\nThink step by step but only keep a minimum draft of each thinking step, with 5 words at most. Be concise. Think concisely"
    # Add other prompt filters here
    return prompt

# --- Helper Functions ---
def print_with_timestamp(message: str, start_time: datetime.datetime):
    """
    Prints a message along with the time elapsed since a provided start time.
    """
    now = datetime.datetime.now()
    elapsed_time = now - start_time
    # Format the output string including the elapsed time
    print(f"[{elapsed_time}] {message}")

def is_server_ready(url, timeout=1):
    """Checks if the KoboldCpp API server is responding and model is loaded."""
    try:
        api_model_url = url.replace("/v1/generate", "/v1/model")
        response = requests.get(api_model_url, timeout=timeout)
        if response.status_code == 200:
             try:
                 content = response.json()
                 # Check if 'result' key exists and is not 'inactive'
                 if content.get("result") and content.get("result").lower() != "inactive":
                     return True
                 else:
                     # print("  Server check: API up, waiting for model load...") # Verbose
                     return False
             except (json.JSONDecodeError, AttributeError):
                 # print("  Server check: API up, but unexpected response (likely loading).") # Verbose
                 return False
        return False
    except requests.exceptions.RequestException: # Catches ConnectTimeout, ConnectionError, Timeout
        return False
    except Exception as e:
        print(f"  [WARN] Error checking server readiness at {api_model_url}: {e}")
        return False

def wait_for_server(url, startup_wait_time, check_interval=2):
    """Waits for the server to become ready by polling."""
    print(f"  Waiting up to {startup_wait_time}s for server and model at {url}...")
    start_wait = time.time()
    while time.time() - start_wait < startup_wait_time:
        if is_server_ready(url):
            print(f"  Server and model are ready (took {time.time() - start_wait:.1f}s).")
            return True
        time.sleep(check_interval)
    print(f"  [ERROR] Server did not become ready within {startup_wait_time}s.")
    return False

def check_if_output_exists(results_dir: Path, model_stem: str, prompt_stem: str) -> bool:
    """Checks if an output file for the given model and prompt exists (ignoring timestamp and _fallback suffix)."""
    # Use filesystem-safe stems
    safe_model_stem = model_stem.replace('/', '_').replace('\\', '_')
    safe_prompt_stem = prompt_stem.replace('/', '_').replace('\\', '_')
    pattern = f"{safe_model_stem}_{safe_prompt_stem}_*.md"
    return next(results_dir.glob(pattern), None) is not None

# --- Main Execution ---

print_with_timestamp("Starting KoboldCpp Benchmark Automation...", main_start_time)

# --- Dynamic Discovery ---
print_with_timestamp(f"Scanning for models in: {MODEL_DIR}", main_start_time)

# Use glob directly for cleaner filtering
potential_paths = MODEL_DIR.glob('*.gguf')
filtered_model_paths = []
for path in potential_paths:
    model_filename = path.name
    if not path.is_file(): continue
    # Skip macOS resource fork files and other hidden files
    if model_filename.startswith('.') or model_filename.startswith('._'):
        print(f"  [INFO] Skipping hidden/system file: {model_filename}")
        continue
    # --- Your specific model filtering ---
    #if model_filename.lower().startswith('qwen'):
    #    print(f"  [INFO] Skipping qwen model: {model_filename}")
    #    continue
    # if model_filename.lower().startswith('llama'):
    #     print(f"  [INFO] Skipping model: {model_filename} (starts with 'llama')")
    #     continue
    # --- End specific filtering ---
    try:
        file_size = path.stat().st_size
        if file_size > MAX_SIZE_BYTES:
            print(f"  [INFO] Skipping model: {model_filename} (Size {file_size / (1024**3):.2f} GiB > {MAX_SIZE_BYTES / (1024**3):.0f} GiB)")
            continue
        if file_size < MIN_SIZE_BYTES:
            print(f"  [INFO] Skipping model: {model_filename} (Size {file_size / (1024**3):.2f} GiB < {MIN_SIZE_BYTES / (1024**3):.0f} GiB)")
            continue
    except OSError as e:
        print(f"  [WARN] Cannot access file stats for {model_filename} (skipped): {e}")
        continue
    filtered_model_paths.append(path)

model_paths = sorted(filtered_model_paths)

if not model_paths:
    print(f"[ERROR] No matching *.gguf models found in {MODEL_DIR} based on filters. Exiting.")
    sys.exit(1)
print(f"Found {len(model_paths)} models to process.")

print(f"Scanning for prompts in: {PROMPT_DIR}")
# Filter prompts similarly
potential_prompt_paths = PROMPT_DIR.glob('*.md')
prompt_paths = []
for path in potential_prompt_paths:
     if not path.is_file(): continue
     prompt_filename = path.name
     if prompt_filename.startswith('.') or prompt_filename.startswith('._'):
         print(f"  [INFO] Skipping hidden/system prompt file: {prompt_filename}")
         continue
     prompt_paths.append(path)

prompt_paths = sorted(prompt_paths) # Sort after filtering

if not prompt_paths:
    print(f"[ERROR] No *.md prompts found in {PROMPT_DIR}. Exiting.")
    sys.exit(1)
print(f"Found {len(prompt_paths)} prompts.")

# Create results directory if it doesn't exist
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
print(f"Results will be saved in: {RESULTS_DIR}")

print(f"KoboldCpp Script: {KOBOLDCPP_SCRIPT}")
print("-" * 30)

# --- Signal Handling ---
original_sigint_handler = signal.getsignal(signal.SIGINT)
kobold_process = None

def signal_handler(sig, frame):
    print("\nCtrl+C detected. Shutting down KoboldCpp process if running...")
    if kobold_process and kobold_process.poll() is None:
        print(f"  Terminating KoboldCpp process (PID: {kobold_process.pid})...")
        # Send SIGINT first for graceful shutdown attempt
        kobold_process.send_signal(signal.SIGINT)
        try:
            kobold_process.wait(timeout=10)
            print("  KoboldCpp process terminated gracefully (SIGINT).")
        except subprocess.TimeoutExpired:
            print("  KoboldCpp did not respond to SIGINT, sending SIGTERM...")
            kobold_process.terminate() # More forceful
            try:
                kobold_process.wait(timeout=5)
                print("  KoboldCpp process terminated (SIGTERM).")
            except subprocess.TimeoutExpired:
                print("  KoboldCpp process unresponsive, killing (SIGKILL)...")
                kobold_process.kill() # Most forceful
                kobold_process.wait()
                print("  KoboldCpp process killed.")
    print("Exiting benchmark script.")
    # Restore original handler before exiting abnormally? Optional.
    # signal.signal(signal.SIGINT, original_sigint_handler)
    sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)

# --- Benchmarking Loop ---
total_combinations = len(model_paths) * len(prompt_paths)
run_counter = 0
failed_runs = [] # List to store tuples of (model_filename, prompt_filename, reason)
skipped_models_count = 0
skipped_prompts_count = 0

for model_idx, model_path in enumerate(model_paths):
    model_start_time = datetime.datetime.now()
    model_filename = model_path.name
    model_stem = model_path.stem # Filename without extension

    print_with_timestamp(f"\n--- Evaluating Model {model_idx+1}/{len(model_paths)}: {model_filename} ---", main_start_time)

    # --- MODEL SKIP CHECK ---
    # Check if all prompts for this model already have results
    existing_output_count = 0
    for prompt_path_check in prompt_paths:
        prompt_stem_check = prompt_path_check.stem
        if check_if_output_exists(RESULTS_DIR, model_stem, prompt_stem_check):
            existing_output_count += 1

    if existing_output_count == len(prompt_paths):
        print_with_timestamp(f"  [SKIP] All {len(prompt_paths)} prompt outputs already exist for model '{model_filename}'. Skipping model.", main_start_time)
        skipped_models_count += 1
        run_counter += len(prompt_paths) # Add skipped prompts to the run counter
        continue # Skip to the next model
    elif existing_output_count > 0:
         print_with_timestamp(f"  [INFO] Found {existing_output_count}/{len(prompt_paths)} existing outputs for model '{model_filename}'. Will skip individual prompts.", main_start_time)
    # --- END MODEL SKIP CHECK ---

    # If we're here, at least one prompt needs running for this model
    print_with_timestamp(f"--- Starting Model {model_idx+1-skipped_models_count}/{len(model_paths)-skipped_models_count} (Actual): {model_filename} ---", model_start_time)

    if not model_path.exists():
        print(f"  [ERROR] Model file check failed: {model_path}. Skipping model.")
        # Mark all *remaining* (non-existing) prompts for this model as failed
        for prompt_path_fail in prompt_paths:
            prompt_stem_fail = prompt_path_fail.stem
            if not check_if_output_exists(RESULTS_DIR, model_stem, prompt_stem_fail):
                 run_counter += 1 # Increment counter for this failed attempt
                 failed_runs.append((model_filename, prompt_path_fail.name, "Model file not found before launch"))
        continue

    # Construct command specific to this model
    current_command = KOBOLDCPP_ARGS + ["--model", str(model_path)]
    print(f"  Running command: {' '.join(current_command)}")

    kobold_process = None # Ensure reset before launch attempt
    server_started_successfully = False
    prompts_processed_this_model = 0 # Track prompts attempted/skipped *within* this model's run

    try:
        # Start koboldcpp process
        print("  Launching KoboldCpp...")
        # Capture stderr to help diagnose startup issues, use DEVNULL for stdout
        kobold_process = subprocess.Popen(current_command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
        print(f"  KoboldCpp process started (PID: {kobold_process.pid}).")

        # Wait for the server to be ready
        if not wait_for_server(API_URL, SERVER_STARTUP_WAIT):
             stderr_output = "[Stderr not available or empty]"
             if kobold_process:
                 try:
                     # Ensure process hasn't terminated unexpectedly
                     if kobold_process.poll() is None:
                         # Give stderr a moment
                         time.sleep(0.5)
                         stderr_output = kobold_process.stderr.read() if kobold_process.stderr else "[Stderr stream closed]"
                     else:
                         stderr_output = "[Process terminated unexpectedly during startup]"
                 except Exception as e:
                     stderr_output = f"[Error reading stderr: {e}]"

             print(f"  [ERROR] Server failed to start or respond for model {model_filename}. Killing process.")
             if kobold_process and kobold_process.poll() is None:
                 kobold_process.terminate()
                 try: kobold_process.wait(timeout=5)
                 except subprocess.TimeoutExpired: kobold_process.kill(); kobold_process.wait()
             print(f"  KoboldCpp stderr glimpse:\n---\n{stderr_output[:1000]}...\n---") # Show first 1KB

             # Mark all *remaining* prompts for this model as failed
             for prompt_path_fail in prompt_paths:
                 prompt_stem_fail = prompt_path_fail.stem
                 if not check_if_output_exists(RESULTS_DIR, model_stem, prompt_stem_fail):
                     run_counter += 1 # Count this as an attempted run
                     failed_runs.append((model_filename, prompt_path_fail.name, "Server failed to start"))
             kobold_process = None # Reset process variable
             # No 'continue' here, finally block will handle cooldown
        else:
            server_started_successfully = True # Server is up, proceed with prompts

        # --- Inner Loop: Iterate through prompts for the current model ---
        if server_started_successfully: # Only run prompts if server started
            for prompt_idx, prompt_path in enumerate(prompt_paths):
                prompt_filename = prompt_path.name
                prompt_stem = prompt_path.stem # Filename without extension
                prompts_processed_this_model += 1 # Count this prompt towards model's processing

                # --- PROMPT SKIP CHECK ---
                if check_if_output_exists(RESULTS_DIR, model_stem, prompt_stem):
                    if prompts_processed_this_model == existing_output_count + 1: # Only print once if skipping occurs
                         print_with_timestamp(f"\n  Skipping prompts for {model_filename} where output exists...", model_start_time)
                    print(f"    [SKIP] Output for Prompt '{prompt_filename}' already exists.")
                    run_counter += 1 # Still count towards total progress
                    skipped_prompts_count += 1
                    continue # Skip to the next prompt
                # --- END PROMPT SKIP CHECK ---

                # If we reach here, the prompt needs to be run
                run_counter += 1 # Increment run counter *before* attempting the run

                print_with_timestamp(f"\n  [{run_counter}/{total_combinations}] Running Prompt: {prompt_filename} ({prompt_idx+1}/{len(prompt_paths)})", model_start_time)

                # Read prompt content
                try:
                    # Read as bytes first to detect encoding, then decode robustly
                    raw_bytes = prompt_path.read_bytes()
                    # Basic check for UTF-8 BOM, remove if present
                    if raw_bytes.startswith(b'\xef\xbb\xbf'):
                        raw_bytes = raw_bytes[3:]
                    # Decode using UTF-8, replace errors
                    benchmark_prompt = raw_bytes.decode('utf-8', errors='replace').strip()
                    # Clean potential null bytes or control chars often found at end of file
                    benchmark_prompt = ''.join(c for c in benchmark_prompt if c.isprintable() or c.isspace())

                    # --- Debugging: Inspect the cleaned original prompt ---
                    # print("--- Cleaned Original Prompt ---")
                    # print(repr(benchmark_prompt)) # Use repr() to see invisible chars
                    # print("-" * 30)

                    if not benchmark_prompt:
                        print(f"    [WARN] Prompt file {prompt_path} is empty or contains only non-printable characters. Skipping.")
                        failed_runs.append((model_filename, prompt_filename, "Prompt file empty or invalid"))
                        continue # Skip to next prompt

                    # Apply model-specific prompt filtering
                    payload_prompt = model_prompt_filter(model_filename, benchmark_prompt)

                    # --- Debugging: Inspect the final prompt ---
                    # print("--- Final Prompt Sent to LLM ---")
                    # print(repr(payload_prompt)) # Use repr() again
                    # print("-" * 30)

                except Exception as e:
                    print(f"    [ERROR] Failed to read or process prompt file {prompt_path}: {e}. Skipping prompt.")
                    failed_runs.append((model_filename, prompt_filename, f"Failed to read/process prompt: {e}"))
                    continue # Skip to next prompt

                # Prepare API payload for this specific prompt
                api_payload = API_PAYLOAD_TEMPLATE.copy()
                api_payload["genkey"] = f"KCPP_BENCH_{model_stem}_{prompt_stem}" # More specific genkey
                api_payload["prompt"] = API_PAYLOAD_TEMPLATE["prompt"].format(prompt=payload_prompt)

                # Apply model-specific payload filtering
                api_payload = model_payload_filter(model_filename, api_payload)

                # --- API Call with Timeout Fallback ---
                final_api_response = None
                generation_time = 0
                request_successful = False
                is_fallback = False

                try:
                    # Send PRIMARY API request
                    print(f"    Sending API request (max_length={api_payload['max_length']}, timeout={PRIMARY_API_TIMEOUT}s)...")
                    # print(json.dumps(api_payload, indent=2)) # Uncomment for deep debugging
                    start_req_time = time.time()
                    response = requests.post(API_URL, json=api_payload, timeout=PRIMARY_API_TIMEOUT)
                    end_req_time = time.time()
                    generation_time = end_req_time - start_req_time

                    response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)

                    # Process successful primary response
                    final_api_response = response.json()
                    request_successful = True
                    print(f"    Primary generation successful (took {generation_time:.2f}s).")

                except requests.exceptions.Timeout:
                    end_req_time = time.time()
                    generation_time = end_req_time - start_req_time # Time until timeout
                    print(f"    [WARNING] Primary API request timed out after {generation_time:.2f}s. Attempting fallback...")
                    is_fallback = True
                    grab_payload = {"genkey": api_payload["genkey"]} # Use the same genkey for the check

                    try:
                        # Attempt the FALLBACK request
                        print(f"    Sending fallback request to {GRAB_DATA_URL} (timeout={FALLBACK_API_TIMEOUT}s)...")
                        start_grab_time = time.time()
                        grab_response = requests.post(GRAB_DATA_URL, json=grab_payload, timeout=FALLBACK_API_TIMEOUT)
                        end_grab_time = time.time()
                        print(f"    Fallback request attempt took {end_grab_time - start_grab_time:.2f}s.")

                        grab_response.raise_for_status() # Check fallback status

                        final_api_response = grab_response.json()
                        request_successful = True # We got a response via fallback
                        print(f"    Fallback data retrieval successful.")
                        # Note: We don't add to failed_runs here because the fallback succeeded

                    except requests.exceptions.RequestException as grab_e:
                        print(f"    [ERROR] Fallback request to {GRAB_DATA_URL} failed: {grab_e}")
                        failed_runs.append((model_filename, prompt_filename, f"Primary API timeout AND Fallback failed: {grab_e}"))
                    except Exception as grab_e_unexpected:
                        print(f"    [ERROR] Unexpected error during fallback request/processing: {grab_e_unexpected}")
                        failed_runs.append((model_filename, prompt_filename, f"Primary API timeout AND Fallback unexpected error: {grab_e_unexpected}"))

                except requests.exceptions.RequestException as e:
                    print(f"    [ERROR] Primary API request failed (non-timeout): {e}")
                    failed_runs.append((model_filename, prompt_filename, f"API request failed: {e}"))
                except Exception as e:
                    # Catch unexpected errors during primary request/processing (e.g., JSON decode error)
                    print(f"    [ERROR] An unexpected error occurred during API call or initial processing: {e}")
                    failed_runs.append((model_filename, prompt_filename, f"Unexpected error: {e}"))

                # --- Processing Logic (Runs if final_api_response is populated) ---
                if request_successful and final_api_response is not None:
                    print("    Processing response data...")
                    if is_fallback:
                        print("      (Using data obtained from fallback URL)")
                    # print("      Response JSON:", json.dumps(final_api_response, indent=2)) # Verbose debugging

                    # --- Try to extract the text ---
                    generated_text = None
                    try:
                        # !!! IMPORTANT: Verify the structure of BOTH primary and fallback responses !!!
                        # This assumes the fallback response ALSO has ["results"][0]["text"]
                        # Adjust the 'if is_fallback:' block if the structure differs.
                        results_list = final_api_response.get("results")
                        if results_list and isinstance(results_list, list) and len(results_list) > 0:
                             text_entry = results_list[0]
                             if isinstance(text_entry, dict):
                                 generated_text = text_entry.get("text")

                        # Example for different fallback structure:
                        # if is_fallback:
                        #     generated_text = final_api_response.get("data", {}).get("completion_text")
                        # else:
                        #      results_list = final_api_response.get("results")
                        #      # ... standard extraction ...

                        if generated_text is None or not isinstance(generated_text, str):
                            print("    [ERROR] 'text' field not found or not a string in the received API response.")
                            print(f"    Response JSON: {json.dumps(final_api_response, indent=2)}")
                            # Avoid adding duplicate failure if already added above
                            failure_reason = "Text not found/invalid in fallback response" if is_fallback else "Text not found/invalid in primary response"
                            if not any(entry[0] == model_filename and entry[1] == prompt_filename for entry in failed_runs):
                                 failed_runs.append((model_filename, prompt_filename, failure_reason))
                        else:
                             # Strip potentially unwanted whitespace/newlines from start/end
                             generated_text = generated_text.strip()
                             print(f"    Text successfully extracted ({len(generated_text)} chars).")


                    except (AttributeError, KeyError, IndexError, TypeError) as extract_err:
                        print(f"    [ERROR] Failed to extract text due to structure error: {extract_err}")
                        print(f"    Response JSON: {json.dumps(final_api_response, indent=2)}")
                        failure_reason = f"Extraction error from fallback response: {extract_err}" if is_fallback else f"Extraction error from primary response: {extract_err}"
                        if not any(entry[0] == model_filename and entry[1] == prompt_filename for entry in failed_runs):
                             failed_runs.append((model_filename, prompt_filename, failure_reason))
                        generated_text = None # Ensure it's None if extraction fails

                    # --- Save the result if text was extracted ---
                    if generated_text is not None and generated_text: # Also check if not empty string after strip
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        # Ensure filename components are filesystem-safe
                        safe_model_stem = model_stem.replace('/', '_').replace('\\', '_').replace(':', '_')
                        safe_prompt_stem = prompt_stem.replace('/', '_').replace('\\', '_').replace(':', '_')
                        suffix = '_fallback' if is_fallback else ''
                        output_filename = f"{safe_model_stem}_{safe_prompt_stem}_{timestamp}{suffix}.md"
                        output_path = RESULTS_DIR / output_filename
                        generated_text += f"\n <!-- {generation_time:.2f}s -->"
                        try:
                            with open(output_path, 'w', encoding='utf-8') as f_out:
                                f_out.write(generated_text)
                            print(f"    Result saved to: {output_path}")
                        except IOError as e:
                            print(f"    [ERROR] Failed to write output file {output_path}: {e}")
                            if not any(entry[0] == model_filename and entry[1] == prompt_filename for entry in failed_runs):
                                 failed_runs.append((model_filename, prompt_filename, f"Failed to write output: {e}"))
                    elif generated_text is not None: # It was None or empty string
                         print("    [INFO] Extracted text was empty. Nothing to save.")
                         # Optionally mark as failed if empty text is considered failure
                         # failure_reason = "Extracted text was empty"
                         # if not any(entry[0] == model_filename and entry[1] == prompt_filename for entry in failed_runs):
                         #      failed_runs.append((model_filename, prompt_filename, failure_reason))


                elif not request_successful:
                    # This branch is hit if primary failed (non-timeout) OR primary timed out AND fallback failed.
                    print("    Skipping processing and saving due to request failure.")
                    # The specific error should have been logged and added to failed_runs already.

            # --- End of inner prompt loop ---
        # --- End of server_started_successfully check ---

    except Exception as model_loop_error:
        # Catch unexpected errors during the model setup/server check/prompt loop itself
        print(f"  [ERROR] An unexpected error occurred during processing for model {model_filename}: {model_loop_error}")
        # Try to mark remaining non-existent prompts as failed
        try:
            for prompt_path_fail in prompt_paths:
                prompt_stem_fail = prompt_path_fail.stem
                if not check_if_output_exists(RESULTS_DIR, model_stem, prompt_stem_fail):
                    # Check if failure wasn't already recorded for this specific prompt
                    if not any(f[0] == model_filename and f[1] == prompt_path_fail.name for f in failed_runs):
                         run_counter += 1 # Assume it would have been attempted
                         failed_runs.append((model_filename, prompt_path_fail.name, f"Model-level error: {model_loop_error}"))
        except Exception as fail_log_err:
             print(f"  [WARN] Additional error while logging failures after model error: {fail_log_err}")

    finally:
        # --- Shutdown Kobold process for this model ---
        print_with_timestamp(f" == Finished Model Run: {model_filename} ==", model_start_time)
        if kobold_process and kobold_process.poll() is None: # Check if process is still running
            print(f"\n  Terminating KoboldCpp process for {model_filename} (PID: {kobold_process.pid})...")
            kobold_process.send_signal(signal.SIGINT) # Try graceful SIGINT first
            try:
                kobold_process.wait(timeout=10)
                print("  KoboldCpp process terminated (SIGINT).")
            except subprocess.TimeoutExpired:
                print("  KoboldCpp did not respond to SIGINT, sending SIGTERM...")
                kobold_process.terminate()
                try:
                    kobold_process.wait(timeout=5)
                    print("  KoboldCpp process terminated (SIGTERM).")
                except subprocess.TimeoutExpired:
                    print("  KoboldCpp did not terminate gracefully, killing (SIGKILL)...")
                    kobold_process.kill()
                    kobold_process.wait()
                    print("  KoboldCpp process killed.")
            # Ensure stderr is closed if process terminated
            if kobold_process.stderr:
                kobold_process.stderr.close()
        kobold_process = None # Reset process variable

        # Wait before starting the next model if this wasn't the last one
        if model_idx < len(model_paths) - 1:
            print(f"\nWaiting {SERVER_COOLDOWN_WAIT}s before next model...")
            time.sleep(SERVER_COOLDOWN_WAIT)
    # --- End of outer model loop ---


# Restore original signal handler
signal.signal(signal.SIGINT, original_sigint_handler)

# --- Final Summary ---
print("\n" + "="*40)
print("Benchmark Script Finished")
end_run_time = datetime.datetime.now()
print(f"Total elapsed time: {end_run_time - main_start_time}")
print(f"Total Model/Prompt Combinations Configured: {total_combinations}")
print(f"Total Runs Processed (Attempted or Skipped): {run_counter}")
print(f"  - Models Skipped Entirely (All prompts existed): {skipped_models_count}")
print(f"  - Individual Prompts Skipped (Output existed): {skipped_prompts_count}")
# Actual attempted runs = total processed - total skipped
actual_attempts = run_counter - (skipped_models_count * len(prompt_paths)) - skipped_prompts_count
# Successful runs = actual attempts - failures logged
# Note: Failed_runs might include model-level failures affecting multiple prompts.
# A more precise success count might need refinement based on how failures are logged.
# This counts unique failure entries.
successful_runs = actual_attempts - len(failed_runs)
print(f"Successful Runs (Generated output file): {max(0, successful_runs)}") # Ensure non-negative
print(f"Failed Runs (Logged in summary): {len(failed_runs)}")
print(f"Results saved in directory: {RESULTS_DIR}")

if failed_runs:
    print("\n--- Summary of Failures ---")
    # Sort failures for consistency
    failed_runs.sort(key=lambda x: (x[0], x[1]))
    for model, prompt, reason in failed_runs:
        print(f"  - Model: {model}, Prompt: {prompt}, Reason: {reason}")
print("="*40)