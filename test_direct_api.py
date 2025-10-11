#!/usr/bin/env python3
"""Direct OpenAI API test"""

import os
from dotenv import load_dotenv
load_dotenv()

import openai
import httpx

api_key = os.environ.get("OPENAI_API_KEY")
print(f"API Key found: {bool(api_key)}")
print(f"API Key prefix: {api_key[:20] if api_key else 'None'}...")

try:
    # Create client
    http_client = httpx.Client()
    client = openai.OpenAI(api_key=api_key, http_client=http_client)
    
    print("\n✅ Client created successfully")
    print("Attempting API call...")
    
    # Try a simple call
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say 'test successful' in 3 words"}],
        max_tokens=10
    )
    
    result = response.choices[0].message.content
    print(f"\n🎉 SUCCESS! Response: {result}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print(f"Error type: {type(e).__name__}")
