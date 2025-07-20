#!/usr/bin/env python3
"""
Direct API test without async.
"""

def test_api_direct():
    """Test API directly."""
    
    import os
    import requests
    
    print("Testing OpenRouter API directly...")
    
    # Load API key from .env
    api_key = "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"
    
    print(f"API key: {api_key[:15]}...")
    print(f"API key length: {len(api_key)}")
    print(f"Starts with sk-or-v1-: {api_key.startswith('sk-or-v1-')}")
    
    # Test API call
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [{"role": "user", "content": "Hello, respond with 'API working!'"}],
        "temperature": 0.1,
        "max_tokens": 20
    }
    
    print(f"\nHeaders: {headers}")
    print(f"Data: {data}")
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"SUCCESS: {content}")
            return True
        else:
            print(f"ERROR: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_api_direct()