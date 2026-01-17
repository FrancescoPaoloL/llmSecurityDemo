import subprocess
import requests
import json
from typing import Dict, Any
from config import Config

class LlamaService:
    def __init__(self, server_url: str | None = None):
        self.server_url = server_url or "http://localhost:8081"
        self.detection_binary = Config.BINARY_PATH

    def generate_response(self, prompt: str, max_tokens: int = 50) -> Dict[str, Any]:
        # Generate LLM response via llama-server
        # Returns: Dict with response content and metadata
        try:
            response = requests.post(
                f"{self.server_url}/completion",
                json={
                    "prompt": prompt,
                    "n_predict": max_tokens,
                    "temperature": 0.7,
                    "stop": ["</s>", "\n\n"]
                },
                timeout=120
            )
            response.raise_for_status()
            data = response.json()

            return {
                "content": data.get("content", ""),
                "tokens_prompt": data.get("tokens_evaluated", 0),
                "tokens_generated": data.get("tokens_predicted", 0),
                "generation_time": data.get("timings", {}).get("predicted_ms", 0) / 1000.0,
                "stop_reason": data.get("stop_type", "unknown")
            }

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"llama-server error: {str(e)}")

    def detect_category(self, prompt: str, response: str) -> str:
        # detect OWASP category using owasp-llm-tool
        try:
            result = subprocess.run(
                [
                    str(self.detection_binary),
                    "--detect-only",
                    "--prompt", str(prompt),
                    "--response", str(response)
                ],
                capture_output=True,
                text=True,
                timeout=5,
                check=False
            )

            if result.returncode != 0:
                raise RuntimeError(f"Detection failed: {result.stderr}")

            detection_data = json.loads(result.stdout)
            return detection_data.get("category", "unknown")

        except subprocess.TimeoutExpired:
            raise RuntimeError("Detection timeout")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid detection output: {str(e)}")

    def process_prompt(self, prompt: str, max_tokens: int = 50) -> Dict[str, Any]:
        # make a full pipeline

        # 1. Generate response (fast via server)
        llm_result = self.generate_response(prompt, max_tokens)

        # 2. Detect security category (fast via C++ tool)
        category = self.detect_category(prompt, llm_result["content"])

        # 3: Merge results
        return {
            "prompt": prompt,
            "response": llm_result["content"],
            "category": category,
            "metadata": {
                "tokens_prompt": llm_result["tokens_prompt"],
                "tokens_generated": llm_result["tokens_generated"],
                "generation_time": llm_result["generation_time"],
                "stop_reason": llm_result["stop_reason"]
            }
        }

