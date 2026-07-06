"""Programmatic end-to-end run of the Podcast Visualizer pipeline.
 
Used by test_local.sh. Sends one request to the editor (root) agent and
streams its responses, exactly as if a user had typed the request in the
adk web UI.
 
Design note: ADK agents are not invoked directly (there is no
root_agent.chat()). They are executed through a Runner, which manages
the session state, the tool/agent-tool calls, and the event stream.
InMemoryRunner is the simplest Runner: it keeps the session in memory,
which is all a scripted test needs.
"""
 
import asyncio
 
from google.adk.runners import InMemoryRunner
from google.genai import types
 
from agent.agent import root_agent
 
APP_NAME = "podcast-visualizer"
USER_ID = "local-tester"
REQUEST = "Summarize episode insulin-pcos-101"
 
 
async def main() -> None:
    runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
 
    # A session is the container for one conversation's state/history.
    session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )
 
    print(f"Sending request: {REQUEST}")
    message = types.Content(role="user", parts=[types.Part(text=REQUEST)])
 
    # run_async yields events as the pipeline executes: model text,
    # tool calls (MCP + agent-tools), and tool results. We print the
    # text parts so the run is observable in the terminal.
    async for event in runner.run_async(
        user_id=USER_ID, session_id=session.id, new_message=message
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text)
 
    print("\nAgent interaction finished.")
 
 
if __name__ == "__main__":
    asyncio.run(main())
 
