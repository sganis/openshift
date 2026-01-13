# tools = client.list_tools()
# messages = [user_prompt, system_prompt, tools]
# while True:
#     tool_calls, reply = llm.chat(messages)
#     if tool_calls:
#         for tool in tool_calls:
#             result = client.call_tool(tool)
#             messages.append(result)
#     else:
#         show(reply)
#         break

import os
import json
import asyncio
from dotenv import load_dotenv
from pathlib import Path
from openai import AsyncOpenAI
from client import client as mcp_client

# Load the .env file from the parent directory
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("OPENAI_API_KEY")
assert api_key, "API key not found. Make sure you have a .env file in the parent directory."

llm_client = AsyncOpenAI()

async def list_models():
    client = AsyncOpenAI()
    response = await client.models.list()
    
    for model in response.data:
        print(model.id)

# asyncio.run(list_models())
# MODEL = "gpt-4o-mini"
MODEL = "gpt-4o"

SYSTEM_PROMPT =  (
    "You are an AI assistant with access to tools provided by the MCP server. " 
    "Always plan before solving. " 
    "Always use tools when available to answer user queries. "
    "Trust the tool catalog and never guess answers if a tool is relevant. "
    "You must call the 'plan' function first before using other tools. "
    "Never guess the answer. List tools used at the end." 
    "Use the file file.csv in my machine to get data of cost of living indices per city."
    "Search for the 327 cities in the file and return the one with the lowest grocery index."
    "The grocery index is the sixth column in the file, with columns separated by commas. "
)

PLAN_TOOL = [{
    "type": "function",
    "function": {
        "name": "plan",
        "description": "Create a plan of reasoning before solving the task.",
        "parameters": {
            "type": "object",
            "properties": {
                "steps": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "The steps to solve the problem"
                }
            },
            "required": ["steps"]
        }
    }
}]

async def main():
    # prompt = "Compute 2 and 3"
    prompt = (
        "which city has the lowest grocery index?"
        "Compare with my city. Which position is my city in the list?" 
    )
    
    async with mcp_client:
        tool_list = await mcp_client.list_tools()
        print(f"Available tools: {tool_list}")
    
    tool_names = [tool.name for tool in tool_list]
    print(f'Available tool names: {tool_names}')
        
    openai_tools = PLAN_TOOL + [{
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema
        }
    } for tool in tool_list]


    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]

    i = 1
    while True:
        # Ask the LLM what to do next
        print(f'{i}: Calling llm...')
        response = await llm_client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=openai_tools,
            tool_choice="auto"
        )

        msg = response.choices[0].message

        # If LLM wants to call tools
        if msg.tool_calls:
            messages.append({"role": "assistant", "tool_calls": msg.tool_calls})

            for call in msg.tool_calls:
                tool_name = call.function.name
                tool_args = json.loads(call.function.arguments)
                print(f"   Tool Call: {tool_name}, Args: {tool_args}")

                if call.function.name == "plan":
                    print("🧠 Plan Steps:")
                    for step in tool_args["steps"]:
                        print(f" - {step}")
                    tool_output = "Plan acknowledged."
                else:
                    async with mcp_client:
                        tool_result = await mcp_client.call_tool(tool_name, tool_args)
                    tool_output = tool_result[0].text
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": tool_name,
                    "content": tool_output
                })
            # print(f"Messages: {messages}")
            i += 1
        else:
            # Final answer
            print(f"\nFinal Response:\n{msg.content}")
            break

if __name__ == "__main__":
    asyncio.run(main())


