"""
channel factory
"""


def create_bot(bot_type):
    """
    create a bot_type instance
    :param bot_type: bot type code
    :return: bot instance
    """
    if bot_type == "openai":
        from bot.openai.openai_bot import OpenAIBot
        return OpenAIBot()
    elif bot_type == "gemini":
        from bot.google.google_gemini_bot import GoogleGeminiBot
        return GoogleGeminiBot()
    elif bot_type == "claude":
        from bot.claude.claude_ai_bot import ClaudeAIBot
        return ClaudeAIBot()
    raise RuntimeError
