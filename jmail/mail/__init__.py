import email

from jmail import JMailBase

SHOW_HEADERS = [
    'x-spam-level',
    'date',
    'subject',
    'from',
    'to',
]


class JMailMessage:
    uid = None
    _honly = None
    _imap = None
    _fetch_cmd = None
    _raw = None
    log = None
    headers = None
    headers_full = None
    flags = None
    body = None
    body_parts = None
    size = None


    def __init__(self, mail_uid=None, headers_only=False, imap=None):
        self.uid = mail_uid
        self._honly = headers_only
        self._imap = JMailBase.imap
        if imap is not None:
            self._imap = imap
        self.log = JMailBase.log
        self.log.dbg('JMailMessage created')
        self._fetch_cmd = 'BODY[]'


    def fetch(self, mail_uid=None, headers_only=None):
        if mail_uid is not None:
            self.uid = mail_uid
        if headers_only is not None:
            self._honly = headers_only
            self._fetch_cmd = 'BODY.PEEK[HEADER]'

        self.log.dbg('JMailMessage mail_uid: ', self.uid)
        self.log.dbg('JMailMessage headers_only: ', self._honly)
        self.log.dbg('JMailMessage imap: ', self._imap)
        self.log.dbg('JMailMessage fetch_cmd: ', self._fetch_cmd)
        typ, mdata = self._imap.uid('FETCH', self.uid, '(FLAGS {})'.format(self._fetch_cmd))

        self.body_raw = email.message_from_bytes(mdata[0][1])
        self.log.dbg('body_raw multipart: ', self.body_raw.is_multipart())

        self.headers_full = self.body_raw.items()
        self.headers = self._headers_filter(self.headers_full)

        self.body = self._body_get(self.body_raw)
        self.flags = self._flags_get(mdata[0][0])


    def _flags_get(self, mdata):
        self.size = mdata.split()[-1]
        return [f.decode().replace('(', '').replace(')', '') for f in mdata.split()[4:][:-2]]


    def _headers_filter(self, headers):
        f = list()
        for hk, hv in headers:
            if hk.lower() in SHOW_HEADERS:
                f.append((hk, hv))
        return f


    def _body_text(self, msg):
        self.log.dbg('body_text msg: ', dir(msg))
        self.log.dbg('body_text msg default type: ', msg.get_default_type())
        self.log.dbg('body_text msg content type: ', msg.get_content_type())
        self.log.dbg('body_text msg content charset: ', msg.get_content_charset())
        self.log.dbg('body_text msg charset: ', msg.get_charset())
        self.log.dbg('body_text msg charsets: ', msg.get_charsets())
        self.log.dbg('body_text msg params: ', msg.get_params())
        self.log.dbg('body_text msg unixfrom: ', msg.get_unixfrom())
        if msg.get_content_subtype() == 'plain':
            return msg.get_payload()
        else:
            return None


    def _body_get(self, body):
        if body.is_multipart():
            return self._body_parts(body)
        else:
            self.log.dbg('body: ', sorted(dir(body)))
            self.log.dbg('body content main type: ', body.get_content_maintype())
            if body.get_content_maintype() == 'text':
                text = self._body_text(body)
            if text is None:
                return '[NO TEXT CONTENT]'
            else:
                return text


    def _body_parts(self, body):
        self.body_parts = list()
        text = None
        for part in body.walk():
            self.log.dbg('part content main type: ', part.get_content_maintype())
            if part.get_content_maintype() == 'text':
                if text is None:
                    text = self._body_text(part)
            else:
                self.body_parts.append(part.get_content_type())
        if text is None:
            text = '[NO PLAIN TEXT CONTENT]'
        return text


    def __str__(self):
        try:
            return 'JMailMessage({}: {})'.format(self.headers[0][0], self.headers[0][1])
        except:
            return 'JMailMessage'
