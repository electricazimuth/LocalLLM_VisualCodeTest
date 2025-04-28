# backends/llama_cpp_backend.py
import time
import json
import requests
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List

from .base_backend import LLMBackend
import config # Import the shared config

class LlamaCppBackend(LLMBackend):

    def __init__(self, host: str, port: int, startup_args: List[str], timeout_config: Dict[str, int]):
        super().__init__(host, port, startup_args, timeout_config)
        # Change endpoint to the OpenAI compatible chat completions one
        self._api_chat_completions_url = f"{self._api_base_url}/v1/chat/completions"
        self._api_health_url = f"{self._api_base_url}/health"
        # We might need the models endpoint if we want to verify the model name later
        self._api_models_url = f"{self._api_base_url}/v1/models"

    def get_backend_name(self) -> str:
        return "llamacpp"

    def build_start_command(self, model_path: Path) -> List[str]:
        """Construct the llama-server start command."""
        command = list(self.startup_args) # Make a copy
        command.extend(["-m", str(model_path)])
        command.extend(["--host", self.host])
        command.extend(["--port", str(self.port)])
        # Ensure essential args like ctx-size and ngl are present if not overridden
        # (This logic remains useful)
        if "--ctx-size" not in " ".join(self.startup_args):
             command.extend(["--ctx-size", "16384"]) # Default if not in base args
        if "-ngl" not in " ".join(self.startup_args) and "--n-gpu-layers" not in " ".join(self.startup_args):
             command.extend(["-ngl", "99"]) # Default if not in base args

        # Explicitly enable OpenAI API endpoints if not default?
        # Usually enabled by default, but good practice to be aware
        # command.extend(["--api-endpoints", "/v1/chat/completions,/health,/v1/models"]) # Example

        return command

    def is_server_ready(self) -> bool:
        """Checks if the Llama.cpp server is healthy via /health."""
        # Consider adding a check to /v1/models as well, although /health is usually sufficient
        try:
            response = requests.get(self._api_health_url, timeout=1)
            if response.status_code == 200:
                content = response.json()
                if content.get("status", "").lower() == "ok":
                    # Optional: Check if model is loaded via /v1/models
                    # try:
                    #     models_resp = requests.get(self._api_models_url, timeout=1)
                    #     if models_resp.status_code == 200 and models_resp.json().get("data"):
                    #         return True
                    # except: # Ignore errors in secondary check
                    #     pass
                    return True # Primary health check passed
            return False
        except requests.exceptions.RequestException:
            return False
        except (json.JSONDecodeError, AttributeError, KeyError):
            return False
        except Exception as e:
            print(f"  [WARN] Error checking Llama.cpp server readiness: {e}")
            return False

    def get_default_generation_params(self) -> Dict[str, Any]:
        """Returns Llama.cpp /v1/chat/completions default parameters, mapped from common ones."""
        common_params = config.COMMON_GEN_PARAMS
        # Map common config names to OpenAI API parameter names
        mapped_params = {
            "model": "default-model", # This will be overridden or ignored by server usually
            "messages": [],           # Placeholder, filled in generate()
            "max_tokens": common_params.get("max_tokens", 1024),
            "temperature": common_params.get("temperature", 0.7),
            "top_p": common_params.get("top_p", 0.9),
            # top_k is supported as an extension by llama.cpp's OAI endpoint
            "top_k": common_params.get("top_k", 40),
            "presence_penalty": common_params.get("presence_penalty", 0.0),
            "frequency_penalty": common_params.get("frequency_penalty", 0.0),
            # Map repeat_penalty to presence_penalty if defined in common, otherwise use specific penalties
            # "presence_penalty": common_params.get("repeat_penalty", common_params.get("presence_penalty", 0.0)),
            "seed": common_params.get("seed", -1),
            "stop": common_params.get("stop", []),
            "stream": False, # Benchmarking typically doesn't use streaming
            # "logit_bias": {}, # OAI format is different: {"token_id": bias_value}
            # "n": 1, # Number of choices, usually 1 for benchmarks
            # Add other supported OAI params if needed, e.g., logprobs, user
        }
        # Ensure max_tokens is not 0, as 0 might be invalid for OAI max_tokens
        if mapped_params["max_tokens"] == 0:
             mapped_params["max_tokens"] = 1 # Generate at least one token

        return mapped_params

    def apply_model_payload_filter(self, model_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Applies model-specific adjustments to the OpenAI chat payload."""
        # Filters now modify the OAI payload structure (e.g., add system messages)

        # Ensure messages list exists
        if "messages" not in payload:
             payload["messages"] = []

        if 'qwen' in model_name.lower():
            print(f"    Applying Qwen filter to Llama.cpp OAI payload.")
            payload["temperature"] = 0.4
            payload["top_k"] = 30
            # Qwen often uses a system prompt, add if needed
            # payload["messages"].insert(0, {"role": "system", "content": "You are a helpful assistant."})

        if 'deephermes' in model_name.lower():
            print(f"    Applying DeepHermes filter to Llama.cpp OAI payload (adding system prompt).")
            systemthinkprompt = "You are a deep thinking AI, you may use extremely long chains of thought to deeply consider the problem and deliberate with yourself via systematic reasoning processes to help come to a correct solution prior to answering. You should enclose your thoughts and internal monologue inside <think> </think> tags, and then provide your solution or response to the problem.\n"
            # Add system prompt at the beginning of the messages list
            # Check if a system prompt already exists to avoid duplicates
            has_system = any(msg.get("role") == "system" for msg in payload["messages"])
            if not has_system:
                payload["messages"].insert(0, {"role": "system", "content": systemthinkprompt})
            # Stop sequences might be needed if the model doesn't stop naturally after templating
            # payload["stop"] = payload.get("stop", []) + ["<|im_end|>", "<|start_header_id|>user"]

        if 'reka-flash' in model_name.lower():
             print(f"    Applying Reka-Flash filter to Llama.cpp OAI payload.")
             # Adjust sampling params if needed
             # payload["temperature"] = ...
             # Reka might need specific stop tokens if not handled by template
             # payload["stop"] = payload.get("stop", []) + ["<sep> human:", "human:"]
             pass

        # Add other model-specific adjustments for the OAI payload format
        return payload

    def apply_model_prompt_filter(self, model_name: str, prompt: str) -> str:
        """
        Applies model-specific changes to the *content* of the user prompt
        before it's placed in the 'messages' structure. Less critical now
        that templating is handled by the server.
        """
        # Keep the base implementation or customize if needed
        # Example: Adding context/instructions *within* the user message
        prompt = super().apply_model_prompt_filter(model_name, prompt)
        if 'instruct' in model_name.lower() and 'user:' not in prompt.lower():
             # Basic instruction formatting if needed, though template should handle this
             # print("    Applying basic instruction formatting to prompt content.")
             # prompt = f"User: {prompt}\nAssistant:"
             pass
        return prompt


    def generate(self, prompt: str, generation_params: Dict[str, Any], model_name: str) -> Tuple[Optional[str], float, bool, bool]:
        """Sends generation request to Llama.cpp /v1/chat/completions."""

        # 1. Prepare Payload Structure
        payload = self.get_default_generation_params()
        # Override defaults with any benchmark-run-specific params provided
        payload.update(generation_params)

        # 2. Apply prompt filter to the raw prompt content
        # This modifies the user's input string before it becomes a message
        filtered_prompt_content = self.apply_model_prompt_filter(model_name, prompt)

        # 3. Create the messages list (simple user message for now)
        # Filters might add system messages later
        payload["messages"] = [{"role": "user", "content": filtered_prompt_content}]

        # 4. Apply model-specific payload filtering (can add system msgs, adjust params)
        payload = self.apply_model_payload_filter(model_name, payload)

        # --- API Call ---
        final_api_response = None
        generation_time = 0.0
        request_successful = False
        is_fallback = False # OAI endpoint has no standard fallback mechanism
        primary_timeout = self.timeout_config.get("primary_api_timeout", 600)

        try:
            print(f"    Sending Llama.cpp OAI request (timeout={primary_timeout}s)...")
            # print(f"    Payload: {json.dumps(payload, indent=2)}") # Debug payload
            start_req_time = time.time()
            response = requests.post(
                self._api_chat_completions_url,
                json=payload,
                timeout=primary_timeout,
                headers={"Content-Type": "application/json"} # Good practice
            )
            end_req_time = time.time()
            generation_time = end_req_time - start_req_time

            # Check for non-200 status codes (OAI errors)
            if response.status_code != 200:
                 print(f"    [ERROR] Llama.cpp OAI request failed with status {response.status_code}")
                 try:
                     error_info = response.json()
                     print(f"    Error details: {json.dumps(error_info, indent=2)}")
                     reason = error_info.get("error", {}).get("message", response.text[:200])
                 except json.JSONDecodeError:
                     reason = response.text[:200] # Show beginning of non-JSON error
                     print(f"    Raw error response: {reason}")
                 # Store more specific error if available
                 return None, generation_time, False, is_fallback

            final_api_response = response.json()
            request_successful = True
            # print(f"    Raw Response: {json.dumps(final_api_response, indent=2)}") # Debug full response
            print(f"    Llama.cpp OAI generation successful (took {generation_time:.2f}s).")

        except requests.exceptions.Timeout:
            end_req_time = time.time()
            generation_time = end_req_time - start_req_time # Time until timeout
            print(f"    [ERROR] Llama.cpp OAI request timed out after {generation_time:.2f}s.")
            return None, generation_time, False, is_fallback

        except requests.exceptions.RequestException as e:
            print(f"    [ERROR] Llama.cpp OAI request failed (connection/other): {e}")
            return None, generation_time, False, is_fallback
        except json.JSONDecodeError as e:
             # Should be less likely if status code check is robust, but possible
             print(f"    [ERROR] Failed to decode Llama.cpp OAI JSON response: {e}")
             print(f"    Raw response text: {response.text[:500]}")
             return None, generation_time, False, is_fallback
        except Exception as e:
            import traceback
            print(f"    [ERROR] Unexpected error during Llama.cpp OAI call/processing: {e}")
            traceback.print_exc()
            return None, generation_time, False, is_fallback

        # --- Process successful response ---
        if request_successful and final_api_response:
            generated_text = None
            try:
                # Extract text from the OAI response structure
                choices = final_api_response.get("choices")
                if choices and isinstance(choices, list) and len(choices) > 0:
                    message = choices[0].get("message")
                    if message and isinstance(message, dict):
                        generated_text = message.get("content")

                if generated_text is None or not isinstance(generated_text, str):
                    print("    [ERROR] 'content' not found in response choices[0].message.")
                    print(f"    Response JSON: {json.dumps(final_api_response, indent=2)}")
                    return None, generation_time, False, is_fallback # Failed to extract text
                else:
                    # Optional: Log token usage if needed
                    usage = final_api_response.get("usage")
                    # if usage:
                    #     print(f"      Token Usage: {usage}")

                    print(f"    Llama.cpp OAI text successfully extracted ({len(generated_text)} chars).")
                    return generated_text.strip(), generation_time, True, is_fallback

            except (AttributeError, KeyError, IndexError, TypeError) as extract_err:
                print(f"    [ERROR] Failed to extract text from Llama.cpp OAI response structure: {extract_err}")
                print(f"    Response JSON: {json.dumps(final_api_response, indent=2)}")
                return None, generation_time, False, is_fallback

        # Safeguard return
        return None, generation_time, False, is_fallback