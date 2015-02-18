import email
import imaplib

from quopri import decodestring
from time import strptime, strftime
from email.header import decode_header
from base64 import b64decode, urlsafe_b64encode

from .. import JMailBase
from ..error import JMailError


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
                if c is None:
                    items.append(s.decode())
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
            if len(v) > 30:
                v = v[:30] + '..'
            hs[k] = v
        return hs

    def __str__(self):
        return str(self._data)


class JMailMessage(JMailBase):
    flags = None
    flags_short = None
    size = None
    headers = None
    headers_short = None
    body = None
    body_html = None
    attachs = None
    uid = None
    seen = None
    mdir_cache = None

    def __init__(self, meta=None, source=None, uid=None):
        self.__init_empty()
        self.uid = uid
        if meta is not None:
            self.flags = self._flags_parse(meta)
            self.flags_short = self._flags_short(self.flags)
        if source is not None:
            self.body, self.body_html = self._parse_message(source)
            self.headers_short = self.headers.short()
            self.size = len(source)
        self.__mdir_cache_init()


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
        self.flags = list()
        self.body = self.body_html = ''
        self.headers = JMailMessageHeaders()
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
        return flags


    def _flags_short(self, flags):
        self.log.dbg('flags short')
        fs = ''
        # -- attachs
        if self.attachs and len(self.attachs) > 0:
            fs += 'A'
        else:
            fs += '.'
        # -- replied
        if b'\\Answered' in flags:
            fs += 'R'
        else:
            fs += '.'
        return fs


    def _parse_message(self, data):
        self.log.dbg('parse message: ', type(data))
        self.attachs = list()
        attach_no = 0
        if type(data) is str:
            data = data.encode()
        msg = email.message_from_bytes(data)
        self.headers = JMailMessageHeaders(msg.items())
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
                charset = self._charset_get(part)
                tenc = part.get('content-transfer-encoding', None)
                if subtype == 'plain':
                    # -- text plain
                    #~ msg_text = self._text_encoding(part.get_payload(), tenc, charset).splitlines()
                    msg_text = part.get_payload(decode=True)
                elif subtype == 'html':
                    # -- text html
                    msg_html = self._text_encoding(part.get_payload(), tenc, charset)
        del msg
        return (msg_text, msg_html)


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
        return part.get_param('charset', JMailBase.charset)


    def _text_encoding(self, text, transfer_encoding, charset):
        self.log.dbg('text encoding')
        # -- quoted-printable
        if transfer_encoding == 'quoted-printable':
            text = decodestring(text.encode()).decode(charset)
        # -- base64
        elif transfer_encoding == 'base64':
            text = b64decode(text.encode()).decode(charset)
        return text


    def size_human(self):
        return JMailBase.bytes2human(self.size)


    def body_lines(self):
        return self.body.splitlines()


    def flags_store(self, flags, command='+FLAGS'):
        self.log.dbg('msg flags store: ', flags)
        typ, data = self.imap.uid('STORE', self.uid, command, '({})'.format(flags))
        self.log.dbg('store: ', typ, data)
        if data is not None:
            self._flags_parse(data[0])
            self.mdir_cache.msg_flags_set(self.uid, data[0])


    def flag_seen(self):
        if not self.seen:
            self.flags_store('\\Seen')
