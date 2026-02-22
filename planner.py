import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

def create_plan(user_goal):
    prompt = f"""
    You are an autonomous financial AI agent.

    A user has the following goal:
    {user_goal}

    Break this goal into clear financial subtasks.
    Return only numbered steps.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text
