import email

from jmail import JMailBase


class JMailMessage:
    _muid = None
    _honly = None
    _imap = None
    log = None
    headers = None
    body = None


    def __init__(self, mail_uid=None, headers_only=False, imap=None):
        self._muid = mail_uid
        self._honly = headers_only
        self._imap = JMailBase.imap
        if imap is not None:
            self._imap = imap
        self.log = JMailBase.log
        self.log.dbg('JMailMessage created')


    def fetch(self, mail_uid=None, headers_only=None):
        if mail_uid is not None:
            self._muid = mail_uid
        if headers_only is not None:
            self._honly = headers_only
        self.log.dbg('JMailMessage mail_uid: ', self._muid)
        self.log.dbg('JMailMessage headers_only: ', self._honly)
        self.log.dbg('JMailMessage imap: ', self._imap)
        self._fetch_headers()
        if not self._honly:
            self._fetch_body()


    def _fetch_headers(self):
        typ, hdata = self._imap.uid('FETCH', self._muid, '(FLAGS BODY.PEEK[HEADER])')
        self.headers = email.message_from_bytes(hdata[0][1])


    def _fetch_body(self):
        typ, mdata = self._imap.uid('FETCH', self._muid, '(FLAGS BODY[TEXT])')
        self.body = email.message_from_bytes(mdata[0][1])


    def __str__(self):
        return '{}{}'.format(self.headers, self.body)
