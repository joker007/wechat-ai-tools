from bot.bot_factory import create_bot
from bridge.context import Context
from bridge.reply import Reply
from common.log import logger
from common.singleton import singleton
from common.config import conf
#from translate.factory import create_translator
#from voice.factory import create_voice


@singleton
class Bridge(object):
    def __init__(self):
        # self.btype = {
        #     "chat": const.CHATGPTNEW,
        #     "url_to_content": const.CHATGPTNEW,
        #     "voice_to_text": conf().get("voice_to_text", "openai"),
        #     "text_to_voice": conf().get("text_to_voice", "google"),
        #     "translate": conf().get("translate", "baidu"),
        # }
        self.bot_type = conf().get("bot")
        #model_type = conf().get("model")
        # if model_type in ["text-davinci-003"]:
        #     self.btype["chat"] = const.OPEN_AI
        # if conf().get("use_azure_chatgpt", False):
        #     self.btype["chat"] = const.CHATGPTONAZURE
        # if model_type in ["wenxin"]:
        #     self.btype["chat"] = const.BAIDU
        # if model_type in ["xunfei"]:
        #     self.btype["chat"] = const.XUNFEI
        # if conf().get("use_linkai") and conf().get("linkai_api_key"):
        #     self.btype["chat"] = const.LINKAI
        # if model_type in ["claude"]:
        #     self.btype["chat"] = const.CLAUDEAI
        self.bots = {}
        self.chat_bots = {}

    def get_bot(self, typename):
        if self.bots.get(typename) is None:
            logger.info("create bot {} for {}".format(self.bot_type, typename))
            if typename == "openai":
                self.bots[typename] = create_bot(self.bot_type)
        return self.bots[typename]

    def get_bot_type(self, typename):
        return self.btype[typename]

    def fetch_reply_content(self, query, context: Context) -> Reply:
        return self.get_bot("openai").reply(query, context)

    def fetch_url_to_content(self, query, context: Context) -> Reply:
        return self.get_bot("openai").reply(query, context)

    def fetch_file_to_content(self, query, context: Context) -> Reply:
        return self.get_bot("openai").reply(query, context)

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
