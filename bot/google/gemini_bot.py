
import google.generativeai as genai

from bot.bot import Bot
from bot.session_manager import SessionManager
from bridge.context import ContextType, Context
from bridge.reply import Reply, ReplyType
from common.config import conf, load_config
from common.log import logger

class GeminiBot(Bot):
    def __init__(self):
        super().__init__()

        genai.api_key = conf.get("aip_key")


        self.args = {

        }

    def manage(self):
        pass

    def reply(self, query, context: Context = None) -> Reply:
        if context.type == ContextType.TEXT:

            #判断是否是控制命令
            reply = self.manage()
            if reply:
                return reply


        elif context.type == ContextType.SHARING:
            pass
        elif context.type == ContextType.FILE:
            pass
        else:
            reply = Reply(ReplyType.ERROR, "Bot不支持处理{}类型的消息".format(context.type))
            return reply

    def reply_text(self, api_key=None, args=None, retry_count=0) -> dict:
        """
        call google  to get the answer

        """
        try:
            if args is None:
                args = self.args
            model = genai.GenerativeModel(conf.get("model"))
            response = model.generate_content()
            logger.info("[Gemini] reply={}, total_tokens={}".format(response.choices[0].message.content,
                                                                     response.usage.total_tokens))

            return {
                "content": response.text,
            }
        except Exception as e:
            result = {"completion_tokens": 0, "content": "我现在有点累了，等会再来吧"}
            logger.exception("[CHATGPT] Exception: {}".format(e))