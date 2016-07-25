from .. import JMailBase
from email.message import Message
from email import policy, message_from_bytes

class JMailMsgParser(Message, JMailBase):
    """class to parse email messages"""

    def parse(self, blob):
        """parse email content as binary/bytes source"""
        m = message_from_bytes(blob, policy=policy.default)
        self.log.dbg('Parsed message blob: ', type(blob), ' - charsets: ',
                m.get_content_charset(), ' - ', m.get_charset(),
                ' - ', m.get_charsets())
        return m
