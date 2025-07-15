#!/usr/bin/env python3
"""
Test script to verify OpenAI API integration
"""

import asyncio
from llm_service import LLMService

async def test_openai():
    """Test OpenAI API integration"""
    print("🧪 Testing OpenAI API integration...")
    
    try:
        llm_service = LLMService()
        
        # Test simple response generation
        test_prompt = "Generate a professional response for: 'Why do you want to work at this company?'"
        response = await llm_service.generate_response(test_prompt, max_tokens=100)
        
        print("✅ OpenAI API test successful!")
        print(f"Response: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_openai())
    if success:
        print("\n🎉 OpenAI integration is working perfectly!")
    else:
        print("\n⚠️ OpenAI integration needs attention.") 