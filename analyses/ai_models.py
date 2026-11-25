"""The models offered for CV analysis. To add a model of an existing provider, add one entry here."""

from django.conf import settings

DEFAULT_AI_MODEL = "openai"

AI_MODELS = {
    "openai": {
        "label": "GPT-5.6 Sol",
        "provider": "openai",
        "model": settings.OPENAI_MODEL,
        "reasoning_effort": "high",
    },
    "openai-sol62": {
        "label": "GPT-6.2 Sol",
        "provider": "openai",
        "model": settings.OPENAI_SOL62_MODEL,
        "reasoning_effort": "high",
    },
    "deepseek-flash": {
        "label": "DeepSeek V4.1 Flash 1017",
        "provider": "deepseek",
        "model": settings.DEEPSEEK_FLASH_MODEL,
        "reasoning_effort": "high",  # "max" took about 77 seconds in testing, "high" about 30
    },
}
