import os
import re
import time
from typing import Any, Callable, Dict

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage
from openai import OpenAI
import anthropic


load_dotenv()


# ============================================================
# Configuration
# ============================================================

DEFAULT_MAX_TOKENS = 4000

# Local Ollama
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
)

# Gemini daily quota cooldown
DAILY_QUOTA_COOLDOWN_SECONDS = 3600

# Normal temporary provider failure
DEFAULT_COOLDOWN_SECONDS = 60


# ============================================================
# Provider cooldown state
# ============================================================

_provider_cooldowns: Dict[str, float] = {}


# ============================================================
# Error / cooldown helpers
# ============================================================

def is_daily_quota_failure(error_text: str) -> bool:
    text = str(error_text).lower()

    daily_quota_patterns = [
        "generaterequestsperdaypermodel-freetier",
        "generaterequestsperdayperproject-model-freetier",
        "generate_content_free_tier_requests",
        "daily quota",
        "daily quota exceeded",
        "quota limit",
        "requests per day",
    ]

    return any(pattern in text for pattern in daily_quota_patterns)


def is_temporary_provider_failure(error_text: str) -> bool:
    text = str(error_text).lower()

    temporary_patterns = [
        "429",
        "rate limit",
        "rate_limit",
        "ratelimit",
        "too many requests",
        "resource_exhausted",
        "quota exhausted",
        "quota exceeded",
        "quota_exceeded",
        "temporarily unavailable",
        "temporarily overloaded",
        "try again later",
        "503",
        "service unavailable",
        "timeout",
        "timed out",
    ]

    return any(pattern in text for pattern in temporary_patterns)


def get_retry_delay(error_text: str) -> int:
    if is_daily_quota_failure(error_text):
        return DAILY_QUOTA_COOLDOWN_SECONDS

    text = str(error_text)

    patterns = [
        r"retry(?:\s+in)?\s*[:=]?\s*(\d+)\s*s",
        r"retryDelay['\"]?\s*[:=]\s*['\"]?(\d+)s",
        r"retry_delay['\"]?\s*[:=]\s*['\"]?(\d+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            try:
                seconds = int(match.group(1))
                return max(30, min(seconds + 5, 300))
            except ValueError:
                pass

    return DEFAULT_COOLDOWN_SECONDS


def set_provider_cooldown(
    provider_name: str,
    error_text: str,
) -> None:
    delay = get_retry_delay(error_text)

    _provider_cooldowns[provider_name] = (
        time.monotonic() + delay
    )

    print(
        f"⏸️ {provider_name} cooldown enabled for "
        f"{delay} seconds."
    )


def get_remaining_cooldown(provider_name: str) -> int:
    cooldown_until = _provider_cooldowns.get(provider_name)

    if cooldown_until is None:
        return 0

    remaining = cooldown_until - time.monotonic()

    if remaining <= 0:
        _provider_cooldowns.pop(provider_name, None)
        return 0

    return max(1, int(remaining))


def is_provider_in_cooldown(provider_name: str) -> bool:
    return get_remaining_cooldown(provider_name) > 0


# ============================================================
# Provider clients
# ============================================================

def get_gemini(max_tokens=DEFAULT_MAX_TOKENS):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return None

    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=api_key,
        max_output_tokens=max_tokens,
    )


def get_groq():
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return None

    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )


def get_deepseek():
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        return None

    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )


def get_claude():
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        return None

    return anthropic.Anthropic(
        api_key=api_key
    )


def get_openrouter():
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        return None

    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )


# ============================================================
# Response extraction
# ============================================================

def _extract_content_value(content: Any) -> str:
    if content is None:
        return ""

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, str):
                parts.append(item)

            elif isinstance(item, dict):
                text = (
                    item.get("text")
                    or item.get("content")
                    or item.get("value")
                )

                if text:
                    parts.append(str(text))

            else:
                text = getattr(item, "text", None)

                if text:
                    parts.append(str(text))

        return "\n".join(parts).strip()

    if isinstance(content, dict):
        text = (
            content.get("text")
            or content.get("content")
            or content.get("value")
        )

        if text:
            return str(text).strip()

    return str(content).strip()


def extract_gemini_response(response) -> str:
    try:
        content = getattr(
            response,
            "content",
            None,
        )

        result = _extract_content_value(content)

        if not result:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return result

    except Exception as error:
        raise RuntimeError(
            f"Could not extract Gemini response: {error}"
        ) from error


def extract_openai_response(response) -> str:
    try:
        choices = getattr(
            response,
            "choices",
            None,
        )

        if not choices:
            raise RuntimeError(
                "Provider returned no choices."
            )

        first_choice = choices[0]

        message = getattr(
            first_choice,
            "message",
            None,
        )

        if message is None:
            raise RuntimeError(
                "Provider returned no message object."
            )

        content = getattr(
            message,
            "content",
            None,
        )

        result = _extract_content_value(content)

        if not result:
            reasoning = getattr(
                message,
                "reasoning",
                None,
            )

            if reasoning:
                raise RuntimeError(
                    "Provider returned reasoning but "
                    "no final message content."
                )

            raise RuntimeError(
                "Provider returned empty message content."
            )

        return result

    except Exception as error:
        raise RuntimeError(
            f"Could not extract provider response: {error}"
        ) from error


def extract_deepseek_response(response) -> str:
    try:
        content = getattr(
            response,
            "output_text",
            None,
        )

        result = _extract_content_value(content)

        if not result:
            raise RuntimeError(
                "DeepSeek returned no message content."
            )

        return result

    except Exception as error:
        raise RuntimeError(
            f"Could not extract DeepSeek response: {error}"
        ) from error


def extract_claude_response(response) -> str:
    try:
        content_blocks = getattr(
            response,
            "content",
            None,
        )

        if not content_blocks:
            raise RuntimeError(
                "Claude returned empty content."
            )

        parts = []

        for block in content_blocks:
            if hasattr(block, "text"):
                text = block.text

            elif isinstance(block, dict):
                text = block.get("text", "")

            else:
                text = str(block)

            if text:
                parts.append(str(text))

        content = "\n".join(parts).strip()

        if not content:
            raise RuntimeError(
                "Claude returned empty message content."
            )

        return content

    except Exception as error:
        raise RuntimeError(
            f"Could not extract Claude response: {error}"
        ) from error


# ============================================================
# Ollama
# ============================================================

def call_ollama(
    prompt: str,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> str:
    """
    Call local Ollama.

    Default model:
        gpt-oss:20b

    Default API:
        http://localhost:11434
    """

    try:
        from ollama import Client

        client = Client(
            host=OLLAMA_BASE_URL
        )

        print(
            f"🦙 Ollama model: {OLLAMA_MODEL}"
        )

        response = client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": 0,
                "num_predict": min(
                    max_tokens,
                    6000,
                ),
            },
        )

        message = getattr(
            response,
            "message",
            None,
        )

        if message is None:
            raise RuntimeError(
                "Ollama returned no message."
            )

        content = getattr(
            message,
            "content",
            None,
        )

        result = _extract_content_value(content)

        if not result:
            raise RuntimeError(
                "Ollama returned an empty response."
            )

        return result

    except Exception as error:
        raise RuntimeError(
            f"Ollama failed: {error}"
        ) from error


# ============================================================
# Individual provider calls
# ============================================================

def call_gemini(
    prompt,
    max_tokens=DEFAULT_MAX_TOKENS,
):
    llm = get_gemini(
        max_tokens=max_tokens
    )

    if llm is None:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    response = llm.invoke(prompt)

    return extract_gemini_response(response)


def call_groq(
    prompt,
    max_tokens=DEFAULT_MAX_TOKENS,
):
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
                "content": prompt,
            }
        ],
        max_completion_tokens=min(
            max_tokens,
            6000,
        ),
    )

    return extract_openai_response(response)


def call_deepseek(
    prompt,
    max_tokens=DEFAULT_MAX_TOKENS,
):
    client = get_deepseek()

    if client is None:
        raise RuntimeError(
            "DEEPSEEK_API_KEY is not configured."
        )

    response = client.responses.create(
        model="deepseek-flash",
        input=prompt,
        max_output_tokens=max_tokens,
    )

    return extract_deepseek_response(response)


def call_claude(
    prompt,
    max_tokens=DEFAULT_MAX_TOKENS,
):
    client = get_claude()

    if client is None:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not configured."
        )

    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=max_tokens,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return extract_claude_response(response)


def call_openrouter(
    prompt,
    max_tokens=DEFAULT_MAX_TOKENS,
):
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
                "content": prompt,
            }
        ],
        max_tokens=max_tokens,
    )

    return extract_openai_response(response)


# ============================================================
# Main provider router
# ============================================================

def invoke_llm(
    prompt: str,
    max_tokens: int = DEFAULT_MAX_TOKENS,
):
    """
    Main LLM router.

    Priority:

    1. Ollama
    2. Groq
    3. Gemini
    4. DeepSeek
    5. Claude
    6. OpenRouter
    """

    providers: list[
        tuple[str, Callable[[str], str]]
    ] = [
        (
            "Ollama",
            lambda p: call_ollama(
                p,
                max_tokens,
            ),
        ),
        (
            "Groq",
            lambda p: call_groq(
                p,
                max_tokens,
            ),
        ),
        (
            "Gemini",
            lambda p: call_gemini(
                p,
                max_tokens,
            ),
        ),
        (
            "DeepSeek",
            lambda p: call_deepseek(
                p,
                max_tokens,
            ),
        ),
        (
            "Claude",
            lambda p: call_claude(
                p,
                max_tokens,
            ),
        ),
        (
            "OpenRouter",
            lambda p: call_openrouter(
                p,
                max_tokens,
            ),
        ),
    ]

    errors = []

    for provider_name, provider_function in providers:

        # ----------------------------------------------------
        # Skip provider during cooldown
        # ----------------------------------------------------

        remaining = get_remaining_cooldown(
            provider_name
        )

        if remaining > 0:
            print(
                f"⏭️ Skipping {provider_name} "
                f"(cooldown: {remaining}s remaining)"
            )
            continue

        print(
            f"\n🤖 Trying {provider_name}..."
        )

        try:
            response = provider_function(prompt)

            if not response:
                raise RuntimeError(
                    f"{provider_name} returned "
                    f"an empty response."
                )

            print(
                f"✅ {provider_name} responded successfully."
            )

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

            # ------------------------------------------------
            # Temporary failure -> cooldown
            # ------------------------------------------------

            if is_temporary_provider_failure(
                error_text
            ):
                set_provider_cooldown(
                    provider_name,
                    error_text,
                )

            continue

    raise RuntimeError(
        "All LLM providers failed.\n\n"
        + "\n".join(errors)
    )