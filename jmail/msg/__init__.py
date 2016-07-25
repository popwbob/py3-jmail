import imaplib
from email.header import decode_header
from time import strptime, strftime
from .. import JMailBase
from .parser import JMailMsgParser
from email.iterators import typed_subpart_iterator
from base64 import urlsafe_b64encode


class JMailMessageHeaders(JMailBase):
    _data = None

    def __init__(self, data=[], charset=None):
        self._data = data
        if charset is not None:
            self.charset = charset
        self.log.dbg('MsgHeaders charset: ', self.charset)

    def __len__(self):
        return len(self._data)

    def _parse_key(self, k):
        k = k.lower()
        return k.replace('-', '_')

    def __getitem__(self, k):
        return self.get(k)

    def __contains__(self, k):
        k = self._parse_key(k)
        return k in [self._parse_key(hk) for hk, hv in self._data]

    def set_hdr(self, k, v):
        for hk, hv in self._data:
            if self._parse_key(hk) == self._parse_key(k):
                self._data.remove((hk, hv))
        self._data.append((k, v))

    def get(self, k, d=''):
        k = self._parse_key(k)
        for hk, hv in self._data:
            if self._parse_key(hk) == k:
                return self._hdecode(hv)
        return d

    def get_raw(self, k, d=None):
        k = self._parse_key(k)
        for hk, hv in self._data:
            if self._parse_key(hk) == k:
                return hv
        return d

    def _hdecode(self, hval):
        l = decode_header(hval)
        #~ self.log.dbg('hdecode: ', hval, ' ', l)
        items = list()
        for t in l:
            s = t[0]
            c = t[1]
            if type(s) is str:
                items.append(s)
            else:
                if c is None or c.startswith('unknown'):
                    if isinstance(s, str):
                        items.append(s)
                    else:
                        try:
                            items.append(s.decode(self.charset))
                        except UnicodeDecodeError as e:
                            self.log.error("message header decode: ", e)
                            items.append(str(s))
                else:
                    items.append(s.decode(c))
        r = ' '.join(items)
        #~ self.log.dbg('hdecode return: ', r)
        return r

    def short(self):
        #~ self.log.dbg('headers short')
        hs = dict()
        # -- date
        hdate = self.get_raw('date')
        if hdate is None:
            hs['date'] = ''
        else:
            dstring = ' '.join(hdate.split()[:6])
            dobj = strptime(dstring, JMailBase.conf.get('DATE_HEADER_FORMAT'))
            hs['date'] = strftime('%Y%m%d %H:%M', dobj)
        # -- from, to, subject
        for k in ('from', 'to', 'subject'):
            v = self.get(k)
            if len(v) > 128:
                v = v[:128] + '..'
            hs[k] = v
        return hs

    def __str__(self):
        return str(self._data)


class JMailMessage(JMailBase):
    _m = None
    flags = None
    flags_short = None
    size = None
    headers = None
    headers_short = None
    uid = None
    seen = None


    def __init__(self, meta=None, source=None, uid=None):
        self.uid = uid
        self.__init_empty()
        if meta is not None:
            self.flags = self._flags_parse(meta)
            self.flags_short = self._flags_short(self.flags)
        if source is not None:
            self._m = self._parse_message(source)
            self.headers = JMailMessageHeaders(
                    self._m.items(), self.get_charset())
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
        # TODO: add attachs short flag if there are non text/ parts in msg
        # -- replied
        if b'\\Answered' in flags:
            fs += 'R'
        return fs


    def _parse_message(self, data):
        self.log.dbg('message parse data: ', type(data))
        return JMailMsgParser().parse(data)


    def size_human(self):
        return self.bytes2human(self.size)


    def get_charset(self):
        """return message charset (or try to guess)"""
        cs = self._m.get_content_charset()
        if cs is None:
            cs = self._m.get_charset()
            if cs is None:
                for cs in self._m.get_charsets():
                    if cs is not None: break
        if cs is None:
            self.log.dbg('Msg guessing default charset')
            cs = self.charset # jmail default
        self.log.dbg('Msg got charset: ', cs)
        return cs


    def source_lines(self):
        return self._m.as_string().splitlines()


    def body_lines(self):
        """return a list of message body lines"""
        if self._m.is_multipart():
            payload = '(multipart message)'
            for p in typed_subpart_iterator(self._m, maintype='text', subtype='plain'):
                payload = p.get_payload(decode=True)
                break # pick up the first one!
            self.log.dbg('Msg multipart body lines: ', len(payload))
        else:
            payload = self._m.get_payload(decode=True)
            self.log.dbg('Msg body lines: ', type(payload), len(payload))
        return payload.decode(self.get_charset()).splitlines()


    def body_html(self):
        """return message html body (if any)"""
        if self._m.is_multipart():
            payload = '(multipart message)'
            for p in typed_subpart_iterator(self._m, maintype='text', subtype='html'):
                payload = p.get_payload(decode=True)
                break # pick up the first one!
            self.log.dbg('Msg multipart body html: ', len(payload))
        else:
            payload = self._m.get_payload(decode=True)
            self.log.dbg('Msg body html: ', len(payload))
        return payload.decode(self.get_charset())


    def parts(self):
        pl = list()
        idx = 0
        for p in self._m.walk():
            if p.get_content_maintype() == 'multipart':
                continue
            pl.append(JMailMessage(source=p.as_bytes(), uid=idx))
            idx += 1
        return pl


    def content_type(self):
        return self._m.get_content_type()


    def filename(self):
        ctype = self.content_type()
        fn = self._m.get_filename()
        if not fn:
            if not ctype.startswith('text/'):
                ext = mimetypes.guess_extension(ctype)
                if not ext:
                    ext = '.bin'
                fn = 'part-{}{}'.format(self.uid, ext)
        return fn

    def filename_encode(self):
        return urlsafe_b64encode(self.filename().encode()).decode()
