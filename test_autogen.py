from autogen import AssistantAgent, UserProxyAgent

assistant = AssistantAgent(
    name="asistente",
    llm_config={
        "api_type": "ollama",
        "model": "qwen2.5:7b",
        "base_url": "http://localhost:11434"
    }
)

user = UserProxyAgent(name="usuario")

user.initiate_chat(
    assistant,
    message="Explica qué es Autogen en una frase."
)
