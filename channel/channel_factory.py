"""
channel factory
"""


def create_channel(channel_type):
    """
    create a channel instance
    :param channel_type: channel type code
    :return: channel instance
    """
    if channel_type == "wx":
        from channel.wechat.wechat_channel import WechatChannel

        return WechatChannel()
    raise RuntimeError
