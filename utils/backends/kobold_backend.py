# backends/kobold_backend.py
import time
import json
import requests
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List

from .base_backend import LLMBackend
import config # Import the shared config

class KoboldBackend(LLMBackend):

    def __init__(self, host: str, port: int, startup_args: List[str], timeout_config: Dict[str, int]):
        super().__init__(host, port, startup_args, timeout_config)
        self._api_generate_url = f"{self._api_base_url}/api/v1/generate"
        self._api_check_url = f"{self._api_base_url}/api/extra/generate/check"
        self._api_model_url = f"{self._api_base_url}/api/v1/model"
        self._fallback_timeout = timeout_config.get("fallback_api_timeout", 10) # Add specific fallback timeout

    def get_backend_name(self) -> str:
        return "koboldcpp"

    def build_start_command(self, model_path: Path) -> List[str]:
        """Construct the KoboldCpp start command."""
        # Combine default args with model-specific and connection args
        command = list(self.startup_args) # Make a copy
        command.extend(["--model", str(model_path)])
        command.extend(["--host", self.host]) # Ensure host/port are passed
        command.extend(["--port", str(self.port)])
        return command

    def is_server_ready(self) -> bool:
        """Checks if the KoboldCpp API server is responding and model is loaded."""
        try:
            response = requests.get(self._api_model_url, timeout=1)
            if response.status_code == 200:
                content = response.json()
                # Check if 'result' key exists and is not 'inactive'
                if content.get("result") and content.get("result").lower() != "inactive":
                    return True
            return False
        except requests.exceptions.RequestException:
            return False
        except (json.JSONDecodeError, AttributeError, KeyError):
             # Handle cases where response is not JSON or lacks expected keys during startup
             return False
        except Exception as e:
            print(f"  [WARN] Error checking Kobold server readiness: {e}")
            return False

    def get_default_generation_params(self) -> Dict[str, Any]:
        """Returns KoboldCpp specific default parameters."""
        # Start with common params and add/override Kobold specific ones
        params = config.COMMON_GEN_PARAMS.copy()
        params.update({
            "n": 1,
            "max_context_length": 16384, # Kobold specific? Or use ctx-size arg?
            "max_length": params.get("max_tokens", 1024), # Map common name
            "rep_pen": params.get("repeat_penalty", 1.1), # Map common name
            "temperature": params.get("temperature", 0.7),
            "top_p": params.get("top_p", 0.95),
            "top_k": params.get("top_k", 40),
            "top_a": 0,
            "typical": 1,
            "tfs": 1,
            "rep_pen_range": 160,
            "rep_pen_slope": 0.7,
            "sampler_order": [6, 0, 1, 3, 4, 2, 5],
            "memory": "",
            "trim_stop": True,
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
            "quiet": True,
            "stop_sequence": ["{{[INPUT]}}", "{{[OUTPUT]}}"], # Kobold default stops
            "use_default_badwordsids": False,
            "bypass_eos": False,
            "seed": params.get("seed", -1) # Map common name
            # Remove common keys already mapped if necessary
        })
        # Remove keys handled by mapping if they exist in the original common set
        params.pop("max_tokens", None)
        params.pop("repeat_penalty", None)
        # params.pop("seed", None) # Keep seed

        return params

    def apply_model_payload_filter(self, model_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Applies model-specific payload adjustments for KoboldCpp."""
        if 'qwen' in model_name.lower():
            print(f"    Applying Qwen filter to Kobold payload.")
            payload["temperature"] = 0.4
            payload["top_k"] = 30

        if 'deephermes' in model_name.lower():
            print(f"    Applying DeepHermes filter to Kobold payload.")
            systemthinkprompt = "You are a deep thinking AI, you may use extremely long chains of thought to deeply consider the problem and deliberate with yourself via systematic reasoning processes to help come to a correct solution prior to answering. You should enclose your thoughts and internal monologue inside <think> </think> tags, and then provide your solution or response to the problem.\n"
            system = "<|start_header_id|>system<|end_header_id|>\n\n"
            user = "<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n"
            assistant = "<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"

            # Assume payload['prompt'] already has the base prompt formatted like "{{[INPUT]}} {prompt} {{{{[OUTPUT]}}}}"
            base_prompt_content = payload["prompt"].split("{{{[INPUT]}}}")[1].split("{{{[OUTPUT]}}}}")[0].strip()
            payload["prompt"] = f"{user}{base_prompt_content}{assistant}" # Apply ChatML structure within Kobold's prompt/memory
            payload["memory"] = system + systemthinkprompt
            payload["stop_sequence"] = ["<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n", "<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"]

        if 'reka-flash' in model_name.lower():
            print(f"    Applying Reka-Flash filter to Kobold payload.")
            # Assume payload['prompt'] already has the base prompt formatted like "{{[INPUT]}} {prompt} {{{{[OUTPUT]}}}}"
            base_prompt_content = payload["prompt"].split("{{{[INPUT]}}}")[1].split("{{{[OUTPUT]}}}}")[0].strip()
            payload["prompt"] = f"human:\n{base_prompt_content}<sep> assistant:"
            payload["stop_sequence"] = ["<sep> human:", "human:"]

        return payload

    def generate(self, prompt: str, generation_params: Dict[str, Any], model_name: str) -> Tuple[Optional[str], float, bool, bool]:
        """Sends generation request to KoboldCpp, handles fallback."""
        payload = self.get_default_generation_params()
        payload.update(generation_params) # Override defaults with run-specific params

        # Format the prompt using Kobold's template structure
        # The base prompt filter might have already modified the 'prompt' content
        payload["prompt"] = "{{{[INPUT]}}} " + prompt + " {{{{[OUTPUT]}}}}"

        # Apply model-specific payload filtering *after* base prompt is set
        payload = self.apply_model_payload_filter(model_name, payload)

        # Add a unique genkey
        timestamp_key = time.strftime("%Y%m%d%H%M%S")
        payload["genkey"] = f"KCPP_BENCH_{model_name[:10]}_{timestamp_key}"

        final_api_response = None
        generation_time = 0.0
        request_successful = False
        is_fallback = False
        primary_timeout = self.timeout_config.get("primary_api_timeout", 600)

        try:
            print(f"    Sending Kobold API request (gen_key={payload['genkey']}, timeout={primary_timeout}s)...")
            start_req_time = time.time()
            response = requests.post(self._api_generate_url, json=payload, timeout=primary_timeout)
            end_req_time = time.time()
            generation_time = end_req_time - start_req_time
            response.raise_for_status()
            final_api_response = response.json()
            request_successful = True
            print(f"    Kobold primary generation successful (took {generation_time:.2f}s).")

        except requests.exceptions.Timeout:
            end_req_time = time.time()
            generation_time = end_req_time - start_req_time # Time until timeout
            print(f"    [WARNING] Kobold primary API request timed out after {generation_time:.2f}s. Attempting fallback...")
            is_fallback = True
            grab_payload = {"genkey": payload["genkey"]}

            try:
                print(f"    Sending Kobold fallback request (timeout={self._fallback_timeout}s)...")
                start_grab_time = time.time()
                grab_response = requests.post(self._api_check_url, json=grab_payload, timeout=self._fallback_timeout)
                end_grab_time = time.time()
                print(f"    Kobold fallback request attempt took {end_grab_time - start_grab_time:.2f}s.")
                grab_response.raise_for_status()
                final_api_response = grab_response.json()
                request_successful = True
                print(f"    Kobold fallback data retrieval successful.")

            except requests.exceptions.RequestException as grab_e:
                print(f"    [ERROR] Kobold fallback request failed: {grab_e}")
                # generation_time remains time until primary timeout
                return None, generation_time, False, True # Indicate fallback attempt failed
            except Exception as grab_e_unexpected:
                 print(f"    [ERROR] Unexpected error during Kobold fallback: {grab_e_unexpected}")
                 return None, generation_time, False, True

        except requests.exceptions.RequestException as e:
            print(f"    [ERROR] Kobold primary API request failed: {e}")
            # generation_time might be 0 if connection failed instantly
            return None, generation_time, False, False # Indicate primary failure, no fallback attempted
        except Exception as e:
            print(f"    [ERROR] Unexpected error during Kobold API call/processing: {e}")
            return None, generation_time, False, False

        # --- Process successful response (primary or fallback) ---
        if request_successful and final_api_response:
            generated_text = None
            try:
                results_list = final_api_response.get("results")
                if results_list and isinstance(results_list, list) and len(results_list) > 0:
                    text_entry = results_list[0]
                    if isinstance(text_entry, dict):
                        generated_text = text_entry.get("text")

                if generated_text is None or not isinstance(generated_text, str):
                    print("    [ERROR] 'text' field not found or invalid in Kobold response.")
                    # print(f"    Response JSON: {json.dumps(final_api_response, indent=2)}") # Optional Debug
                    return None, generation_time, False, is_fallback # Failed to extract text
                else:
                    print(f"    Kobold text successfully extracted ({len(generated_text)} chars).")
                    return generated_text.strip(), generation_time, True, is_fallback

            except (AttributeError, KeyError, IndexError, TypeError) as extract_err:
                print(f"    [ERROR] Failed to extract text from Kobold response: {extract_err}")
                # print(f"    Response JSON: {json.dumps(final_api_response, indent=2)}") # Optional Debug
                return None, generation_time, False, is_fallback

        # Should not be reached if logic is correct, but as a safeguard:
        return None, generation_time, False, is_fallback