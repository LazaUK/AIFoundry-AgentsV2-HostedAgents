# Patch missing opentelemetry-semantic-conventions-ai attributes
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

import os
from azure.identity import DefaultAzureCredential
from agent_framework import ChatAgent, HostedMCPTool
from agent_framework_azure_ai import AzureAIAgentClient
from azure.ai.agentserver.agentframework import from_agent_framework

# Create credential ONCE at module level so token refresh works across requests
_credential = DefaultAzureCredential()

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
        credential = _credential,
        should_cleanup_agent = False,  # don't delete agent between requests
    )

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

if __name__ == "__main__":
    from_agent_framework(get_agent()).run()