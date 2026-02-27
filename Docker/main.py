import opentelemetry.semconv_ai as _semconv
_missing = {
    'LLM_REQUEST_MODEL': 'llm.request.model',
    'LLM_RESPONSE_MODEL': 'llm.response.model',
    'LLM_SYSTEM': 'llm.system',
    'LLM_TOKEN_TYPE': 'llm.usage.token_type',
    'LLM_REQUEST_MAX_TOKENS': 'llm.request.max_tokens',
    'LLM_REQUEST_TEMPERATURE': 'llm.request.temperature',
    'LLM_REQUEST_TOP_P': 'llm.request.top_p',
}
for attr, value in _missing.items():
    if not hasattr(_semconv.SpanAttributes, attr):
        setattr(_semconv.SpanAttributes, attr, value)

import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from agent_framework_azure_ai import AzureAIAgentClient
from agent_framework import HostedMCPTool, ChatMessageStore
from azure.ai.agentserver.agentframework import from_agent_framework
from azure.ai.agentserver.agentframework.persistence.agent_thread_repository import AgentThreadRepository

PROJECT_ENDPOINT = os.environ.get("AZURE_FOUNDRY_PROJECT_ENDPOINT")
MODEL_DEPLOYMENT = os.environ.get("AZURE_FOUNDRY_GPT_MODEL")

if not PROJECT_ENDPOINT or not MODEL_DEPLOYMENT:
    print("WARNING: Environment variables not set properly!")
else:
    print("Environment variables set successfully!")

class NoOpThreadRepository(AgentThreadRepository):
    """Never persists threads - each request gets a fresh thread."""
    async def get(self, conversation_id, agent=None):
        return None

    async def set(self, conversation_id, thread):
        pass

async def main():
    print("Starting main()...")
    async with DefaultAzureCredential() as credential:
        print("Credential created successfully")
        async with AzureAIAgentClient(
            project_endpoint=PROJECT_ENDPOINT,
            model_deployment_name=MODEL_DEPLOYMENT,
            credential=credential,
            should_cleanup_agent=False,
        ) as client:
            agent = client.create_agent(
                name="Microsoft Documentation Agent",
                instructions="You are an agent, which can use its MCP documentation tool to answer end user questions about Microsoft products. Limit your response to 2 paragraphs.",
                tools=HostedMCPTool(
                    name="Microsoft Learn MCP",
                    url="https://learn.microsoft.com/api/mcp",
                    approval_mode="never_require"
                ),
                chat_message_store_factory=lambda: ChatMessageStore(),  # fresh store per request, no Foundry history
            )
            print(f"Agent ready, starting server...")
            # server = from_agent_framework(agent, thread_repository=NoOpThreadRepository())
            server = from_agent_framework(agent)
            await server.run_async()

if __name__ == "__main__":
    asyncio.run(main())