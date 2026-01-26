# utils/config_loader.py
import yaml
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

class ConfigLoader:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path).resolve()
        if not self.config_path.exists():
            # Fallback for running from utils dir
            self.config_path = Path("../config.yaml").resolve()
            
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found at {config_path}")

        with open(self.config_path, 'r') as f:
            self._data = yaml.safe_load(f)

        self._expand_paths()

    def _expand_paths(self):
        """Expands ~ in paths."""
        paths = self._data.get('paths', {})
        for key, val in paths.items():
            paths[key] = Path(val).expanduser().resolve()
        
        # Expand backend paths
        for backend in self._data.get('backends', {}).values():
            if 'bin_path' in backend:
                backend['bin_path'] = Path(backend['bin_path']).expanduser().resolve()

    # --- Accessors ---
    
    @property
    def paths(self):
        return self._data.get('paths', {})

    @property
    def server_config(self):
        return self._data.get('server', {})

    @property
    def default_gen_params(self) -> Dict[str, Any]:
        return self._data.get('default_generation_params', {}).copy()

    def get_backend_config(self, backend_name: str) -> Dict[str, Any]:
        backends = self._data.get('backends', {})
        if backend_name not in backends:
            raise ValueError(f"Backend '{backend_name}' not defined in config.yaml")
        return backends[backend_name]

    def get_model_config(self, model_filename: str) -> Dict[str, Any]:
        """
        Iterates through the 'models' list in yaml. 
        Returns a merged configuration (startup args, gen params) for the matching model.
        """
        model_filename_lower = model_filename.lower()
        
        # Default return structure
        result = {
            "startup_args": [],
            "generation_params": self.default_gen_params,
            "prompt_template": {}
        }

        # Find match
        matched_rule = None
        for rule in self._data.get('models', []):
            pattern = rule.get('pattern', '').lower()
            match_all = rule.get('match_all', [])
            
            # Check primary pattern
            if pattern and pattern in model_filename_lower:
                # Check secondary requirements if they exist
                if match_all:
                    if all(term.lower() in model_filename_lower for term in match_all):
                        matched_rule = rule
                        break
                else:
                    matched_rule = rule
                    break

        if matched_rule:
            # Override/Append Startup Args
            # Note: This simply extends the list. 
            # If you need to replace specific default args (like -ngl), 
            # complex logic is needed, or just define the FULL list in YAML.
            result["startup_args"] = matched_rule.get("startup_args", [])

            # Merge Generation Params
            overrides = matched_rule.get("generation_params", {})
            result["generation_params"].update(overrides)

            # Prompt Templates
            result["prompt_template"] = matched_rule.get("prompt_template", {})
            
        return result

# Singleton instance for easy import, or instantiate in main
# config = ConfigLoader() 