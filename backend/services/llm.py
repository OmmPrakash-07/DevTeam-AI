import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage
from openai import OpenAI
import anthropic

load_dotenv()


# ============================================================
# GEMINI
# ============================================================

def get_gemini():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return None

    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=api_key
    )


# ============================================================
# GROQ
# ============================================================

def get_groq():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return None

    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )


# ============================================================
# DEEPSEEK
# ============================================================

def get_deepseek():
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        return None

    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )


# ============================================================
# CLAUDE
# ============================================================

def get_claude():
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        return None

    return anthropic.Anthropic(
        api_key=api_key
    )


# ============================================================
# OPENROUTER
# ============================================================

def get_openrouter():
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        return None

    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )


# ============================================================
# RESPONSE EXTRACTION
# ============================================================

def extract_openai_response(response):
    try:
        content = response.choices[0].message.content

        if content is None:
            raise RuntimeError(
                "Provider returned no message content."
            )

        content = str(content).strip()

        if not content:
            raise RuntimeError(
                "Provider returned empty message content."
            )

        return content

    except Exception as error:
        raise RuntimeError(
            f"Could not extract provider response: {error}"
        )


def extract_deepseek_response(response):
    try:
        content = response.output_text

        if content is None:
            raise RuntimeError(
                "DeepSeek returned no message content."
            )

        content = str(content).strip()

        if not content:
            raise RuntimeError(
                "DeepSeek returned empty message content."
            )

        return content

    except Exception as error:
        raise RuntimeError(
            f"Could not extract DeepSeek response: {error}"
        )


def extract_claude_response(response):
    try:
        if not response.content:
            raise RuntimeError(
                "Claude returned empty content."
            )

        first_block = response.content[0]

        if hasattr(first_block, "text"):
            content = first_block.text

        elif isinstance(first_block, dict):
            content = first_block.get("text", "")

        else:
            content = str(first_block)

        content = str(content).strip()

        if not content:
            raise RuntimeError(
                "Claude returned empty message content."
            )

        return content

    except Exception as error:
        raise RuntimeError(
            f"Could not extract Claude response: {error}"
        )


# ============================================================
# PROVIDER CALLS
# ============================================================

def call_gemini(prompt):
    llm = get_gemini()

    if llm is None:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    response = llm.invoke(prompt)

    if not response.content:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return str(response.content).strip()


def call_groq(prompt):
    client = get_groq()

    if client is None:
        raise RuntimeError(
            "GROQ_API_KEY is not configured."
        )

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=4000
    )

    return extract_openai_response(response)


def call_deepseek(prompt):
    client = get_deepseek()

    if client is None:
        raise RuntimeError(
            "DEEPSEEK_API_KEY is not configured."
        )

    response = client.responses.create(
        model="deepseek-flash",
        input=prompt
    )

    return extract_deepseek_response(response)


def call_claude(prompt):
    client = get_claude()

    if client is None:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not configured."
        )

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=4000,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return extract_claude_response(response)


def call_openrouter(prompt):
    client = get_openrouter()

    if client is None:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not configured."
        )

    response = client.chat.completions.create(
        model="anthropic/claude-sonnet-5",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=4000
    )

    return extract_openai_response(response)


# ============================================================
# MAIN LLM ROUTER
# ============================================================

def invoke_llm(prompt: str):

    providers = [
        ("Gemini", call_gemini),
        ("Groq", call_groq),
        ("DeepSeek", call_deepseek),
        ("Claude", call_claude),
        ("OpenRouter", call_openrouter),
    ]

    errors = []

    for provider_name, provider_function in providers:

        print(f"\n🤖 Trying {provider_name}...")

        try:

            response = provider_function(prompt)

            if not response:
                raise RuntimeError(
                    f"{provider_name} returned an empty response."
                )

            print(
                f"✅ {provider_name} responded successfully."
            )

            # IMPORTANT:
            # Existing agents use response.content
            return AIMessage(
                content=str(response)
            )

        except Exception as error:

            error_text = str(error)

            errors.append(
                f"{provider_name}: {error_text}"
            )

            print(
                f"⚠️ {provider_name} failed:"
            )

            print(error_text)

            continue

    # ========================================================
    # ALL PROVIDERS FAILED
    # ========================================================

    raise RuntimeError(
        "All LLM providers failed.\n\n"
        + "\n".join(errors)
    )