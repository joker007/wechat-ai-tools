from bot.bot_factory import create_bot
from bridge.context import Context
from bridge.reply import Reply
from common.log import logger
from common.singleton import singleton
from common.config import conf


# from translate.factory import create_translator
# from voice.factory import create_voice


@singleton
class Bridge(object):
    def __init__(self):
        # 读取各平台场景模型
        self.platforms = conf().get("platforms")
        # 获取当前配置平台bot
        self.bot_type = conf().get("bot")
        # 保存实例化bot对象
        self.bots = {}
        #
        self.chat_bots = {}

    def get_bot(self, typename):
        if self.bots.get(typename) is None:
            logger.info("create bot {} for {}".format(self.bot_type, typename))
            if typename in ["openai", "gemini"]:
                self.bots[typename] = create_bot(typename)
        return self.bots[typename]

    def get_bot_type(self):
        return self.bot_type

    # TEXT回复
    def fetch_reply_content(self, query, context: Context) -> Reply:
        return self.get_bot(self.bot_type).reply(query, context)

    # SHARING回复
    def fetch_url_to_content(self, query, context: Context) -> Reply:
        return self.get_bot(self.bot_type).reply(query, context)

    # FILE回复
    def fetch_file_to_content(self, query, context: Context) -> Reply:
        return self.get_bot(self.bot_type).reply(query, context)

    def fetch_voice_to_text(self, voiceFile) -> Reply:
        return self.get_bot("voice_to_text").voiceToText(voiceFile)

    def fetch_text_to_voice(self, text) -> Reply:
        return self.get_bot("text_to_voice").textToVoice(text)

    def fetch_translate(self, text, from_lang="", to_lang="en") -> Reply:
        return self.get_bot("translate").translate(text, from_lang, to_lang)

    def find_chat_bot(self, bot_type: str):
        if self.chat_bots.get(bot_type) is None:
            self.chat_bots[bot_type] = create_bot(bot_type)
        return self.chat_bots.get(bot_type)

    def reset_bot(self):
        """
        重置bot路由
        """
        self.__init__()
