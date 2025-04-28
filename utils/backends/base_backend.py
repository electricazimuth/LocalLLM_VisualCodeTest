# backends/base_backend.py
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
import datetime
from typing import Tuple, Dict, Any, Optional, List

class LLMBackend(ABC):
    """Abstract Base Class for LLM Backends."""

    def __init__(self, host: str, port: int, startup_args: List[str], timeout_config: Dict[str, int]):
        self.host = host
        self.port = port
        self.startup_args = startup_args # Base args, model path added later
        self.timeout_config = timeout_config
        self._process: Optional[subprocess.Popen] = None
        self._model_path: Optional[Path] = None
        self._api_base_url = f"http://{self.host}:{self.port}"

    @abstractmethod
    def get_backend_name(self) -> str:
        """Return the name of the backend (e.g., 'koboldcpp', 'llamacpp')."""
        pass

    @abstractmethod
    def build_start_command(self, model_path: Path) -> List[str]:
        """Construct the full command list to start the server."""
        pass

    def start_server(self, model_path: Path) -> bool:
        """Starts the backend server process."""
        if self._process and self._process.poll() is None:
            print(f"  [WARN] Server process already running (PID: {self._process.pid}).")
            return False # Or maybe stop existing one first?

        self._model_path = model_path
        command = self.build_start_command(model_path)
        print(f"  Running command: {' '.join(command)}")
        try:
            # Capture stderr for debugging startup issues
            self._process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE, # Capture stderr
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            print(f"  {self.get_backend_name()} process started (PID: {self._process.pid}).")
            return True
        except Exception as e:
            print(f"  [ERROR] Failed to start {self.get_backend_name()} process: {e}")
            self._process = None
            return False

    def stop_server(self) -> None:
        """Stops the backend server process gracefully."""
        if self._process and self._process.poll() is None:
            print(f"\n  Terminating {self.get_backend_name()} process (PID: {self._process.pid})...")
            import signal
            import time
            # Try SIGINT first
            self._process.send_signal(signal.SIGINT)
            try:
                self._process.wait(timeout=10)
                print(f"  {self.get_backend_name()} process terminated (SIGINT).")
            except subprocess.TimeoutExpired:
                print(f"  {self.get_backend_name()} did not respond to SIGINT, sending SIGTERM...")
                self._process.terminate()
                try:
                    self._process.wait(timeout=5)
                    print(f"  {self.get_backend_name()} process terminated (SIGTERM).")
                except subprocess.TimeoutExpired:
                    print(f"  {self.get_backend_name()} did not respond to SIGTERM, killing (SIGKILL)...")
                    self._process.kill()
                    self._process.wait()
                    print(f"  {self.get_backend_name()} process killed.")
            # Ensure stderr is closed
            if self._process.stderr:
                try:
                    self._process.stderr.close()
                except Exception:
                    pass # Ignore errors closing already closed streams
        elif self._process:
            print(f"  {self.get_backend_name()} process (PID: {self._process.pid}) already terminated.")
        else:
            print(f"  No active {self.get_backend_name()} process found to terminate.")
        self._process = None
        self._model_path = None # Clear model path on stop

    def get_process_stderr(self) -> str:
        """Reads the captured stderr from the server process."""
        if self._process and self._process.stderr:
            try:
                # Non-blocking read might be better, but simple read for now
                return self._process.stderr.read()
            except Exception as e:
                return f"[Error reading stderr: {e}]"
        return "[Stderr not available or process not running]"


    @abstractmethod
    def is_server_ready(self) -> bool:
        """Checks if the backend server is up and ready to process requests."""
        pass

    @abstractmethod
    def generate(self, prompt: str, generation_params: Dict[str, Any], model_name: str) -> Tuple[Optional[str], float, bool, bool]:
        """
        Sends a generation request to the backend.

        Args:
            prompt (str): The user prompt.
            generation_params (Dict[str, Any]): Common generation parameters.
            model_name (str): The name of the model file being used.

        Returns:
            Tuple[Optional[str], float, bool, bool]:
                - Generated text (str) or None if failed.
                - Generation time (float) in seconds.
                - Success status (bool).
                - Was fallback used (bool) - specific to some backends.
        """
        pass

    @abstractmethod
    def get_default_generation_params(self) -> Dict[str, Any]:
        """Returns the default generation parameters specific to this backend."""
        pass

    # --- Model Specific Filters ---
    # Keep these methods, but implementations will adapt filters to specific backend payloads/prompts
    @abstractmethod
    def apply_model_payload_filter(self, model_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Applies model-specific adjustments to the API request payload."""
        pass

    def apply_model_prompt_filter(self, model_name: str, prompt: str) -> str:
        """
        Applies model-specific additions/modifications to the prompt string.
        This can often be generic, but can be overridden if needed.
        """
        if 'qwq' in model_name.lower(): # Example filter
            print(f"    Applying 'qwq' filter to prompt.")
            prompt += "\nThink step by step but only keep a minimum draft of each thinking step, with 5 words at most. Be concise. Think concisely"
        # Add other generally applicable prompt filters here if desired
        return prompt