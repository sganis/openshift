import asyncio
from fastmcp import Client

client = Client("server.py") # server.py exists
# client = Client("http://localhost:9000/mcp")  # HTTP transport

async def main():
    # Connection is established here
    async with client:
        print(f"Client connected: {client.is_connected()}")
        await client.ping()
        print("Server is reachable")
        
        # Make MCP calls within the context
        tools = await client.list_tools()
        print(f"Available tools: {tools}")
        resources = await client.list_resources()
        print(f"Available resources: {resources}")
        templates = await client.list_resource_templates()
        print(f"Available templates: {templates}")
        prompts = await client.list_prompts()
        print(f"Available prompts: {prompts}")

        result = await client.call_tool("get_total_expenses", {"car": "Yukon"})
        print(f"result: {result}")

    # Connection is closed automatically here
    print(f"Client connected: {client.is_connected()}")

if __name__ == "__main__":
    asyncio.run(main())



# # client.py
# import os
# import asyncio
# from fastmcp.hosts.openai import OpenAIHost
# from fastmcp import Client

# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# async def main():
#     # Connect to the tool server (e.g., stdio or TCP)
#     async with Client("stdio://", tools=True) as tool_client:
#         # Wrap the LLM as a host, providing access to the connected tools
#         host = OpenAIHost(api_key=OPENAI_API_KEY, 
#                           model="gpt-4o", 
#                           tools=[tool_client])
        
#         result = await host.run("Say hello using the greet tool")
#         print(result)

# if __name__ == "__main__":
#     asyncio.run(main())


