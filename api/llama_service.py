import subprocess
import requests
import json
from typing import Dict, Any
from config import Config

class LlamaService:
    def __init__(self, server_url: str | None = None):
        self.server_url = server_url or "http://localhost:8081"
        self.detection_binary = Config.BINARY_PATH
        self.model_path = Config.MODEL_PATH

    def _format_qwen_prompt(self, prompt: str) -> str:
        # Format prompt for Qwen instruction model
        system_msg = "You are a helpful AI assistant. Answer questions directly, accurately, and concisely."
        return f"<|im_start|>system\n{system_msg}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"

    def generate_response(self, prompt: str, max_tokens: int = 50) -> Dict[str, Any]:
        # Generate LLM response via llama-server
        # Returns: Dict with response content and metadata
        try:
            formatted_prompt = self._format_qwen_prompt(prompt)

            response = requests.post(
                f"{self.server_url}/completion",
                json={
                    "prompt": formatted_prompt,
                    "n_predict": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "repeat_penalty": 1.1,
                    "stop": ["<|im_end|>", "</s>", "\n\nUser:", "\n\nAssistant:"]
                },
                timeout=120
            )
            response.raise_for_status()
            data = response.json()

            return {
                "content": data.get("content", "").strip(),
                "tokens_prompt": data.get("tokens_evaluated", 0),
                "tokens_generated": data.get("tokens_predicted", 0),
                "generation_time": data.get("timings", {}).get("predicted_ms", 0) / 1000.0,
                "stop_reason": data.get("stop_type", "unknown")
            }

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"llama-server error: {str(e)}")

    def detect_category(self, prompt: str, response: str) -> tuple[str, dict]:
        """
        Detect OWASP category using owasp-llm-tool
        Returns: (category, metadata) - metadata includes perplexity if LLM03
        """
        try:
            # Step 1: Fast pattern-based detection (LLM01/02/04/06)
            result = subprocess.run(
                [
                    str(self.detection_binary),
                    "--skip_llm_generation",
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
            category = detection_data.get("category", "unknown")

            # Step 2: If unknown, try perplexity-based detection (LLM03)
            if category == "unknown":
                result_perplexity = subprocess.run(
                    [
                        str(self.detection_binary),
                        str(self.model_path),
                        str(prompt)
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,  # Longer timeout for model load
                    check=False
                )

                if result_perplexity.returncode == 0:
                    perplexity_data = json.loads(result_perplexity.stdout)
                    category = perplexity_data.get("category", "unknown")

                    # Return perplexity metadata if LLM03 detected
                    if category == "LLM03":
                        perplexity_value = perplexity_data.get("metadata", {}).get("perplexity")
                        return category, {"perplexity": perplexity_value}

            return category, {}

        except subprocess.TimeoutExpired:
            raise RuntimeError("Detection timeout")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid detection output: {str(e)}")

    def process_prompt(self, prompt: str, max_tokens: int = 50) -> Dict[str, Any]:
        # Full pipeline
        # 1. Generate response (fast via server)
        llm_result = self.generate_response(prompt, max_tokens)

        # 2. Detect security category (pattern + perplexity if needed)
        category, extra_metadata = self.detect_category(prompt, llm_result["content"])

        # 3: Merge results
        metadata = {
            "tokens_prompt": llm_result["tokens_prompt"],
            "tokens_generated": llm_result["tokens_generated"],
            "generation_time": llm_result["generation_time"],
            "stop_reason": llm_result["stop_reason"]
        }

        # Add perplexity if present (LLM03)
        if "perplexity" in extra_metadata:
            metadata["perplexity"] = extra_metadata["perplexity"]

        return {
            "prompt": prompt,
            "response": llm_result["content"],
            "category": category,
            "metadata": metadata
        }

