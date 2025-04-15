from contextlib import asynccontextmanager

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

model = ChatOpenAI(model="gpt-4o")


@asynccontextmanager
async def make_graph():
    async with MultiServerMCPClient(
        {
            "box_mcp": {
                # "command": "python",
                # # Make sure to update to the full absolute path to your math_server.py file
                # "args": ["/path/to/math_server.py"],
                "command": "uv",
                "args": [
                    "--directory",
                    "/Users/rbarbosa/Documents/code/python/box/mcp-server-box",
                    "run",
                    "src/mcp_server_box.py",
                ],
                "transport": "stdio",
            },
        }
    ) as client:
        agent = create_react_agent(model, client.get_tools())
        yield agent
