# Create server parameters for stdio connection
import uuid

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from console_utils.console_app import (
    print_ai_message,
    print_human_message,
    print_markdown,
    print_tool_message,
    prompt_user,
)


async def main():
    model = ChatOpenAI(model="gpt-4o")

    server_params = StdioServerParameters(
        # command="python",
        command="uv",
        # Make sure to update to the full absolute path to your math_server.py file
        # args=["/path/to/math_server.py"],
        args=[
            "--directory",
            "/Users/rbarbosa/Documents/code/python/box/mcp-server-box",
            "run",
            "src/mcp_server_box.py",
        ],
    )
    memory = MemorySaver()
    chat_id = uuid.uuid4()
    config = {"configurable": {"thread_id": str(chat_id)}}

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # Get tools
            tools = await load_mcp_tools(session)

            # Create and run the agent
            agent = create_react_agent(model, tools, checkpointer=memory)

            # loop through user input
            # print("Enter 'exit' to quit.")
            history_index = 0
            while True:
                user_input = prompt_user("Prompt (exit to quit)")
                if user_input.lower() == "exit":
                    break

                # Send the user input to the agent
                agent_response = await agent.ainvoke(
                    {"messages": user_input}, config=config
                )
                # print(agent_response)
                messages = agent_response.get("messages", [])
                for message in messages[history_index:]:
                    # use different prints depending on message object type
                    if isinstance(message, HumanMessage):
                        print_human_message(message)
                    elif isinstance(message, AIMessage):
                        print_ai_message(message)
                    elif isinstance(message, ToolMessage):
                        print_tool_message(message)
                    else:
                        print_markdown(f"**Unknown message type:** {type(message)}")
                    # print(type(message))
                    # print_markdown(message.content)
                    history_index += 1
                    print_markdown("---")
                # history_index = len(messages - 1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
