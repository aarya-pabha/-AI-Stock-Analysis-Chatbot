import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from beeai_framework.backend.chat import ChatModel, ChatModelParameters
from src.orchestration.schemas import UserContext
from src.agents.bull_agent import create_bull_agent

async def debug_agent():
    print("Debugging Bull Agent instantiation and run...")
    context = UserContext(ticker="AAPL")
    agent = create_bull_agent(context)
    
    print(f"Using model: {agent._llm.model_id}")
    print(f"Provider: {agent._llm.provider_id}")
    
    try:
        # Just a simple prompt to see if it responds
        result = await agent.run("Hello, are you ready?")
        print("Response:", result.last_message.text)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_agent())
