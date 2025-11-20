import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from agent_framework import ChatAgent, HostedMCPTool
from agent_framework_azure_ai import AzureAIAgentClient
from azure.ai.agentserver.agentframework import from_agent_framework

def get_agent() -> ChatAgent:
    """Create and return a ChatAgent with MCP tool."""

    PROJECT_ENDPOINT = os.environ.get("AZURE_FOUNDRY_PROJECT_ENDPOINT")
    MODEL_DEPLOYMENT = os.environ.get("AZURE_FOUNDRY_GPT_MODEL")
    if not PROJECT_ENDPOINT or not MODEL_DEPLOYMENT:
        print("WARNING: Environment variables not set properly!")
    else:
        print("Environment variables set successfully!")

    chat_client = AzureAIAgentClient(
        project_endpoint = PROJECT_ENDPOINT,
        model_deployment_name = MODEL_DEPLOYMENT,
        async_credential = DefaultAzureCredential(),
    )

    # Create ChatAgent with the MCP tool
    agent = chat_client.create_agent(
        name = "Microsoft Documentation Agent",
        instructions = "You are an agent, which can use its MCP documentation tool to answer end user questions about Microsoft products. Limit your response to 2 paragraphs.",
        tools = HostedMCPTool(
            name = "Microsoft Learn MCP",
            url = "https://learn.microsoft.com/api/mcp",
            approval_mode = "never_require"
        ),
    )
    return agent

async def test_agent():
    agent = get_agent()
    response = await agent.run("How do I create an Azure Function in Python?")
    print("Agent response:", response.text)

if __name__ == "__main__":
    # asyncio.run(test_agent())
    from_agent_framework(get_agent()).run()
