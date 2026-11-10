
import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path


class LLMClient:

    def __init__(self):
        env_path = Path(__file__).resolve().parent/".env"
        load_dotenv(dotenv_path=env_path)

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment.")

        self.client = OpenAI(api_key=api_key)

        self.model = "gpt-5.4"

    def generate_response(self, prompt):

        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        return response.output_text
