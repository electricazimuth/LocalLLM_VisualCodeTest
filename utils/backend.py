# utils/backend.py
import subprocess
import requests
import time
import json
import signal
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List

class LLMBackend(ABC):
    def __init__(self, config_loader, host: str, port: int):
        self.config_loader = config_loader
        self.host = host
        self.port = port
        self.timeout_config = {
            "primary": config_loader.server_config.get('primary_timeout', 600),
            "fallback": config_loader.server_config.get('fallback_timeout', 10)
        }
        self._process: Optional[subprocess.Popen] = None
        self._api_base_url = f"http://{self.host}:{self.port}"

    def start_server(self, model_path: Path, model_config: Dict[str, Any]) -> bool:
        """Starts the server subprocess."""
        if self._process and self._process.poll() is None:
            print(f"  [WARN] Server already running (PID: {self._process.pid})")
            return False

        # Get backend-specific config (path to binary, basic args)
        backend_cfg = self.config_loader.get_backend_config(self.get_backend_name())
        bin_path = str(backend_cfg['bin_path'])
        
        # Determine command prefix (e.g. python3 vs direct executable)
        cmd = []
        if backend_cfg.get('type') == 'python':
            cmd = ["python3", bin_path]
        else:
            cmd = [bin_path]

        # Add generic backend args (from yaml: backends.<name>.startup_args)
        cmd.extend(backend_cfg.get('startup_args', []))

        # Add Host/Port
        cmd.extend(["--host", self.host, "--port", str(self.port)])

        # Add Model Path (Backend specific flag)
        cmd.extend(self.get_model_flag(model_path))

        # Add Model-Specific overrides (from yaml: models.<pattern>.startup_args)
        # These are appended last to override previous defaults in most CLIs
        cmd.extend(model_config.get("startup_args", []))

        print(f"  Running command: {' '.join(cmd)}")
        
        try:
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            return True
        except Exception as e:
            print(f"  [ERROR] Failed to start process: {e}")
            self._process = None
            return False

    def stop_server(self):
        """Stops the server gracefully."""
        if self._process:
            print(f"  Stopping {self.get_backend_name()} (PID: {self._process.pid})...")
            try:
                self._process.send_signal(signal.SIGINT)
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()
            self._process = None

    def get_process_stderr(self) -> str:
        if self._process and self._process.stderr:
            # Note: This reads strictly what's currently in buffer. 
            # For robust logging, you might want a thread reading this.
            return self._process.stderr.read() or ""
        return ""

    @abstractmethod
    def get_backend_name(self) -> str:
        pass

    @abstractmethod
    def get_model_flag(self, model_path: Path) -> List[str]:
        """Returns the flag used to specify model path (e.g. ['-m', path] or ['--model', path])"""
        pass

    @abstractmethod
    def is_server_ready(self) -> bool:
        pass

    @abstractmethod
    def generate(self, prompt: str, generation_params: Dict[str, Any], prompt_template: Dict[str, Any]) -> Tuple[Optional[str], float, bool, bool]:
        pass

# --- IMPL: KoboldCpp ---

class KoboldBackend(LLMBackend):
    def get_backend_name(self) -> str:
        return "koboldcpp"

    def get_model_flag(self, model_path: Path) -> List[str]:
        return ["--model", str(model_path)]

    def is_server_ready(self) -> bool:
        try:
            # Kobold check URL
            res = requests.get(f"{self._api_base_url}/api/v1/model", timeout=1)
            if res.status_code == 200:
                data = res.json()
                return data.get("result", "").lower() != "inactive"
        except:
            return False
        return False

    def _map_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Maps generic YAML config to Kobold API specific keys."""
        p = params.copy()
        # Mappings
        if "max_tokens" in p: p["max_length"] = p.pop("max_tokens")
        if "repeat_penalty" in p: p["rep_pen"] = p.pop("repeat_penalty")
        if "stop" in p: p["stop_sequence"] = p.pop("stop")
        
        # Ensure generic defaults
        p.setdefault("quiet", True)
        return p

    def generate(self, prompt: str, generation_params: Dict[str, Any], prompt_template: Dict[str, Any]) -> Tuple[Optional[str], float, bool, bool]:
        # 1. Apply Template
        # Kobold typically handles raw strings, but if you have a system prompt in YAML, handle it here
        sys = prompt_template.get("system_prompt", "")
        append = prompt_template.get("append_text", "")
        full_prompt = f"{sys}\n{prompt}\n{append}".strip()

        # 2. Build Payload
        payload = self._map_params(generation_params)
        payload["prompt"] = full_prompt

        # 3. Request
        url = f"{self._api_base_url}/api/v1/generate"
        start_t = time.time()
        fallback = False

        try:
            resp = requests.post(url, json=payload, timeout=self.timeout_config['primary'])
            resp.raise_for_status()
            data = resp.json()
            
            text = data['results'][0]['text']
            return text.strip(), time.time() - start_t, True, False

        except requests.exceptions.Timeout:
            print("  [WARN] Primary timeout, attempting Kobold fallback/check...")
            fallback = True
            # Implement Kobold specific "check" endpoint logic if needed here
            # For brevity, returning None, but you can paste your check_url logic here
            return None, time.time() - start_t, False, True
        except Exception as e:
            print(f"  [ERROR] Gen failed: {e}")
            return None, time.time() - start_t, False, False

# --- IMPL: LlamaCpp ---

class LlamaCppBackend(LLMBackend):
    def get_backend_name(self) -> str:
        return "llamacpp"

    def get_model_flag(self, model_path: Path) -> List[str]:
        return ["-m", str(model_path)]

    def is_server_ready(self) -> bool:
        try:
            res = requests.get(f"{self._api_base_url}/health", timeout=1)
            return res.status_code == 200 and res.json().get("status") == "ok"
        except:
            return False

    def generate(self, prompt: str, generation_params: Dict[str, Any], prompt_template: Dict[str, Any]) -> Tuple[Optional[str], float, bool, bool]:
        # 1. Apply Template (OpenAI Chat Format)
        messages = []
        if prompt_template.get("system_prompt"):
            messages.append({"role": "system", "content": prompt_template["system_prompt"]})
        
        user_text = prompt + prompt_template.get("append_text", "")
        messages.append({"role": "user", "content": user_text})

        # 2. Build Payload
        payload = generation_params.copy()
        payload["messages"] = messages
        # Llama.cpp OAI compatible endpoint handles params like 'temperature' natively.
        # Just ensure 'max_tokens' is present.
        
        # 3. Request
        url = f"{self._api_base_url}/v1/chat/completions"
        start_t = time.time()
        
        try:
            # Non-streaming for simplicity in this example, 
            # but you can copy your streaming logic back in if desired.
            resp = requests.post(url, json=payload, timeout=self.timeout_config['primary'])
            resp.raise_for_status()
            data = resp.json()
            
            text = data['choices'][0]['message']['content']
            return text.strip(), time.time() - start_t, True, False
            
        except Exception as e:
            print(f"  [ERROR] Gen failed: {e}")
            return None, time.time() - start_t, False, False