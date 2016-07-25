import imaplib

from .. import JMailBase
from .parser import JMailMessageDistParser, JMailMsgParser
from email.iterators import typed_subpart_iterator

class JMailMessage(JMailBase):
    _m = None
    flags = None
    flags_short = None
    size = None
    headers = None
    headers_short = None
    body_html = None
    attachs = None
    uid = None
    seen = None
    mdir_cache = None

    def __init__(self, meta=None, source=None, uid=None):
        self.uid = uid
        self.__init_empty()
        self.__mdir_cache_init()
        if meta is not None:
            self.flags = self._flags_parse(meta)
            self.flags_short = self._flags_short(self.flags)
        if source is not None:
            self.body_html = self._parse_message(source)
            self.headers_short = self.headers.short()
            self.size = len(source)


    def __str__(self):
        return '(.headers={})'.format(self.headers)


    def __repr__(self):
        return str({
            'flags': self.flags,
            'seen': self.seen,
            'size': self.size,
            'uid': self.uid,
        })


    def __init_empty(self):
        self.flags = tuple()
        self.headers_short = dict()
        self.flags_short = dict()
        self.size = 0


    def __mdir_cache_init(self):
        from ..mdir import JMailMDirCache
        self.mdir_cache = JMailMDirCache


    def _flags_parse(self, fs):
        self.log.dbg('flags parse: ', fs)
        flags = imaplib.ParseFlags(fs)
        if b'\\Seen' in flags:
            self.seen = True
        self.log.dbg('flags: ', flags)
        return flags


    def _flags_short(self, flags):
        self.log.dbg('flags short')
        fs = ''
        # -- attachs
        if self.attachs and len(self.attachs) > 0:
            fs += 'A'
        # -- replied
        if b'\\Answered' in flags:
            fs += 'R'
        return fs


    def _parse_message(self, data):
        self.log.dbg('message parse data: ', type(data))
        msg = JMailMessageDistParser()
        msg.parse(data)
        self.headers = msg.headers
        msg_html = msg.body_html
        self.attachs = msg.attachs
        self.charset = msg.charset
        del msg
        # --- parser next generation
        p = JMailMsgParser()
        self._m = p.parse(data) # should return m instead of setting self._m
        return msg_html


    def size_human(self):
        return JMailBase.bytes2human(self.size)

    # --- parser next generation

    def get_source(self):
        return self._m.as_string()

    def get_charset(self):
        return self._m.get_content_charset()

    def body_lines(self):
        """return a list of message body lines"""
        if self._m.is_multipart():
            payload = '(multipart message)'
            for p in typed_subpart_iterator(self._m, maintype='text', subtype='plain'):
                payload = p.get_payload(decode=True)
                break # pick up the first one!
            return payload.splitlines()
        else:
            payload = self._m.get_payload(decode=True)
            return payload.decode(self.get_charset()).splitlines()
