# 1. available_tools = mcp_list_available_tools()
# 2. messages = [system_prompt, user_prompt, available_tools]
# 3. while True:
# 4.     tool_calls, reply = llm(messages)
# 5.     if tool_calls:
# 6.         for tool in tool_calls:
# 7.             result = mcp_execute_tool(tool)
# 8.             messages.append(result)
# 9.     else:
# 10.        show(reply)
# 11.        break

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
MODEL = "gpt-4o"

SYSTEM_PROMPT =  (
    "You are an AI assistant with access to tools provided by the MCP server. " 
    "Always plan before solving. " 
    "Always use tools when available to answer user queries. "
    "Trust the tool catalog and never guess answers if a tool is relevant. "
    "You must call the 'plan' function first before using other tools. "
    "Never guess the answer. List tools used at the end." 
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
        "What are the total expenses in SAR of my car," 
        "and the number of times I did a payment?." 
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



# def generate_commit_message(model, diff):
# """Generate a concise commit message using OpenAI."""
# while True:
#     completion = llm_client.chat.completions.create(
#         model=model,
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {
#                 "role": "user",
#                 "content": f"""
#                 Analyze the following git diff output and generate a concise, meaningful commit message. 
#                 Focus on the purpose of the changes rather than listing modified files. 
#                 Keep the response in a single line without markdown formatting.
#                 Make several messages if needed for clarity but all of them in a single line.
#                 If I ask this question again with the same diff, add more details.
#                 Git diff output: {diff}
#                 """
#             }
#         ]
#     )

#     commit_message = completion.choices[0].message.content.strip()
#     print(f"\n\n{commit_message}\n")

#     user_input = input(
#         "\n" + "="*40 + 
#         "\n  Is this message good?:\n" +
#         "="*40 + 
#         "\n  [  Enter  ] → Accept and commit" +
#         "\n  [    g    ] → Generate a new message" +
#         "\n  [ Any key ] → Cancel\n" +
#         "="*40 + "\n> "
#     ).strip().lower()

#     if user_input == "":
#         return commit_message  # Accept the message
#     elif user_input == "g":
#         print("Regenerating commit message...\n")
#     else:
#         print("Commit canceled.")
#         sys.exit()

