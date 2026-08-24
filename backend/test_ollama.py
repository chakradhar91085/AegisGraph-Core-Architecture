import asyncio
from app.llm.ollama_client import ollama_client

async def test():
    print("Health:", await ollama_client.check_health())
    print("Gen:", await ollama_client.generate("Hello! Who are you?"))

if __name__ == "__main__":
    asyncio.run(test())
