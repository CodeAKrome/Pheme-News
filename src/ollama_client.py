import requests
import json
import base64
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Generator
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OllamaClient:
    """Python client for Ollama API"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize the client

        Args:
            base_url: Base URL of the Ollama server
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def _encode_file(self, file_path: Union[str, Path]) -> str:
        """
        Encode a file to base64 for API transmission

        Args:
            file_path: Path to the file to encode

        Returns:
            Base64 encoded file content
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf-8")

        return content

    def _is_image_file(self, file_path: Union[str, Path]) -> bool:
        """Check if file is an image based on extension"""
        image_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".webp",
            ".tiff",
            ".svg",
        }
        return Path(file_path).suffix.lower() in image_extensions

    def generate_text(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        attachments: Optional[List[Union[str, Path]]] = None,
        stream: bool = False,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        repeat_penalty: Optional[float] = None,
        seed: Optional[int] = None,
        num_predict: Optional[int] = None,
        **kwargs,
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        Generate text using Ollama

        Args:
            model: Model name to use
            prompt: The main prompt text
            system_prompt: Optional system prompt to set behavior
            attachments: List of file paths to attach (images supported)
            stream: Whether to stream the response
            temperature: Sampling temperature
            top_k: Top-k sampling parameter
            top_p: Top-p sampling parameter
            repeat_penalty: Repetition penalty
            seed: Random seed
            num_predict: Maximum number of tokens to predict
            **kwargs: Additional parameters

        Returns:
            Dictionary containing the generated text or generator for streaming
        """
        # Prepare the request payload
        payload = {"model": model, "prompt": prompt, "stream": stream}

        # Add system prompt if provided
        if system_prompt:
            payload["system"] = system_prompt

        # Add generation options
        options = {}
        if temperature is not None:
            options["temperature"] = temperature
        if top_k is not None:
            options["top_k"] = top_k
        if top_p is not None:
            options["top_p"] = top_p
        if repeat_penalty is not None:
            options["repeat_penalty"] = repeat_penalty
        if seed is not None:
            options["seed"] = seed
        if num_predict is not None:
            options["num_predict"] = num_predict

        # Add any additional options
        options.update(kwargs)

        if options:
            payload["options"] = options

        # Add image attachments if provided
        if attachments:
            images = []
            for attachment in attachments:
                try:
                    if self._is_image_file(attachment):
                        encoded_image = self._encode_file(attachment)
                        images.append(encoded_image)
                        logger.info(f"Added image attachment: {Path(attachment).name}")
                    else:
                        logger.warning(
                            f"Non-image attachment ignored: {attachment} (Ollama only supports images)"
                        )
                except Exception as e:
                    logger.error(f"Failed to encode attachment {attachment}: {e}")

            if images:
                payload["images"] = images

        try:
            # Send request to the API
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                headers={"Content-Type": "application/json"},
                stream=stream,
            )
            response.raise_for_status()

            if stream:
                return self._handle_stream_response(response)
            else:
                result = response.json()
                logger.info("Text generation completed successfully")
                return result

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        attachments: Optional[List[Union[str, Path]]] = None,
        stream: bool = False,
        temperature: Optional[float] = None,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        **kwargs,
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        Generate text using chat format

        Args:
            model: Model name to use
            messages: List of message dictionaries with 'role' and 'content'
            attachments: List of file paths to attach (images for latest message)
            stream: Whether to stream the response
            temperature: Sampling temperature
            top_k: Top-k sampling parameter
            top_p: Top-p sampling parameter
            **kwargs: Additional parameters

        Returns:
            Dictionary containing the generated response or generator for streaming
        """
        payload = {"model": model, "messages": messages, "stream": stream}

        # Add generation options
        options = {}
        if temperature is not None:
            options["temperature"] = temperature
        if top_k is not None:
            options["top_k"] = top_k
        if top_p is not None:
            options["top_p"] = top_p

        options.update(kwargs)
        if options:
            payload["options"] = options

        # Add image attachments to the last user message
        if attachments and messages:
            images = []
            for attachment in attachments:
                try:
                    if self._is_image_file(attachment):
                        encoded_image = self._encode_file(attachment)
                        images.append(encoded_image)
                        logger.info(f"Added image attachment: {Path(attachment).name}")
                    else:
                        logger.warning(f"Non-image attachment ignored: {attachment}")
                except Exception as e:
                    logger.error(f"Failed to encode attachment {attachment}: {e}")

            if images:
                # Find the last user message and add images
                for i in range(len(messages) - 1, -1, -1):
                    if messages[i].get("role") == "user":
                        messages[i]["images"] = images
                        break

        try:
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
                stream=stream,
            )
            response.raise_for_status()

            if stream:
                return self._handle_stream_response(response)
            else:
                result = response.json()
                logger.info("Chat generation completed successfully")
                return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Chat API request failed: {e}")
            raise

    def _handle_stream_response(
        self, response
    ) -> Generator[Dict[str, Any], None, None]:
        """Handle streaming response from Ollama"""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))
                    yield data
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse streaming response: {e}")
                    continue

    def embed(self, model: str, prompt: str) -> Dict[str, Any]:
        """
        Generate embeddings for text

        Args:
            model: Model name to use for embeddings
            prompt: Text to generate embeddings for

        Returns:
            Dictionary containing embeddings
        """
        payload = {"model": model, "prompt": prompt}

        try:
            response = self.session.post(
                f"{self.base_url}/api/embeddings",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Embeddings request failed: {e}")
            raise

    def list_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            return response.json().get("models", [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list models: {e}")
            raise

    def show_model(self, model: str) -> Dict[str, Any]:
        """Get detailed information about a model"""
        payload = {"name": model}
        try:
            response = self.session.post(
                f"{self.base_url}/api/show",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to show model {model}: {e}")
            raise

    def pull_model(self, model: str) -> Generator[Dict[str, Any], None, None]:
        """
        Pull/download a model

        Args:
            model: Model name to pull

        Yields:
            Progress updates during model download
        """
        payload = {"name": model}
        try:
            response = self.session.post(
                f"{self.base_url}/api/pull",
                json=payload,
                headers={"Content-Type": "application/json"},
                stream=True,
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8"))
                        yield data
                    except json.JSONDecodeError:
                        continue

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to pull model {model}: {e}")
            raise

    def delete_model(self, model: str) -> Dict[str, Any]:
        """Delete a model"""
        try:
            response = self.session.delete(
                f"{self.base_url}/api/delete", json={"name": model}
            )
            response.raise_for_status()
            return {"status": "success", "message": f"Model {model} deleted"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete model {model}: {e}")
            raise

    def copy_model(self, source: str, destination: str) -> Dict[str, Any]:
        """Copy a model"""
        payload = {"source": source, "destination": destination}
        try:
            response = self.session.post(
                f"{self.base_url}/api/copy",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return {
                "status": "success",
                "message": f"Model {source} copied to {destination}",
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to copy model from {source} to {destination}: {e}")
            raise

    def create_model(
        self, name: str, modelfile: str, stream: bool = False
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        Create a model from a Modelfile

        Args:
            name: Name for the new model
            modelfile: Modelfile content
            stream: Whether to stream the response

        Returns:
            Dictionary or generator with creation status
        """
        payload = {"name": name, "modelfile": modelfile, "stream": stream}

        try:
            response = self.session.post(
                f"{self.base_url}/api/create",
                json=payload,
                headers={"Content-Type": "application/json"},
                stream=stream,
            )
            response.raise_for_status()

            if stream:
                return self._handle_stream_response(response)
            else:
                return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create model {name}: {e}")
            raise

    def is_running(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = OllamaClient("http://localhost:11434")

    # Check if server is running
    if not client.is_running():
        print("Ollama server is not running. Please start it first.")
        exit(1)

    try:
        # Example 1: List available models
        print("=== Available Models ===")
        models = client.list_models()
        for model in models:
            print(f"- {model['name']} ({model.get('size', 'unknown size')})")

        if not models:
            print(
                "No models found. Please pull a model first (e.g., 'ollama pull llama2')"
            )
            exit(1)

        # Use the first available model for examples
        model_name = models[0]["name"]
        print(f"\nUsing model: {model_name}")

        # Example 2: Basic text generation
        print("\n=== Basic Text Generation ===")
        result = client.generate_text(
            model=model_name,
            prompt="Explain quantum computing in simple terms.",
            system_prompt="You are a helpful AI assistant that explains complex topics clearly.",
            temperature=0.7,
            num_predict=150,
        )
        print(f"Generated text: {result.get('response', '')}")

        # Example 3: Chat format
        print("\n=== Chat Format Generation ===")
        messages = [
            {"role": "system", "content": "You are an environmental expert."},
            {"role": "user", "content": "What are the benefits of renewable energy?"},
        ]

        result = client.chat(model=model_name, messages=messages, temperature=0.7)
        print(f"Chat response: {result.get('message', {}).get('content', '')}")

        # Example 4: Text generation with image (if you have an image file)
        print("\n=== Text Generation with Image (if available) ===")
        # Create a simple test image or use an existing one
        try:
            # This is just for demonstration - replace with actual image path
            image_path = "test_image.jpg"
            if Path(image_path).exists():
                result = client.generate_text(
                    model=model_name,
                    prompt="Describe what you see in this image.",
                    attachments=[image_path],
                    temperature=0.7,
                )
                print(f"Image description: {result.get('response', '')}")
            else:
                print("No test image found. Skipping image example.")
        except Exception as e:
            print(f"Image example failed: {e}")

        # Example 5: Streaming generation
        print("\n=== Streaming Generation ===")
        print("Streaming response: ", end="", flush=True)
        for chunk in client.generate_text(
            model=model_name,
            prompt="Write a short poem about nature.",
            stream=True,
            num_predict=50,
        ):
            if "response" in chunk:
                print(chunk["response"], end="", flush=True)
            if chunk.get("done", False):
                break
        print("\n")

        # Example 6: Model information
        print("\n=== Model Information ===")
        model_info = client.show_model(model_name)
        print(f"Model details: {model_info.get('details', {})}")

        # Example 7: Embeddings (if supported by model)
        print("\n=== Embeddings ===")
        try:
            embeddings = client.embed(
                model=model_name, prompt="This is a test sentence for embeddings."
            )
            if "embedding" in embeddings:
                print(f"Embedding dimension: {len(embeddings['embedding'])}")
                print(f"First 5 values: {embeddings['embedding'][:5]}")
        except Exception as e:
            print(f"Embeddings not supported or failed: {e}")

    except Exception as e:
        print(f"Error: {e}")

    print("\nExamples completed!")
