from typing import Dict, List

AVAILABLE_MODELS = {
    "Ollama": {
        "enabled": True,
        "models": [
            {
                "id": "gpt-oss:20b",
                "name": "GPT OSS 20B",
                "provider": "Ollama",
                "local": True,
            },
            {
                "id": "llama3.1:8b",
                "name": "Llama 3.1 8B",
                "provider": "Ollama",
                "local": True,
            },
        ],
    },

    "Groq": {
        "enabled": True,
        "models": [
            {
                "id": "openai/gpt-oss-20b",
                "name": "GPT OSS 20B",
                "provider": "Groq",
            },
            {
                "id": "llama-3.3-70b-versatile",
                "name": "Llama 3.3 70B",
                "provider": "Groq",
            },
        ],
    },

    "Gemini": {
        "enabled": True,
        "models": [
            {
                "id": "gemini-2.5-flash",
                "name": "Gemini 2.5 Flash",
                "provider": "Gemini",
            },
            {
                "id": "gemini-2.5-pro",
                "name": "Gemini 2.5 Pro",
                "provider": "Gemini",
            },
        ],
    },

    "DeepSeek": {
        "enabled": True,
        "models": [
            {
                "id": "deepseek-chat",
                "name": "DeepSeek Chat",
                "provider": "DeepSeek",
            },
            {
                "id": "deepseek-reasoner",
                "name": "DeepSeek Reasoner",
                "provider": "DeepSeek",
            },
        ],
    },

    "Claude": {
        "enabled": True,
        "models": [
            {
                "id": "claude-sonnet-4",
                "name": "Claude Sonnet",
                "provider": "Claude",
            }
        ],
    },

    "OpenRouter": {
        "enabled": True,
        "models": [
            {
                "id": "anthropic/claude-sonnet-4",
                "name": "Claude Sonnet",
                "provider": "OpenRouter",
            },
            {
                "id": "openai/gpt-4o",
                "name": "GPT-4o",
                "provider": "OpenRouter",
            },
        ],
    },
}


def get_available_models():
    return AVAILABLE_MODELS