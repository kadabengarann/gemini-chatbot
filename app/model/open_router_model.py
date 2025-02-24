import logging
import tiktoken  # Make sure to install this with: pip install tiktoken
from flask import current_app
from langchain_together import Together
from langchain_openai import ChatOpenAI
from pydantic import Field
from typing import Optional
from pydantic import SecretStr

def get_tokenizer_for_model(model_name: str):
    """
    Map the model name to a specific tiktoken encoding.
    Adjust the mapping based on your supported models.
    For example, many OpenAI models use 'cl100k_base', while Llama-based models
    typically use the 'gpt2' encoding.
    """
    model_to_encoding = {
        "gpt-3.5-turbo": "cl100k_base",
        "gpt-4": "cl100k_base",
        # For DeepSeek-R1 Distilled Llama models, we assume 'gpt2' encoding is appropriate.
        "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free": "gpt2",
        # Add additional mappings as needed.
    }
    
    # Use a default if the model isn't explicitly mapped.
    encoding_name = model_to_encoding.get(model_name, "gpt2")
    try:
        tokenizer = tiktoken.get_encoding(encoding_name)
        logging.info("Using '%s' encoding for model '%s'", encoding_name, model_name)
        return tokenizer
    except Exception as e:
        logging.error("Error initializing tokenizer for model '%s' with encoding '%s': %s",
                      model_name, encoding_name, e)
        raise

class ChatOpenRouter(ChatOpenAI):
    class Config:
        # Allow setting extra attributes not declared in the model schema.
        extra = "allow"

    def __init__(self, model_name: str, **kwargs):
        super().__init__(
            openai_api_key= current_app.config.get("OPENROUTER_API_KEY"),
            openai_api_base= "https://openrouter.ai/api/v1",
            model_name=model_name,
            **kwargs  # Pass any additional arguments to the parent class
        )
        object.__setattr__(self, "tokenizer", get_tokenizer_for_model(model_name))
        
    def get_num_tokens_from_messages(self, messages):
        """
        Calculate the number of tokens in a list of messages using tiktoken.
        Each message is expected to have a 'content' attribute.
        """
        total_tokens = 0
        for message in messages:
            # Use getattr to retrieve content if message is an object (like AIMessage).
            content = getattr(message, "content", "")
            try:
                tokens = self.tokenizer.encode(content)
                total_tokens += len(tokens)
            except Exception as e:
                logging.error("Tokenization error for message '%s': %s", content, e)
                # Fallback heuristic: assume ~1 token per 4 characters.
                total_tokens += len(content) // 4
        return total_tokens
        

# Custom subclass of ChatTogether with an implementation for token counting.
class MyChatTogether(Together):
    # Declare tokenizer as a field.
    tokenizer: any = Field(default=None)

    class Config:
        # Allow setting extra attributes not declared in the model schema.
        extra = "allow"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically select tokenizer based on the MODEL_NAME in your Flask config.
        model_name = current_app.config.get('MODEL_NAME')
        if not model_name:
            raise ValueError("MODEL_NAME environment variable not set")
        # Use object.__setattr__ to bypass Pydantic's immutability.
        object.__setattr__(self, "tokenizer", get_tokenizer_for_model(model_name))

    def get_num_tokens_from_messages(self, messages):
        """
        Calculate the number of tokens in a list of messages using tiktoken.
        Each message is expected to have a 'content' attribute.
        """
        total_tokens = 0
        for message in messages:
            # Use getattr to retrieve content if message is an object (like AIMessage).
            content = getattr(message, "content", "")
            try:
                tokens = self.tokenizer.encode(content)
                total_tokens += len(tokens)
            except Exception as e:
                logging.error("Tokenization error for message '%s': %s", content, e)
                # Fallback heuristic: assume ~1 token per 4 characters.
                total_tokens += len(content) // 4
        return total_tokens