from fastmcp import FastMCP
from typing import Annotated
from pydantic import Field
import csv

mcp = FastMCP("My MCP Server")

# # You can also add instructions for how to interact with the server
# mcp_with_instructions = FastMCP(
#     name="HelpfulAssistant",
#     instructions="""
#         This server provides data analysis tools.
#         Call get_average() to analyze numerical data.
#         """
# )

# @mcp.tool()
# def greet(name: str) -> str:
#     return f"Hello, {name}!"

# @mcp.tool()
# def compute(
#     a: Annotated[float, Field(description="First number")],
#     b: Annotated[float, Field(description="Second number")]) -> float:
#     """Compute two numbers."""
#     return a * b * 100

@mcp.tool()
def read_local_file(
    path: Annotated[str, Field(description="Path to the file in the local filesystem")]
    ) -> str:
    """Read a local file and return the content."""
    print('running read_local_file tool...')
    return open(path, "r").read()

# @mcp.tool()
# def my_current_car() -> str:
#     """Return my current car."""
#     return 'Yukon'

# @mcp.tool()
# def my_country() -> str:
#     """Return my country."""
#     return 'Brazil'

@mcp.tool()
def my_city() -> str:
    """Return my city."""
    return 'Rio de Janeiro'

# @mcp.tool()
# def get_expenses(car: Annotated[str, Field(description="Car model")]) -> list[object]:
#     """Return all the expenses of a car with date, detail, and expense in SAR."""
#     expenses = []
#     with open("file.csv", "r") as file:
#         reader = csv.reader(file)
#         next(reader) 
#         # Fecha,Auto,Km,SAR,Detalle,Taller
#         for row in reader:
#             if row[1] == car:
#                 value = float(row[3].replace(',', '').replace('"', ''))
#                 expenses.append({'date':row[0], 'detail': row[4], 'expense':value})
#     return expenses

# @mcp.tool()
# def get_total_expenses(car: Annotated[str, Field(description="Car model")]) -> float:
#     """Return total expenses of a car in SAR."""
#     expenses = 0
#     with open("file.csv", "r") as file:
#         reader = csv.reader(file)
#         next(reader) 
#         # Fecha,Auto,Km,SAR,Detalle,Taller
#         for row in reader:
#             if row[1] == car:
#                 value = float(row[3].replace(',', '').replace('"', ''))
#                 expenses += value
#     return expenses

# Resource returning JSON data (dict is auto-serialized)
@mcp.resource("data://config")
def get_config() -> dict:
    """Provides application configuration as JSON."""
    return {
        "theme": "dark",
        "version": "1.2.0",
        "features": ["tools", "resources"],
    }

@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: int) -> dict:
    """Retrieves a user's profile by ID."""
    # The {user_id} in the URI is extracted and passed to this function
    return {"id": user_id, "name": f"User {user_id}", "status": "active"}

@mcp.prompt()
def analyze_data(data_points: list[float]) -> str:
    """Creates a prompt asking for analysis of numerical data."""
    formatted_data = ", ".join(str(point) for point in data_points)
    return f"Please analyze these data points: {formatted_data}"


if __name__ == "__main__":
    # This runs the server, defaulting to STDIO transport
    mcp.run()
    
    # To use a different transport, e.g., HTTP:
    # mcp.run(transport="streamable-http", host="127.0.0.1", port=9000, path='/mcp')