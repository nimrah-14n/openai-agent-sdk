from agents import Agent,Runner,OpenAICompletionModel, AsyncOpenAI, RunConfig
import os
from dotenv import load_dotenv
load_dotenv()
gemini_api_key=os.getenv("GEMINI_API_KEY")
provider=AsyncOpenAI