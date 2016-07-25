import email

from quopri import decodestring
from base64 import b64decode, urlsafe_b64encode

from .. import JMailBase


class JMailParserMsg(JMailBase):
    body_html = None
    attachs = None

    def __init__(self):
        self.body_html = ''
        self.attachs = list()


class JMailMessageDistParser(JMailParserMsg):
    def __init__(self):
        JMailParserMsg.__init__(self)

    def parse(self, data):
        self.log.dbg('parse message: ', type(data))
        attach_no = 0
        if type(data) is str:
            data = data.encode()
        msg = email.message_from_bytes(data)
        msg_text = '[NO TEXT CONTENT]'
        msg_html = '[NO HTML CONTENT]'
        for part in msg.walk():
            content_type = part.get_content_type()
            maintype = part.get_content_maintype()
            subtype = part.get_content_subtype()
            # -- multipart is just a container
            if maintype == 'multipart':
                continue
            disp = part.get('content-disposition', None)
            if disp and disp.startswith('attachment;'):
                # -- attachs
                attach_no += 1
                self._attach(part, attach_no)
            elif maintype == 'text':
                # -- text parts
                self.charset = self._charset_get(part)
                # tell headers which is the charset
                tenc = part.get('content-transfer-encoding', None)
                if subtype == 'plain':
                    # -- text plain
                    msg_text = self._text_encoding(part.get_payload(), tenc)
                elif subtype == 'html':
                    # -- text html
                    msg_html = self._text_encoding(part.get_payload(), tenc)
        del msg
        self.body = msg_text
        self.body_html = msg_html


    def _attach(self, part, attach_no):
        ctype = part.get_content_type()
        filename = part.get_filename()
        if not filename:
            ext = mimetypes.guess_extension(ctype)
            if not ext:
                ext = '.bin'
            filename = 'part-{}{}'.format(attach_no, ext)
        payload = part.get_payload(decode=True)

        #~ fh = open('/tmp/jmail-attach-{}'.format(filename), 'wb')
        #~ fh.write(payload)
        #~ fh.close()
        #~ self.log.dbg('part: ', dir(part))

        self.attachs.append({
            'content_type': ctype,
            'filename': filename,
            'filename_encode': urlsafe_b64encode(filename.encode()),
            'payload': payload,
            'size': len(payload),
            'size_human': JMailBase.bytes2human(len(payload)),
            'charset': self._charset_get(part),
            'content_disposition': part.get('content-disposition'),
            'content_transfer_encoding': part.get('content-transfer-encoding'),
        })


    def _charset_get(self, part):
        cs = part.get_param('charset', JMailBase.charset)
        self.log.dbg('parser get charset: ', cs)
        return cs


    def _text_encoding(self, text, transfer_encoding):
        self.log.dbg('text encoding')
        # -- quoted-printable
        if transfer_encoding == 'quoted-printable':
            text = decodestring(text.encode()).decode(self.charset)
        # -- base64
        elif transfer_encoding == 'base64':
            text = b64decode(text.encode()).decode(self.charset)
        return text


# --- parser next generation

from email.message import Message
from email import policy

class JMailMsgParser(Message, JMailBase):
    """class to parse email messages"""

    def parse(self, blob):
        """parse email content as binary/bytes source"""
        m = email.message_from_bytes(blob, policy=policy.default)
        self.log.dbg('Parsed message blob: ', type(m), ' - charsets: ',
                m.get_content_charset(), ' - ', m.get_charset(),
                ' - ', m.get_charsets())
        return m
