import os
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
import openai
from google import genai
from anthropic import Anthropic

# Configure logging
log_directory = os.getenv("LOG_DIR", "logs")
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(log_directory, f"llm_calls_{datetime.now().strftime('%Y%m%d')}.log")

# Set up logger
logger = logging.getLogger("llm_logger")
logger.setLevel(logging.INFO)
logger.propagate = False  # Prevent propagation to root logger
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Simple cache configuration
cache_file = "llm_cache.json"

class LLMService:
    def __init__(self):
        self.client = None
        self.model = None
        self.setup_client()

    def setup_client(self):
        provider = os.getenv("LLM_PROVIDER", "gemini")
        
        if provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")
            self.client = genai.Client(api_key=api_key)
            self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro-exp-03-25")
        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            self.client = Anthropic(api_key=api_key)
            self.model = "claude-3-7-sonnet-20250219"
        elif provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            self.client = openai.OpenAI(api_key=api_key)
            self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    async def generate(self, prompt: str, use_cache: bool = True) -> str:
        """Generate text using the configured LLM."""
        try:
            # Log the prompt
            logger.info(f"PROMPT: {prompt}")
            
            # Check cache if enabled
            if use_cache:
                # Load cache from disk
                cache = {}
                if os.path.exists(cache_file):
                    try:
                        with open(cache_file, 'r') as f:
                            cache = json.load(f)
                    except:
                        logger.warning(f"Failed to load cache, starting with empty cache")
                
                # Return from cache if exists
                if prompt in cache:
                    logger.info(f"CACHE HIT - RESPONSE: {cache[prompt]}")
                    return cache[prompt]

            # Call the appropriate LLM provider
            provider = os.getenv("LLM_PROVIDER", "gemini")
            response_text = ""
            
            if provider == "gemini":
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[prompt]
                )
                response_text = response.text
            elif provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=21000,
                    thinking={
                        "type": "enabled",
                        "budget_tokens": 20000
                    },
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                response_text = response.content[1].text
            elif provider == "openai":
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={
                        "type": "text"
                    },
                    reasoning_effort="medium",
                    store=False,
                    temperature=0.7,
                    max_tokens=2000
                )
                response_text = response.choices[0].message.content
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")

            # Log the response
            logger.info(f"RESPONSE: {response_text}")
            
            # Update cache if enabled
            if use_cache:
                # Load cache again to avoid overwrites
                cache = {}
                if os.path.exists(cache_file):
                    try:
                        with open(cache_file, 'r') as f:
                            cache = json.load(f)
                    except:
                        pass
                
                # Add to cache and save
                cache[prompt] = response_text
                try:
                    with open(cache_file, 'w') as f:
                        json.dump(cache, f)
                except Exception as e:
                    logger.error(f"Failed to save cache: {e}")

            return response_text

        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise Exception(f"LLM generation failed: {str(e)}")

    def test_connection(self) -> bool:
        """Test the LLM connection."""
        try:
            # Try a simple prompt
            test_prompt = "Hello, how are you?"
            response = self.generate(test_prompt, use_cache=False)
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False

    async def analyze_code(self, code: str, context: str) -> str:
        """Analyze code and provide explanations."""
        prompt = f"""
        Analyze this code and provide a beginner-friendly explanation:
        
        Code:
        {code}
        
        Context:
        {context}
        """
        return await self.generate(prompt)

    async def generate_diagram_description(self, description: str) -> str:
        """Generate a Mermaid diagram description."""
        prompt = f"""
        Generate a Mermaid diagram description for this system:
        {description}
        """
        return await self.generate(prompt)

    async def explain_concept(self, concept: str, language: str = "english") -> str:
        """Explain a programming concept in simple terms."""
        prompt = f"""
        Explain this concept in simple terms and provide practical examples:
        {concept}
        
        Language: {language}
        """
        return await self.generate(prompt)
