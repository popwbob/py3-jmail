import email
from quopri import decodestring
from jmail import JMailBase


SHOW_HEADERS = [
    #~ 'x-spam-level',
    'date',
    'from',
    'to',
    'cc',
    'subject',
]


class JMailMessage:
    uid = None
    _honly = None
    _imap = None
    _msg = None
    log = None
    source = None
    headers = None
    headers_full = None
    flags = None
    body = None
    body_parts = None
    size = None
    prop = None


    def __init__(self, mail_uid=None, headers_only=False, imap=None):
        self.log = JMailBase.log
        self.log.dbg('msg init')
        self.uid = mail_uid
        self._honly = headers_only
        self._imap = JMailBase.imap
        if imap is not None:
            self._imap = imap


    def fetch(self, mail_uid=None, headers_only=None):
        fetch_cmd = 'BODY[]'
        if mail_uid is not None:
            self.uid = mail_uid
        if headers_only is not None:
            self._honly = headers_only
        if self._honly:
            fetch_cmd = 'BODY.PEEK[HEADER]'

        self.log.dbg('msg.fetch: ', fetch_cmd, ' ', self.uid, ' honly:', self._honly)
        typ, mdata = self._imap.uid('FETCH', self.uid, '(FLAGS {})'.format(fetch_cmd))

        self._msg = email.message_from_bytes(mdata[0][1])
        #~ self.log.dbg('msg: ', type(self._msg), ' ', sorted(dir(self._msg)))
        self.log.dbg('msg multipart: ', self._msg.is_multipart())

        self.source = self._msg.as_string()
        self.log.dbg('msg source: ', type(self.source))

        self.headers_full = self._msg.items()
        self.headers = self._headers_filter(self.headers_full)

        self.flags = self._flags_get(mdata[0][0])
        self.body = self._body_get(self._msg)


    def _flags_get(self, mdata):
        self.log.dbg('msg flags get')
        self.size = mdata.split()[-1]
        return [f.decode().replace('(', '').replace(')', '') for f in mdata.split()[4:][:-2]]


    def _headers_filter(self, headers):
        self.log.dbg('msg headers filter')
        f = list()
        header_keys = sorted([h[0].lower() for h in headers])
        for hk in SHOW_HEADERS:
            if hk.lower() in header_keys:
                hv = None
                for h in headers:
                    if h[0].lower() == hk:
                        hv = h[1]
                f.append((hk.capitalize(), hv))
        return f


    def _msg_properties(self, msg):
        self.log.dbg('msg properties')
        prop = {
            #~ 'default_type': msg.get_default_type(),
            'content_type': msg.get_content_type(),
            'content_maintype': msg.get_content_maintype(),
            'content_subtype': msg.get_content_subtype(),
            'content_charset': msg.get_content_charset(),
            'charset': msg.get_charset(),
            #~ 'charsets': msg.get_charsets(),
            #~ 'params': msg.get_params(),
            #~ 'unixfrom': msg.get_unixfrom(),
            'filename': msg.get_filename(),
            'transfer_encoding': None,
            'disposition': None,
        }
        msg_keys = msg.keys()
        # -- content type
        try:
            idx = msg_keys.index('Content-Type')
        except ValueError:
            idx = None
        if idx is not None:
            d = msg.values()[idx]
            ct = d.split(';')[0].strip()
            cs = d.split(';')[1].strip()
            prop['content_type'] = ct
            k, v = cs.split('=')
            if k == 'charset':
                prop['charset'] = v
        # -- transfer encoding
        try:
            idx = msg_keys.index('Content-Transfer-Encoding')
        except ValueError:
            idx = None
        if idx is not None:
            prop['transfer_encoding'] = msg.values()[idx]
        # -- disposition
        try:
            idx = msg_keys.index('Content-Disposition')
        except ValueError:
            idx = None
        if idx is not None:
            prop['disposition'] = msg.values()[idx]
        return prop


    def _text_plain(self, msg):
        text = msg.get_payload()
        self.log.dbg('msg text: ', type(text))
        # -- quoted-printable
        if self.prop['transfer_encoding'] == 'quoted-printable':
            self.log.dbg('text quoted-printable')
            text = decodestring(text.encode()).decode(self.prop['charset'])
        return text


    def _body_text(self, msg):
        self.log.dbg('msg body text')
        self.log.dbg('msg boundary: ', msg.get_boundary())
        #~ self.log.dbg('msg attach: ', msg.attach)
        #~ self.log.dbg('msg defects: ', msg.defects)
        #~ self.log.dbg('msg epilogue: ', msg.epilogue)
        #~ self.log.dbg('msg preamble: ', msg.preamble)
        self.log.dbg('msg keys: ', msg.keys())
        self.log.dbg('msg values: ', msg.values())
        self.prop = self._msg_properties(msg)
        self.log.dbg('msg.prop: ', self.prop)
        text = None
        msg_subtype = msg.get_content_subtype()
        if msg_subtype == 'plain':
            self.log.dbg('subtype plain')
            text = self._text_plain(msg)
        elif msg_subtype == 'html':
            self.log.dbg('subtype html')
            self.body_parts.append('text/html')
        return text


    def _body_get(self, body):
        self.log.dbg('msg body get')
        if self._honly:
            return '[HEADERS ONLY]'
        self.body_parts = list()
        if body.is_multipart():
            return self._body_parts(body)
        else:
            self.log.dbg('body content main type: ', body.get_content_maintype())
            text = None
            if body.get_content_maintype() == 'text':
                text = self._body_text(body)
            if text is None:
                return '[NO TEXT CONTENT]'
            else:
                return text


    def _body_parts(self, body):
        self.log.dbg('msg body parts')
        text = None
        for part in body.walk():
            self.log.dbg('part content type: ', part.get_content_type())
            if part.get_content_maintype() == 'text':
                self.log.dbg('part maintype text')
                r = self._body_text(part)
                if r is not None:
                    text = r
        if text is None:
            text = '[NO PLAIN TEXT CONTENT]'
        return text


    def __str__(self):
        self.log.dbg('msg str')
        try:
            return 'JMailMessage({}: {})'.format(self.headers[0][0], self.headers[0][1])
        except:
            return 'JMailMessage'
