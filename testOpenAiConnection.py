from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv()) 
key = os.getenv("OPENAI_API_KEY", "")


