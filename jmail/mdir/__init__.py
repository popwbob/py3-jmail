import re
import imaplib
from base64 import urlsafe_b64encode, urlsafe_b64decode

from .. import JMailBase
from ..error import JMailError
from ..mail import JMailMessage


class JMailMDir(JMailBase):
    name = None
    name_encode = None
    msgs_no = None
    msgs_new = None
    attr = None

    def __init__(self, name=None, name_encode=None):
        self.name = name
        self.name_encode = name_encode
        self._name_parse()
        self._mdir_select()


    def __del__(self):
        if self.imap and self.imap.state == 'SELECTED':
            self.imap.close()


    def _name_parse(self):
        if self.name is None and self.name_encode is None:
            raise JMailError(500, 'no mdir name')
        # -- decode name
        if type(self.name_encode) is str:
            self.name_encode = self.name_encode.encode()
        if self.name is None:
            self.name = urlsafe_b64decode(self.name_encode)
        # -- endecode name
        if type(self.name) is str:
            self.name = self.name.encode()
        if self.name_encode is None:
            self.name_encode = urlsafe_b64encode(self.name)


    def _mdir_select(self):
        typ, sdata = self.imap.select(self.name)
        self.log.dbg('mdir select: ', typ, ' ', sdata)
        if typ != 'OK':
            raise JMailError(500, 'mdir select failed: '+typ)
        self._mdir_attribs()


    def _mdir_attribs(self):
        commands = ['MESSAGES', 'RECENT', 'UNSEEN']
        self.attr = dict()
        for cmd in commands:
            typ, data = self.imap.status(self.name, '({})'.format(cmd))
            m = re.search('{} (\d+)\)$'.format(cmd).encode(), data[0])
            self.attr[cmd.lower()] = int(m.group(1))
        self.log.dbg('mdir attribs: ', self.attr)


    def msg_getlist(self, uid_list='__ALL__', peek=True):
        if type(uid_list) is str:
            if uid_list == '__ALL__':
                typ, msgs_ids = self.imap.uid('SEARCH', 'ALL')
                uid_list = msgs_ids[0].split()
        self.log.dbg('msgs_ids: ', uid_list)
        msgs = list()
        for muid in uid_list:
            if muid != b'':
                msgs.append(self.msg_get(muid, peek))
        return msgs


    def msg_get(self, mail_uid, peek=True):
        if type(mail_uid) is str:
            mail_uid = mail_uid.encode()
        mdata = self._imap_fetch(mail_uid, peek)
        m = JMailMessage(mdata, uid=mail_uid)
        del mdata
        return m


    def msg_source(self, mail_uid, peek=True):
        if type(mail_uid) is str:
            mail_uid = mail_uid.encode()
        mdata = self._imap_fetch(mail_uid, peek)
        return mdata[1]


    def _imap_fetch(self, mail_uid, peek):
        self.log.dbg('mdir state: ', self.imap.state)
        if self.imap.state != 'SELECTED':
            raise JMailError(500, 'mdir not selected, imap state: '+self.imap.state)
        if peek:
            cmd = '(FLAGS BODY.PEEK[])'
        else:
            cmd = '(FLAGS BODY[])'
        typ, mdata = self.imap.uid('FETCH', mail_uid, cmd)
        return mdata[0]


    def subs_list(self):
        mbox = self.imap.lsub()
        self.log.dbg(mbox)
        sl = []
        for d in mbox[1]:
            if d != b'':
                if type(d) == type(tuple()):
                    child = d[1]
                else:
                    child = b' '.join(d.split(b' ')[2:])
                sl.append(child)
        sl.insert(0, b'INBOX')
        self.log.dbg('subs: ', sl)
        #~ sl = sorted(sl)
        r = list()
        for c in sl:
            show_name = c
            if show_name.startswith(b'"'):
                show_name = show_name[1:]
            if show_name.endswith(b'"'):
                show_name = show_name[:-1]
            r.append({
                'name': show_name,
                'imap_name': c.decode(),
                'name_encode': urlsafe_b64encode(c).decode(),
            })
        return r