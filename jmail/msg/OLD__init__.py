import email

from email.header import decode_header
from base64 import b64decode, urlsafe_b64encode
from quopri import decodestring
from time import strftime, strptime

from jmail import JMailBase

from .future import JMailMessage2


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
    _html = None
    _ck = None
    _conf = None
    log = None
    source = None
    headers = None
    headers_full = None
    headers_short = None
    flags = None
    body = None
    body_parts = None
    size = None
    size_bytes = None
    prop = None
    attachs = None
    seen = None
    mbox_name = None


    def __init__(self, mail_uid, mbox_name, headers_only=False, imap=None, read_html=False):
        self.log = JMailBase.log
        self.log.dbg('msg init')
        if type(mail_uid) is str:
            mail_uid = mail_uid.encode()
        self.uid = mail_uid
        if type(mbox_name) is str:
            mbox_name = mbox_name.encode()
        self.mbox_name = mbox_name
        self._honly = headers_only
        self._imap = JMailBase.imap
        if imap is not None:
            self._imap = imap
        self._html = read_html
        self._ck = self.mbox_name.decode()+':'+self.uid.decode()
        self._conf = JMailBase.conf


    def fetch(self, mail_uid=None, headers_only=None):
        fetch_cmd = 'BODY[]'
        if mail_uid is not None:
            self.uid = mail_uid
        if headers_only is not None:
            self._honly = headers_only
        if self._honly:
            fetch_cmd = 'BODY.PEEK[]'

        mdata = JMailBase.cache_get(self._ck+':mdata')
        if mdata is None:
            self._imap.select(self.mbox_name)
            self.log.dbg('msg.fetch: ', fetch_cmd, ' ', self.uid, ' honly:', self._honly)
            typ, mdata = self._imap.uid('FETCH', self.uid, '(FLAGS {})'.format(fetch_cmd))
            #~ self._imap.close()
            JMailBase.cache_set(self._ck+':mdata', mdata)

        self._msg = JMailBase.cache_get(self._ck+':msg')
        if self._msg is None:
            self._msg = email.message_from_bytes(mdata[0][1])
            JMailBase.cache_set(self._ck+':msg', self._msg)

        self.log.dbg('msg multipart: ', self._msg.is_multipart())

        self.source = JMailBase.cache_get(self._ck+':source')
        if self.source is None:
            self.source = self._msg.as_string()
            JMailBase.cache_set(self._ck+':source', self.source)

        self.log.dbg('msg source: ', type(self.source))

        self.headers_full = self._msg.items()
        self.headers = self._headers_filter(self.headers_full)
        self.headers_short = self._headers_short(self.headers)

        self.body = self._body_get(self._msg)
        self.flags = self._flags_get(mdata[0][0])
        self.flags_minimal = self._flags_minimal(self.flags)


    def _flags_get(self, mdata):
        self.log.dbg('msg flags get')
        self.size_bytes = int(mdata.split()[-1][1:-1])
        self.size = JMailBase.bytes2human(self.size_bytes)
        flags = JMailBase.cache_get(self._ck+':flags')
        if flags is not None:
            return flags
        flags = [f.decode().replace('(', '').replace(')', '') for f in mdata.split()[4:][:-2]]
        JMailBase.cache_set(self._ck+':flags', flags)
        return flags


    def _flags_minimal(self, flags):
        self.log.dbg('msg flags minimal')
        # -- seen
        if '\Seen' in flags:
            self.seen = True
        fmc = JMailBase.cache_get(self._ck+':flags_minimal')
        if fmc is not None:
            return fmc
        fm = ''
        # -- attachs
        if self.attachs is not None and len(self.attachs) > 0:
            fm += 'A'
        else:
            fm += '.'
        # -- replied
        if '\Answered' in flags:
            fm += 'R'
        else:
            fm += '.'
        JMailBase.cache_set(self._ck+':flags_minimal', fm)
        return fm


    def _header_decode(self, hval):
        l = decode_header(hval)
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
        return ' '.join(items)



    def _headers_filter(self, headers):
        self.log.dbg('msg headers filter')
        f = JMailBase.cache_get(self._ck+':headers_filter')
        if f is not None:
            return f
        f = list()
        header_keys = sorted([h[0].lower() for h in headers])
        for hk in SHOW_HEADERS:
            if hk.lower() in header_keys:
                hv = None
                for h in headers:
                    if h[0].lower() == hk:
                        hv = self._header_decode(h[1])
                f.append((hk.capitalize(), hv))
        JMailBase.cache_set(self._ck+':headers_filter', f)
        return f


    def _headers_short(self, headers):
        self.log.dbg('headers short')

        hs = JMailBase.cache_get(self._ck+':headers_short')
        if hs is not None:
            return hs
        hs = dict()

        for hk, hv in headers:
            # -- date
            if hk.lower() == 'date':
                dstring = ' '.join(hv.split()[:6])
                dobj = strptime(dstring, self._conf.get('DATE_HEADER_FORMAT'))
                hv = strftime('%Y%m%d.%H:%M', dobj)
                hs['date'] = hv
            # -- from / to
            elif hk.lower() == 'from' or hk.lower() == 'to':
                if len(hv) > 23:
                    hv = hv[:23] + '..'
                hs[hk.lower()] = hv
            # -- subject
            elif hk.lower() == 'subject':
                if len(hv) > 33:
                    hv = hv[:33] + '..'
                hs['subject'] = hv

        JMailBase.cache_set(self._ck+':headers_short', hs)
        return hs


    def _msg_properties(self, msg):
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
            prop['content_type'] = ct
            try:
                cs = d.split(';')[1].strip()
            except IndexError:
                cs = None
            if cs is not None:
                #~ self.log.dbg('split charset: ', cs)
                try:
                    k, v = cs.split('=')
                except ValueError:
                    k = '__VALUE_ERROR__'
                    v = None
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
        # -- debug info
        self.log.dbg('msg properties: ', type(msg),
            ' {}, {}'.format(
                prop['content_type'],
                prop['disposition'],
            )
        )
        return prop


    def _text_encoding(self, text, props):
        self.log.dbg('msg text: ', type(text))
        tenc = props['transfer_encoding']
        charset = props['charset']
        if charset is None:
            charset = JMailBase.charset
        self.log.dbg('transfer encoding: ', tenc)
        # -- quoted-printable
        if tenc == 'quoted-printable':
            text = decodestring(text.encode()).decode(charset)
        # -- base64
        elif tenc == 'base64':
            text = b64decode(text.encode()).decode(charset)
        return text


    def _text_html(self, msg, props):
        self.log.dbg('text html')
        text = JMailBase.cache_get(self._ck+':text_html')
        if text is not None:
            return text
        text = msg.get_payload()
        r = self._text_encoding(text, props)
        JMailBase.cache_set(self._ck+':text_html', r)
        return r


    def _text_plain(self, msg, props):
        self.log.dbg('text plain')
        text = JMailBase.cache_get(self._ck+':text_plain')
        if text is not None:
            return text
        text = self._text_encoding(msg.get_payload(), props)
        r = text.splitlines()
        JMailBase.cache_set(self._ck+':text_plain', r)
        return r


    def _body_text(self, msg, props):
        self.log.dbg('msg body text')
        #~ self.log.dbg('msg boundary: ', msg.get_boundary())
        #~ self.log.dbg('msg attach: ', msg.attach)
        #~ self.log.dbg('msg defects: ', msg.defects)
        #~ self.log.dbg('msg epilogue: ', msg.epilogue)
        #~ self.log.dbg('msg preamble: ', msg.preamble)
        #~ self.log.dbg('msg keys: ', msg.keys())
        #~ self.log.dbg('msg values: ', msg.values())
        #~ self.log.dbg('props: ', props)
        text = None
        msg_subtype = props['content_subtype']
        if msg_subtype == 'plain':
            self.log.dbg('subtype plain')
            if self._html:
                self.body_parts.append('text/plain')
            else:
                text = self._text_plain(msg, props)
        elif msg_subtype == 'html':
            self.log.dbg('subtype html')
            if self._html:
                text = self._text_html(msg, props)
            else:
                self.body_parts.append('text/html')
        return text


    def _body_get(self, body):
        self.log.dbg('msg body get')
        #~ if self._honly:
            #~ return ['[HEADERS ONLY]']
        self.body_parts = list()
        props = self._msg_properties(body)
        if body.is_multipart():
            return self._body_parts(body)
        else:
            self.log.dbg('body content type: ', props['content_type'])
            text = None
            if body.get_content_maintype() == 'text':
                text = self._body_text(body, props)
            if text is None:
                return ['[NO TEXT CONTENT]']
            else:
                return text


    def _msg_attachs(self, part, props):
        self.log.dbg('msg attachs')
        ad = dict()
        ad.update(props)
        ad['filename_enc'] = urlsafe_b64encode(props['filename'].encode())
        if props['content_maintype'] == 'text':
            ad['payload'] = self._text_encoding(part.get_payload(), props)
        else:
            ad['payload'] = part.get_payload()
        self.attachs.append(ad)


    def _body_parts(self, body):
        self.log.dbg('msg body parts')
        self.attachs = list()
        text = None
        for part in body.walk():
            part_props = self._msg_properties(part)
            #~ self.log.dbg('part props: ', part_props)
            disp = part_props.get('disposition', None)
            if disp is None:
                disp = '__NOT_SET__'
            if disp.startswith('attachment'):
                self._msg_attachs(part, part_props)
            elif part_props['content_maintype'] == 'text':
                self.log.dbg('part maintype text')
                r = self._body_text(part, part_props)
                if r is not None:
                    text = r
                    self.prop = part_props
        if text is None:
            text = ['[NO CONTENT]']
        return text


    def __str__(self):
        self.log.dbg('msg str')
        try:
            return 'JMailMessage({}: {})'.format(self.headers[0][0], self.headers[0][1])
        except:
            return 'JMailMessage'
