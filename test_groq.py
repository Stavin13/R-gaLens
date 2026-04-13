import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

try:
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": "Hello, tell me a joke about musicology."}
        ],
        model="llama-3.3-70b-versatile",
    )
    print(chat_completion.choices[0].message.content)
except Exception as e:
    print(f"Groq Error: {e}")
