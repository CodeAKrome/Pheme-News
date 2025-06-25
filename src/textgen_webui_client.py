import requests
import json
import base64
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextGenWebUIClient:
    """Python client for text-generation-webui API"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        Initialize the client
        
        Args:
            base_url: Base URL of the text-generation-webui server
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def _encode_file(self, file_path: Union[str, Path]) -> Dict[str, str]:
        """
        Encode a file to base64 for API transmission
        
        Args:
            file_path: Path to the file to encode
            
        Returns:
            Dictionary with file data
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type is None:
            mime_type = 'application/octet-stream'
            
        with open(file_path, 'rb') as f:
            content = base64.b64encode(f.read()).decode('utf-8')
            
        return {
            'filename': file_path.name,
            'content': content,
            'mime_type': mime_type
        }
    
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        attachments: Optional[List[Union[str, Path]]] = None,
        max_new_tokens: int = 200,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        repetition_penalty: float = 1.1,
        do_sample: bool = True,
        seed: int = -1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using the text-generation-webui API
        
        Args:
            prompt: The main prompt text
            system_prompt: Optional system prompt to set behavior
            attachments: List of file paths to attach
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            repetition_penalty: Penalty for repetition
            do_sample: Whether to use sampling
            seed: Random seed (-1 for random)
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing the generated text and metadata
        """
        # Prepare the request payload
        payload = {
            'prompt': prompt,
            'max_new_tokens': max_new_tokens,
            'temperature': temperature,
            'top_p': top_p,
            'top_k': top_k,
            'repetition_penalty': repetition_penalty,
            'do_sample': do_sample,
            'seed': seed,
            **kwargs
        }
        
        # Add system prompt if provided
        if system_prompt:
            payload['system_prompt'] = system_prompt
            
        # Add attachments if provided
        if attachments:
            encoded_attachments = []
            for attachment in attachments:
                try:
                    encoded_file = self._encode_file(attachment)
                    encoded_attachments.append(encoded_file)
                    logger.info(f"Added attachment: {encoded_file['filename']}")
                except Exception as e:
                    logger.error(f"Failed to encode attachment {attachment}: {e}")
                    
            if encoded_attachments:
                payload['attachments'] = encoded_attachments
        
        try:
            # Send request to the API
            response = self.session.post(
                f"{self.base_url}/api/v1/generate",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info("Text generation completed successfully")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def generate_chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        attachments: Optional[List[Union[str, Path]]] = None,
        max_new_tokens: int = 200,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using chat format
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            system_prompt: Optional system prompt
            attachments: List of file paths to attach
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing the generated response
        """
        payload = {
            'messages': messages,
            'max_new_tokens': max_new_tokens,
            'temperature': temperature,
            **kwargs
        }
        
        if system_prompt:
            payload['system_prompt'] = system_prompt
            
        if attachments:
            encoded_attachments = []
            for attachment in attachments:
                try:
                    encoded_file = self._encode_file(attachment)
                    encoded_attachments.append(encoded_file)
                except Exception as e:
                    logger.error(f"Failed to encode attachment {attachment}: {e}")
                    
            if encoded_attachments:
                payload['attachments'] = encoded_attachments
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/chat/completions",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info("Chat generation completed successfully")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Chat API request failed: {e}")
            raise
    
    def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        attachments: Optional[List[Union[str, Path]]] = None,
        **kwargs
    ):
        """
        Stream text generation (generator function)
        
        Args:
            prompt: The main prompt text
            system_prompt: Optional system prompt
            attachments: List of file paths to attach
            **kwargs: Additional generation parameters
            
        Yields:
            Generated text chunks
        """
        payload = {
            'prompt': prompt,
            'stream': True,
            **kwargs
        }
        
        if system_prompt:
            payload['system_prompt'] = system_prompt
            
        if attachments:
            encoded_attachments = []
            for attachment in attachments:
                try:
                    encoded_file = self._encode_file(attachment)
                    encoded_attachments.append(encoded_file)
                except Exception as e:
                    logger.error(f"Failed to encode attachment {attachment}: {e}")
                    
            if encoded_attachments:
                payload['attachments'] = encoded_attachments
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/generate",
                json=payload,
                headers={'Content-Type': 'application/json'},
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if 'text' in data:
                            yield data['text']
                    except json.JSONDecodeError:
                        continue
                        
        except requests.exceptions.RequestException as e:
            logger.error(f"Streaming request failed: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the currently loaded model"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/model")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get model info: {e}")
            raise
    
    def list_models(self) -> List[str]:
        """Get list of available models"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/models")
            response.raise_for_status()
            return response.json().get('models', [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list models: {e}")
            raise
    
    def load_model(self, model_name: str) -> Dict[str, Any]:
        """Load a specific model"""
        payload = {'model_name': model_name}
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/model",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = TextGenWebUIClient("http://localhost:5000")
    
    try:
        # Example 1: Basic text generation
        print("=== Basic Text Generation ===")
        result = client.generate_text(
            prompt="Explain quantum computing in simple terms.",
            system_prompt="You are a helpful AI assistant that explains complex topics clearly.",
            max_new_tokens=150,
            temperature=0.7
        )
        print(f"Generated text: {result.get('results', [{}])[0].get('text', '')}")
        
        # Example 2: Text generation with file attachment
        print("\n=== Text Generation with Attachment ===")
        # Create a sample file for demonstration
        with open("sample.txt", "w") as f:
            f.write("This is a sample document about machine learning concepts.")
        
        result = client.generate_text(
            prompt="Summarize the attached document and provide key insights.",
            system_prompt="You are an expert at analyzing and summarizing documents.",
            attachments=["sample.txt"],
            max_new_tokens=100
        )
        print(f"Generated summary: {result.get('results', [{}])[0].get('text', '')}")
        
        # Example 3: Chat format
        print("\n=== Chat Format Generation ===")
        messages = [
            {"role": "user", "content": "What are the benefits of renewable energy?"},
        ]
        
        result = client.generate_chat(
            messages=messages,
            system_prompt="You are an environmental expert.",
            max_new_tokens=100
        )
        print(f"Chat response: {result}")
        
        # Example 4: Streaming generation
        print("\n=== Streaming Generation ===")
        print("Streaming response: ", end="", flush=True)
        for chunk in client.stream_generate(
            prompt="Write a short poem about nature.",
            max_new_tokens=50
        ):
            print(chunk, end="", flush=True)
        print("\n")
        
        # Example 5: Model management
        print("\n=== Model Information ===")
        model_info = client.get_model_info()
        print(f"Current model: {model_info}")
        
        models = client.list_models()
        print(f"Available models: {models}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Clean up sample file
        try:
            Path("sample.txt").unlink()
        except FileNotFoundError:
            pass