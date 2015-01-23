import email
from base64 import b64decode
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
    _html = None
    log = None
    source = None
    headers = None
    headers_full = None
    flags = None
    body = None
    body_parts = None
    size = None
    prop = None
    attachs = None


    def __init__(self, mail_uid=None, headers_only=False, imap=None, read_html=False):
        self.log = JMailBase.log
        self.log.dbg('msg init')
        self.uid = mail_uid
        self._honly = headers_only
        self._imap = JMailBase.imap
        if imap is not None:
            self._imap = imap
        self._html = read_html


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
        text = msg.get_payload()
        return self._text_encoding(text, props)


    def _text_plain(self, msg, props):
        self.log.dbg('text plain')
        text = msg.get_payload()
        return self._text_encoding(text, props)


    def _body_text(self, msg, props):
        self.log.dbg('msg body text')
        self.log.dbg('msg boundary: ', msg.get_boundary())
        #~ self.log.dbg('msg attach: ', msg.attach)
        #~ self.log.dbg('msg defects: ', msg.defects)
        #~ self.log.dbg('msg epilogue: ', msg.epilogue)
        #~ self.log.dbg('msg preamble: ', msg.preamble)
        self.log.dbg('msg keys: ', msg.keys())
        self.log.dbg('msg values: ', msg.values())
        self.log.dbg('props: ', props)
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
        if self._honly:
            return '[HEADERS ONLY]'
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
                return '[NO TEXT CONTENT]'
            else:
                return text


    def _msg_attachs(self, part, props):
        self.log.dbg('msg attachs')
        self.attachs.append({
            'content_type': props['content_type'],
            'filename': props['filename'],
        })


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
            text = '[NO CONTENT]'
        return text


    def __str__(self):
        self.log.dbg('msg str')
        try:
            return 'JMailMessage({}: {})'.format(self.headers[0][0], self.headers[0][1])
        except:
            return 'JMailMessage'
