import requests
import os
import json
import openai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")

def ask_llm(prompt):
    
    client = openai.OpenAI(
        api_key=f"{API_KEY}",
        base_url="https://api.groq.com/openai/v1"
    )

    response = client.responses.create(
        model="llama-3.3-70b-versatile",
        input=prompt,
    )
    try:
        return response.output_text
    except Exception as e:
        return f"Something went wrong: {e}"
    

'''prompt="hi"
result=ask_llm(prompt)
print(result)
'''





#previous code
'''headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/mistral-small-3.2-24b-instruct:free",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload)
        )
        result = response.json()
        #message = result["choices"][0]["message"]["content"]
        return result
    except Exception as e:
        return f"Something went wrong: {e}"'''
    