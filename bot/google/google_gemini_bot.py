"""
Google gemini bot

@author zhayujie
@Date 2023/12/15
"""
# encoding:utf-8

from bot.bot import Bot
import google.generativeai as genai
from bot.session_manager import SessionManager
from bridge.context import ContextType, Context
from bridge.reply import Reply, ReplyType
from bot.baidu.baidu_wenxin_session import BaiduWenxinSession
from common.utils import *

# OpenAI对话模型API (可用)
class GoogleGeminiBot(Bot):

    def __init__(self):
        super().__init__()
        self.api_key = conf().get("gemini_api_key")
        self.model = genai.GenerativeModel(conf().get("model") or "gemini-pro")
        # 复用文心的token计算方式
        self.sessions = SessionManager(BaiduWenxinSession, model=conf().get("model") or "gemini-pro")

    def reply(self, query, context: Context = None) -> Reply:
        try:
            if context.type == ContextType.TEXT:
                logger.info(f"[Gemini] query={query}")
                session_id = context["session_id"]
                session = self.sessions.session_query(query, session_id)
                gemini_messages = self._convert_to_gemini_messages(self._filter_messages(session.messages))
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(gemini_messages)
                reply_text = response.text
                self.sessions.session_reply(reply_text, session_id)
                logger.info(f"[Gemini] reply={reply_text}")
                return Reply(ReplyType.TEXT, reply_text)
            elif context.type == ContextType.SHARING:
                logger.info(f"[Gemini] query={query}")
                session_id = context["session_id"]

                # 解析请求链接
                text = get_url_content(query)
                logger.debug("[Gemini] article text length={}, text={}".format(len(text), text))

                if len(text) < 50:
                    logger.debug("[Gemini] article text length={}, text={}".format(len(text), text))
                    reply = Reply(ReplyType.INFO, "提取文章内容失败！")
                    return reply

                # 根据提示语生成新的 请求
                prompt = conf().get("prompts")[conf().get("summarize_user_prompt")].format(text=text)

                self.sessions.clear_session(session_id)
                session = self.sessions.session_query(prompt, session_id)
                logger.debug("[Gemini] session query={}".format(session.messages))
                gemini_messages = self._convert_to_gemini_messages(self._filter_messages(session.messages))
                logger.debug("[Gemini] session query={}".format(gemini_messages))

                genai.configure(api_key=self.api_key)
                #model = genai.GenerativeModel('gemini-pro')

                response = self.model.generate_content(gemini_messages)
                logger.debug("[Gemini] session query={}".format(self.model))
                logger.debug(
                    "[Gemini] new_query={}, session_id={}, reply_cont={}, prompt_feedback={}".format(
                        gemini_messages,
                        session_id,
                        len(response.text),
                        response.prompt_feedback,
                    )
                )
                self.sessions.clear_session(session_id)

                reply = Reply(ReplyType.TEXT, response.text)
                return reply

            else:
                logger.warn(f"[Gemini] Unsupported message type, type={context.type}")
                return Reply(ReplyType.TEXT, None)
        except Exception as e:
            logger.error("[Gemini] fetch reply error, may contain unsafe content")
            logger.error(e)

    def _convert_to_gemini_messages(self, messages: list):
        res = []
        for msg in messages:
            if msg.get("role") == "user":
                role = "user"
            elif msg.get("role") == "assistant":
                role = "model"
            else:
                continue
            res.append({
                "role": role,
                "parts": [{"text": msg.get("content")}]
            })
        return res

    def _filter_messages(self, messages: list):
        res = []
        turn = "user"
        for i in range(len(messages) - 1, -1, -1):
            message = messages[i]
            if message.get("role") != turn:
                continue
            res.insert(0, message)
            if turn == "user":
                turn = "assistant"
            elif turn == "assistant":
                turn = "user"
        return res
