"""OpenAI API connector."""
# Import from standard library
import os
import logging
# Import from 3rd party libraries
import openai
import sys
# Assign credentials from environment variable or streamlit secrets dict
openai.api_type = os.getenv("OPENAI_API_TYPE")
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_version = os.getenv("OPENAI_API_VERSION")
# Suppress openai request/response logging
# Handle by manually changing the respective APIRequestor methods in the openai package
# Does not work hosted on Streamlit since all packages are re-installed by Poetry
# Alternatively (affects all messages from this logger):
logging.getLogger("openai").setLevel(logging.WARNING)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, force=True)
class Openai:
    """OpenAI Connector."""
    @staticmethod
    def chat_completion(
        messages: str,
        temperature: float = 0.9,
        max_tokens: int = 350,
        engine: str = "gpt-4-0314",
    ) -> str:
        """
        Uses OpenAI's GPT-3 to generate a completion for a given prompt message.
        Args:
            messages (str): The prompt message to complete.
            temperature (float): Controls the randomness of the generated text. Higher values means more random.
            max_tokens (int): Controls the maximum number of tokens (words or sub-words) in the generated text.
        Returns:
            str: The generated completion message.
        Raises:
            logging.error: If there is an error with the OpenAI API.
        """
        kwargs = {
            "engine": engine,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 1,  # default
            "frequency_penalty": 0,  # default,
            "presence_penalty": 0,  # default
            "stop": None,
        }
        try:
            response = openai.ChatCompletion.create(**kwargs)
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            logging.error(f"OpenAI API error: {e}")