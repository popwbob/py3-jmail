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
    _muid = None
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


    def __init__(self, mail_uid=None, headers_only=False, imap=None):
        self._muid = mail_uid
        self._honly = headers_only
        self._imap = JMailBase.imap
        if imap is not None:
            self._imap = imap
        self.log = JMailBase.log
        self.log.dbg('JMailMessage created')
        self._fetch_cmd = 'BODY[]'


    def fetch(self, mail_uid=None, headers_only=None):
        if mail_uid is not None:
            self._muid = mail_uid
        if headers_only is not None:
            self._honly = headers_only
            self._fetch_cmd = 'BODY.PEEK[HEADER]'
        self.log.dbg('JMailMessage mail_uid: ', self._muid)
        self.log.dbg('JMailMessage headers_only: ', self._honly)
        self.log.dbg('JMailMessage imap: ', self._imap)
        self.log.dbg('JMailMessage fetch_cmd: ', self._fetch_cmd)
        typ, mdata = self._imap.uid('FETCH', self._muid, '(FLAGS {})'.format(self._fetch_cmd))
        self.body_raw = email.message_from_bytes(mdata[0][1])
        self.log.dbg('body_raw multipart: ', self.body_raw.is_multipart())
        self.headers_full = self.body_raw.items()
        self.headers = self._headers_filter(self.headers_full)
        self.body = self._body_get(self.body_raw)


    def _headers_filter(self, headers):
        f = list()
        for hk, hv in headers:
            if hk.lower() in SHOW_HEADERS:
                f.append((hk, hv))
        return f


    def _body_get(self, body):
        if body.is_multipart():
            return self._body_parts(body)
        else:
            self.log.dbg('body content-type: ', body.get_content_type())
            if body.get_content_type() == 'text/plain':
                return body.get_payload()
            else:
                return body.get_payload(decode=True)


    def _body_parts(self, body):
        self.body_parts = list()
        text = None
        for part in body.walk():
            self.log.dbg('part content-type: ', part.get_content_type())
            if part.get_content_type() == 'text/plain':
                self.log.dbg('part used as body')
                return part.get_payload()
            else:
                self.body_parts.append(part)
        return text


    def __str__(self):
        return '{}{}'.format(self.headers, self.body)
