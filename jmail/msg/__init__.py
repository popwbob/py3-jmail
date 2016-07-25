import imaplib
from email.header import decode_header
from time import strptime, strftime
from .. import JMailBase
from .parser import JMailMessageDistParser, JMailMsgParser
from email.iterators import typed_subpart_iterator


class JMailMessageHeaders(JMailBase):
    _data = None

    def __init__(self, data=[]):
        self._data = data

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
    body_html = None
    attachs = None
    uid = None
    seen = None


    def __init__(self, meta=None, source=None, uid=None):
        self.uid = uid
        self.__init_empty()
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
        msg_html = msg.body_html
        self.attachs = msg.attachs
        self.charset = msg.charset
        del msg
        # --- parser next generation
        p = JMailMsgParser()
        self._m = p.parse(data) # should return m instead of setting self._m
        self.headers = JMailMessageHeaders(self._m.items())
        return msg_html


    def size_human(self):
        return JMailBase.bytes2human(self.size)

    # --- parser next generation

    def get_charset(self):
        cs = self._m.get_content_charset()
        if cs is None:
            cs = self._m.get_charset()
            if cs is None:
                for cs in self._m.get_charsets():
                    if cs is not None: break
        if cs is None:
            self.log.dbg('Msg guessing default charset')
            cs = self.charset # jmail default
        self.log.dbg('Msg charset: ', cs)
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
            return payload.splitlines()
        else:
            payload = self._m.get_payload(decode=True)
            return payload.decode(self.get_charset()).splitlines()

    def parts(self):
        return self._m.walk()
