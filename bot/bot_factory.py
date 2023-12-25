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
    raise RuntimeError
