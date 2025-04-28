# -*- coding: utf-8 -*- # Ensure UTF-8 encoding
# nohup python run_benchmark.py --backend llamacpp > runbench.llamacpp.log 2>&1 &
# nohup python run_benchmark.py --backend koboldcpp > runbench.koboldcpp.log 2>&1 &

import subprocess
import time
import json
import requests
import os
import signal
import sys
import datetime
from pathlib import Path
import glob
import argparse # Use argparse for command-line arguments

# --- Import Configuration and Backends ---
import config
from backends.base_backend import LLMBackend
# Import specific backends dynamically later based on args

# --- Helper Functions ---
def print_with_timestamp(message: str, start_time: datetime.datetime):
    """Prints a message along with the time elapsed since a provided start time."""
    now = datetime.datetime.now()
    elapsed_time = now - start_time
    print(f"[{elapsed_time}] {message}")

def wait_for_server(backend: LLMBackend, startup_wait_time: int, check_interval: int = 2):
    """Waits for the server to become ready by polling the backend's check."""
    print(f"  Waiting up to {startup_wait_time}s for {backend.get_backend_name()} server and model...")
    start_wait = time.time()
    last_stderr_check_time = start_wait
    stderr_buffer = ""
    check_count = 0 # Counter for checks

    while time.time() - start_wait < startup_wait_time:
        check_count += 1
        print(f"    Attempt {check_count}: Checking server readiness every {check_interval}...", end='\r')

        if backend.is_server_ready():
            print(f"  Server and model are ready (took {time.time() - start_wait:.1f}s).")
            return True

        # Periodically check for new stderr output if server isn't ready
        # current_time = time.time()

        #if current_time - last_stderr_check_time > 10: # Check stderr every 10s -- this seems to hang the script
        #     try:
        #         new_stderr = backend.get_process_stderr() # Assuming backend provides a way to get stderr
        #         if new_stderr:
        #            stderr_buffer += new_stderr
        #            # Optional: Print stderr updates immediately?
        #            # print(f"  [Stderr Update]:\n{new_stderr}")
        #     except Exception as e:
        #         print(f"  [WARN] Error reading stderr during wait: {e}")
        #     last_stderr_check_time = current_time

        time.sleep(check_interval)

    print(f"  [ERROR] Server did not become ready within {startup_wait_time}s.")
    print(f"  Potential {backend.get_backend_name()} stderr glimpse during wait:\n---\n{stderr_buffer[-2000:]}\n---") # Show last 2KB
    return False


def check_if_output_exists(results_dir: Path, model_stem: str, prompt_stem: str) -> bool:
    """Checks if an output file for the given model and prompt exists (ignoring timestamp and suffix)."""
    safe_model_stem = model_stem.replace('/', '_').replace('\\', '_').replace(':','_')
    safe_prompt_stem = prompt_stem.replace('/', '_').replace('\\', '_').replace(':','_')
    pattern = f"{safe_model_stem}_{safe_prompt_stem}_*.md"
    # Check if any file matches the pattern
    try:
        return next(results_dir.glob(pattern), None) is not None
    except Exception as e:
        print(f"  [WARN] Error checking for existing output file with pattern '{pattern}': {e}")
        return False # Safer to assume it doesn't exist if check fails

def load_backend(backend_name: str) -> LLMBackend:
    """Loads and instantiates the specified backend."""
    backend_name = backend_name.lower()
    timeout_config = {
        "primary_api_timeout": config.PRIMARY_API_TIMEOUT,
        # Add backend-specific timeouts if needed, e.g., kobold's fallback
        "fallback_api_timeout": 10 # Example for Kobold, ignored by LlamaCpp
    }

    if backend_name == "koboldcpp":
        from backends.kobold_backend import KoboldBackend
        print(f"Loading KoboldCpp backend (Script: {config.KOBOLDCPP_SCRIPT_PATH})")
        if not config.KOBOLDCPP_SCRIPT_PATH.exists():
             print(f"[ERROR] KoboldCpp script not found at: {config.KOBOLDCPP_SCRIPT_PATH}")
             sys.exit(1)
        return KoboldBackend(config.DEFAULT_HOST, config.DEFAULT_PORT, config.KOBOLDCPP_DEFAULT_ARGS, timeout_config)
    elif backend_name == "llamacpp":
        from backends.llama_cpp_backend import LlamaCppBackend
        print(f"Loading Llama.cpp backend (Server: {config.LLAMA_CPP_SERVER_PATH})")
        if not config.LLAMA_CPP_SERVER_PATH.exists():
             print(f"[ERROR] llama-server executable not found at: {config.LLAMA_CPP_SERVER_PATH}")
             sys.exit(1)
        return LlamaCppBackend(config.DEFAULT_HOST, config.DEFAULT_PORT, config.LLAMA_CPP_DEFAULT_ARGS, timeout_config)
    else:
        raise ValueError(f"Unsupported backend: {backend_name}. Choose 'koboldcpp' or 'llamacpp'.")

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description="Run LLM Benchmarks using different backends.")
parser.add_argument(
    "--backend",
    type=str,
    required=True,
    choices=["koboldcpp", "llamacpp"],
    help="The LLM backend to use."
)
parser.add_argument(
    "--port",
    type=int,
    default=config.DEFAULT_PORT,
    help=f"Port for the backend server (default: {config.DEFAULT_PORT})."
)
parser.add_argument(
    "--host",
    type=str,
    default=config.DEFAULT_HOST,
    help=f"Host IP for the backend server (default: {config.DEFAULT_HOST})."
)
# Add other arguments if needed (e.g., override common gen params)

args = parser.parse_args()

# --- Main Execution ---
print_with_timestamp(f"Starting Benchmark Automation (Backend: {args.backend})...", config.MAIN_START_TIME)

# --- Dynamic Discovery ---
print_with_timestamp(f"Scanning for models in: {config.MODEL_DIR}", config.MAIN_START_TIME)
potential_paths = config.MODEL_DIR.glob('*.gguf')
filtered_model_paths = []
for path in potential_paths:
    model_filename = path.name
    if not path.is_file(): continue
    if model_filename.startswith('.') or model_filename.startswith('._'):
        # print(f"  [INFO] Skipping hidden/system file: {model_filename}")
        continue
    # --- Add any specific model filename filtering here if needed ---
    # if 'exclude_this' in model_filename.lower(): continue

    try:
        file_size = path.stat().st_size
        if config.MAX_SIZE_BYTES is not None and file_size > config.MAX_SIZE_BYTES:
            print(f"  [INFO] Skipping model: {model_filename} (Size {file_size / (1024**3):.2f} GiB > {config.MAX_SIZE_BYTES / (1024**3):.0f} GiB)")
            continue
        if config.MIN_SIZE_BYTES is not None and file_size < config.MIN_SIZE_BYTES:
            print(f"  [INFO] Skipping model: {model_filename} (Size {file_size / (1024**3):.2f} GiB < {config.MIN_SIZE_BYTES / (1024**3):.0f} GiB)")
            continue
    except OSError as e:
        print(f"  [WARN] Cannot access file stats for {model_filename} (skipped): {e}")
        continue
    filtered_model_paths.append(path)

model_paths = sorted(filtered_model_paths)

if not model_paths:
    print(f"[ERROR] No matching *.gguf models found in {config.MODEL_DIR} based on filters. Exiting.")
    sys.exit(1)
print(f"Found {len(model_paths)} models to process.")

print(f"Scanning for prompts in: {config.PROMPT_DIR}")
potential_prompt_paths = config.PROMPT_DIR.glob('*.md')
prompt_paths = []
for path in potential_prompt_paths:
     if not path.is_file(): continue
     prompt_filename = path.name
     if prompt_filename.startswith('.') or prompt_filename.startswith('._'):
         # print(f"  [INFO] Skipping hidden/system prompt file: {prompt_filename}")
         continue
     prompt_paths.append(path)

prompt_paths = sorted(prompt_paths)

if not prompt_paths:
    print(f"[ERROR] No *.md prompts found in {config.PROMPT_DIR}. Exiting.")
    sys.exit(1)
print(f"Found {len(prompt_paths)} prompts.")

# Create results directory
config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
print(f"Results will be saved in: {config.RESULTS_DIR}")
print("-" * 30)

# --- Load selected backend ---
try:
    backend = load_backend(args.backend)
    backend.port = args.port # Override default port/host if provided
    backend.host = args.host
except (ValueError, SystemExit) as e:
    print(f"[FATAL] {e}")
    sys.exit(1)

# --- Signal Handling ---
original_sigint_handler = signal.getsignal(signal.SIGINT)

def signal_handler(sig, frame):
    print("\nCtrl+C detected. Shutting down backend process if running...")
    backend.stop_server() # Use backend's stop method
    print("Exiting benchmark script.")
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
    model_stem = model_path.stem

    print_with_timestamp(f"\n--- Evaluating Model {model_idx+1}/{len(model_paths)}: {model_filename} ---", config.MAIN_START_TIME)

    # --- MODEL SKIP CHECK ---
    existing_output_count = 0
    for prompt_path_check in prompt_paths:
        prompt_stem_check = prompt_path_check.stem
        if check_if_output_exists(config.RESULTS_DIR, model_stem, prompt_stem_check):
            existing_output_count += 1

    if existing_output_count == len(prompt_paths):
        print_with_timestamp(f"  [SKIP] All {len(prompt_paths)} prompt outputs already exist for model '{model_filename}'. Skipping model.", config.MAIN_START_TIME)
        skipped_models_count += 1
        run_counter += len(prompt_paths)
        continue
    elif existing_output_count > 0:
         print_with_timestamp(f"  [INFO] Found {existing_output_count}/{len(prompt_paths)} existing outputs for model '{model_filename}'. Will skip individual prompts.", config.MAIN_START_TIME)
    # --- END MODEL SKIP CHECK ---

    print_with_timestamp(f"--- Starting Model {model_idx+1-skipped_models_count}/{len(model_paths)-skipped_models_count} (Actual): {model_filename} ---", model_start_time)

    if not model_path.exists():
        print(f"  [ERROR] Model file check failed: {model_path}. Skipping model.")
        for prompt_path_fail in prompt_paths:
            if not check_if_output_exists(config.RESULTS_DIR, model_stem, prompt_path_fail.stem):
                 run_counter += 1
                 failed_runs.append((model_filename, prompt_path_fail.name, "Model file not found before launch"))
        continue

    server_started_successfully = False
    prompts_processed_this_model = 0

    try:
        # Start the backend server for this model
        if not backend.start_server(model_path):
             # Error already printed by start_server
             # Try to get more stderr info if possible
             stderr_output = backend.get_process_stderr() # Assumes backend provides method
             print(f"  {backend.get_backend_name()} stderr glimpse on start failure:\n---\n{stderr_output[:1000]}...\n---") # Show first 1KB

             for prompt_path_fail in prompt_paths:
                 if not check_if_output_exists(config.RESULTS_DIR, model_stem, prompt_path_fail.stem):
                     run_counter += 1
                     failed_runs.append((model_filename, prompt_path_fail.name, "Server process failed to start"))
             # No 'continue' here, finally block handles cleanup/cooldown
        else:
            # Wait for the server to be ready using backend's check
            if not wait_for_server(backend, config.SERVER_STARTUP_WAIT):
                print(f"  [ERROR] Server failed to become ready for model {model_filename}. Shutting down server.")
                backend.stop_server() # Ensure server is stopped if it failed readiness check
                stderr_output_post_wait = backend.get_process_stderr()
                print(f"  {backend.get_backend_name()} stderr glimpse after wait failure:\n---\n{stderr_output_post_wait[:1000]}...\n---")

                for prompt_path_fail in prompt_paths:
                    if not check_if_output_exists(config.RESULTS_DIR, model_stem, prompt_path_fail.stem):
                        run_counter += 1
                        failed_runs.append((model_filename, prompt_path_fail.name, "Server failed readiness check"))
                # No 'continue' here, finally block handles cooldown
            else:
                server_started_successfully = True # Server is up, proceed

        # --- Inner Loop: Iterate through prompts ---
        if server_started_successfully:
            for prompt_idx, prompt_path in enumerate(prompt_paths):
                prompt_filename = prompt_path.name
                prompt_stem = prompt_path.stem
                prompts_processed_this_model += 1

                # --- PROMPT SKIP CHECK ---
                if check_if_output_exists(config.RESULTS_DIR, model_stem, prompt_stem):
                    if prompts_processed_this_model == existing_output_count + 1:
                         print_with_timestamp(f"\n  Skipping prompts for {model_filename} where output exists...", model_start_time)
                    print(f"    [SKIP] Output for Prompt '{prompt_filename}' already exists.")
                    run_counter += 1
                    skipped_prompts_count += 1
                    continue
                # --- END PROMPT SKIP CHECK ---

                run_counter += 1
                print_with_timestamp(f"\n  [{run_counter}/{total_combinations}] Running Prompt: {prompt_filename} ({prompt_idx+1}/{len(prompt_paths)})", model_start_time)

                # Read prompt content
                try:
                    raw_bytes = prompt_path.read_bytes()
                    if raw_bytes.startswith(b'\xef\xbb\xbf'): raw_bytes = raw_bytes[3:]
                    benchmark_prompt = raw_bytes.decode('utf-8', errors='replace').strip()
                    benchmark_prompt = ''.join(c for c in benchmark_prompt if c.isprintable() or c.isspace())

                    if not benchmark_prompt:
                        print(f"    [WARN] Prompt file {prompt_path} is empty or invalid. Skipping.")
                        failed_runs.append((model_filename, prompt_filename, "Prompt file empty or invalid"))
                        continue

                    # Apply model-specific prompt filtering (potentially backend-agnostic part)
                    filtered_prompt = backend.apply_model_prompt_filter(model_filename, benchmark_prompt)

                except Exception as e:
                    print(f"    [ERROR] Failed to read/process prompt file {prompt_path}: {e}. Skipping prompt.")
                    failed_runs.append((model_filename, prompt_filename, f"Failed to read/process prompt: {e}"))
                    continue

                # Get generation parameters (start with common, let backend override/map)
                generation_params = config.COMMON_GEN_PARAMS.copy()
                # Add any specific overrides for this run if needed later

                # --- API Call via Backend ---
                generated_text, generation_time, success, was_fallback = backend.generate(
                    filtered_prompt,
                    generation_params,
                    model_filename # Pass model name for potential filtering inside backend
                )

                # --- Processing Logic ---
                if success and generated_text is not None:
                    print("    Processing response data...")
                    if was_fallback: # Check if backend indicated fallback was used
                        print("      (Using data obtained from fallback mechanism)")

                    if generated_text: # Check if not empty string after strip
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        safe_model_stem = model_stem.replace('/', '_').replace('\\', '_').replace(':', '_')
                        safe_prompt_stem = prompt_stem.replace('/', '_').replace('\\', '_').replace(':', '_')
                        suffix = '_fallback' if was_fallback else ''
                        output_filename = f"{safe_model_stem}_{safe_prompt_stem}_{timestamp}{suffix}.md"
                        output_path = config.RESULTS_DIR / output_filename
                        # Add generation time as comment
                        output_text = generated_text + f"\n\n<!-- Benchmark Info -->\n<!-- Backend: {backend.get_backend_name()} -->\n<!-- Model: {model_filename} -->\n<!-- Prompt: {prompt_filename} -->\n<!-- Generation Time: {generation_time:.2f}s -->\n<!-- Fallback Used: {was_fallback} -->"

                        try:
                            with open(output_path, 'w', encoding='utf-8') as f_out:
                                f_out.write(output_text)
                            print(f"    Result saved to: {output_path}")
                        except IOError as e:
                            print(f"    [ERROR] Failed to write output file {output_path}: {e}")
                            if not any(entry[0] == model_filename and entry[1] == prompt_filename for entry in failed_runs):
                                 failed_runs.append((model_filename, prompt_filename, f"Failed to write output: {e}"))
                    else: # Generated text was empty string
                         print("    [INFO] Backend returned empty text. Nothing to save.")
                         failure_reason = "Backend returned empty text"
                         if not any(entry[0] == model_filename and entry[1] == prompt_filename for entry in failed_runs):
                              failed_runs.append((model_filename, prompt_filename, failure_reason))

                elif not success:
                    # Error should have been logged by the backend's generate method
                    print("    Skipping processing and saving due to generation failure.")
                    failure_reason = f"Generation failed (backend: {backend.get_backend_name()})"
                    # Add to failed runs if not already added by previous steps (e.g., read error)
                    if not any(entry[0] == model_filename and entry[1] == prompt_filename for entry in failed_runs):
                         failed_runs.append((model_filename, prompt_filename, failure_reason))
                # else: success is True but generated_text is None (shouldn't happen with current backend logic)

            # --- End of inner prompt loop ---
        # --- End of server_started_successfully check ---

    except Exception as model_loop_error:
        print(f"  [ERROR] An unexpected error occurred during processing for model {model_filename}: {model_loop_error}")
        import traceback
        traceback.print_exc() # Print traceback for unexpected errors
        try:
            for prompt_path_fail in prompt_paths:
                if not check_if_output_exists(config.RESULTS_DIR, model_stem, prompt_path_fail.stem):
                    if not any(f[0] == model_filename and f[1] == prompt_path_fail.name for f in failed_runs):
                         run_counter += 1
                         failed_runs.append((model_filename, prompt_path_fail.name, f"Model-level error: {model_loop_error}"))
        except Exception as fail_log_err:
             print(f"  [WARN] Additional error while logging failures after model error: {fail_log_err}")

    finally:
        # --- Shutdown Backend process for this model ---
        print_with_timestamp(f" == Finished Model Run: {model_filename} ==", model_start_time)
        backend.stop_server() # Use the backend's stop method

        # Wait before starting the next model
        if model_idx < len(model_paths) - 1:
            print(f"\nWaiting {config.SERVER_COOLDOWN_WAIT}s before next model...")
            time.sleep(config.SERVER_COOLDOWN_WAIT)
    # --- End of outer model loop ---


# Restore original signal handler
signal.signal(signal.SIGINT, original_sigint_handler)

# --- Final Summary ---
print("\n" + "="*40)
print("Benchmark Script Finished")
end_run_time = datetime.datetime.now()
print(f"Using Backend: {args.backend}")
print(f"Total elapsed time: {end_run_time - config.MAIN_START_TIME}")
print(f"Total Model/Prompt Combinations Configured: {total_combinations}")
print(f"Total Runs Processed (Attempted or Skipped): {run_counter}")
print(f"  - Models Skipped Entirely (All prompts existed): {skipped_models_count}")
print(f"  - Individual Prompts Skipped (Output existed): {skipped_prompts_count}")
# Calculate actual attempts more carefully
total_possible_runs_for_skipped_models = skipped_models_count * len(prompt_paths)
actual_attempts = run_counter - total_possible_runs_for_skipped_models - skipped_prompts_count
successful_runs = max(0, actual_attempts - len(failed_runs)) # Ensure non-negative
print(f"Successful Runs (Generated output file): {successful_runs}")
print(f"Failed Runs (Logged in summary): {len(failed_runs)}")
print(f"Results saved in directory: {config.RESULTS_DIR}")

if failed_runs:
    print("\n--- Summary of Failures ---")
    failed_runs.sort(key=lambda x: (x[0], x[1])) # Sort by model, then prompt
    for model, prompt, reason in failed_runs:
        print(f"  - Model: {model}, Prompt: {prompt}, Reason: {reason}")
print("="*40)