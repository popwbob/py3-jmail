import re
import os.path
import imaplib

from base64 import urlsafe_b64encode, urlsafe_b64decode

from django.conf import settings as django_settings
from django.core.cache.backends.filebased import FileBasedCache
from django.core.cache.backends.dummy import DummyCache

from .. import JMailBase
from ..error import JMailError
from ..msg import JMailMessage


class JMailMDirCache(JMailBase):
    __cache = None
    _meta_ttl = None
    _data_ttl = None

    @classmethod
    def init(self, name_encode):
        cache_conf = django_settings.CACHES['mdir-cache']
        cache_location = os.path.join(cache_conf.get('LOCATION'), str(self.macct.get('id')), name_encode.decode())
        #~ self.log.dbg('cache_conf: ', cache_conf)
        self.log.dbg('cache_location: ', cache_location)
        if self.conf.get('MDIR_CACHE_ENABLE', False):
            self.__cache = FileBasedCache(cache_location, cache_conf)
        else:
            self.__cache = DummyCache('localhost', cache_conf)
        self.log.dbg('mdir cache: ', self.__cache)
        self._meta_ttl = self.conf.get('MDIR_CACHE_META_TTL')
        self._data_ttl = self.conf.get('MDIR_CACHE_DATA_TTL')

    @classmethod
    def __msg_cache_key(self, dtype, msg_uid):
        return 'msg:{}:{}'.format(dtype, int(msg_uid))

    @classmethod
    def mdir_attribs_set(self, mdir_name, attribs):
        if type(mdir_name) is bytes:
            mdir_name = mdir_name.decode()
        self.__cache.set('mdir:attribs:'+mdir_name, attribs, self._meta_ttl)
        self.log.dbg('CACHE save: ', 'mdir:attribs:'+mdir_name)

    @classmethod
    def mdir_attribs_get(self, mdir_name):
        if type(mdir_name) is bytes:
            mdir_name = mdir_name.decode()
        return self.__cache.get('mdir:attribs:'+mdir_name, None)

    @classmethod
    def subs_list_get(self):
        return self.__cache.get('subs:list', None)

    @classmethod
    def subs_list_set(self, sl):
        self.__cache.set('subs:list', sl, self._meta_ttl)

    @classmethod
    def msg_data_get(self, msg_uid):
        ck = self.__msg_cache_key('data', msg_uid)
        return self.__cache.get(ck, None)

    @classmethod
    def msg_data_set(self, msg_uid, data):
        ck = self.__msg_cache_key('data', msg_uid)
        self.__cache.set(ck, data, self._data_ttl)
        self.log.dbg('CACHE save: msg data - %s' % msg_uid)

    @classmethod
    def msg_meta_get(self, msg_uid):
        ck = self.__msg_cache_key('meta', msg_uid)
        return self.__cache.get(ck, None)

    @classmethod
    def msg_meta_set(self, msg_uid, meta):
        ck = self.__msg_cache_key('meta', msg_uid)
        self.__cache.set(ck, meta, self._meta_ttl)
        self.log.dbg('CACHE save: msg meta - %s' % msg_uid)


class JMailMDir(JMailBase):
    __cache = None
    name = None
    name_encode = None
    msgs_no = None
    msgs_new = None
    attr = None

    def __init__(self, name=None, name_encode=None):
        self.name = name
        self.name_encode = name_encode
        self._name_parse()
        self._cache_init()
        self._mdir_select()


    def __del__(self):
        if self.imap and self.imap.state == 'SELECTED':
            self.imap.close()
        del self.__cache


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
        self.attr = self._mdir_attribs(self.name, self.name_encode)


    def _mdir_attribs(self, mdir_name, name_encode):
        attribs = self.__cache.mdir_attribs_get(name_encode)
        if attribs is not None:
            self.log.dbg('CACHE hit: mdir attribs ', mdir_name)
            return attribs
        attribs = dict(messages=-1, recent=-1, unseen=-1)
        try:
            typ, data = self.imap.status(mdir_name, '(MESSAGES RECENT UNSEEN)')
            self.log.dbg('mdir attribs: ', typ, ' ', data)
            if typ == 'OK':
                m = re.search(b'^[^ ]* \(MESSAGES (\d+) RECENT (\d+) UNSEEN (\d+)\)$', data[0])
                attribs = {
                    'messages': int(m.group(1)),
                    'recent': int(m.group(2)),
                    'unseen': int(m.group(3)),
                }
                self.__cache.mdir_attribs_set(name_encode, attribs)
        except Exception as e:
            self.log.err('mdir attribs: ', e)
        return attribs


    def msg_getlist(self, uid_list='__ALL__', peek=True):
        self.log.dbg('Mdir msg getlist')
        if type(uid_list) is str:
            if uid_list == '__ALL__':
                #~ typ, msgs_ids = self.imap.uid('SEARCH', 'ALL')
                #~ uid_list = msgs_ids[0].split()
                #~ self.log.dbg('msgs_ids: ', uid_list)
                typ, msgs_ids = self.imap.uid('SORT', '(REVERSE DATE)', 'utf-8', '(ALL)')
                sorted_uid_list = msgs_ids[0].split()
                self.log.dbg('msgs_ids sorted: ', sorted_uid_list)
        msgs = list()
        for muid in sorted_uid_list:
            if muid != b'':
                msgs.append(self.msg_get(muid, peek))
        return msgs


    def msg_get(self, mail_uid, peek=True):
        if type(mail_uid) is str:
            mail_uid = mail_uid.encode()
        self.log.dbg('Mdir message get: %s' % mail_uid.decode())
        src = self.__cache.msg_data_get(mail_uid)
        if src is None:
            met, src = self._imap_fetch_source(mail_uid, peek)
        else:
            self.log.dbg('CACHE hit: msg data - %s' % mail_uid)
            met = self.__cache.msg_meta_get(mail_uid)
            if met is None:
                met = self._imap_fetch_flags(mail_uid)
            else:
                self.log.dbg('CACHE hit: msg meta - %s' % mail_uid)
        return JMailMessage(meta=met, source=src, uid=mail_uid)


    def _imap_fetch(self, mail_uid, cmd):
        if self.imap.state != 'SELECTED':
            raise JMailError(500, 'mdir not selected, imap state: '+self.imap.state)
        _, data = self.imap.uid('FETCH', mail_uid, cmd)
        return data[0]


    def _imap_fetch_source(self, mail_uid, peek):
        self.log.dbg('Mdir imap fetch source: %d' % int(mail_uid))
        cmd = 'BODY[]'
        if peek:
            cmd = 'BODY.PEEK[]'
        meta, source = self._imap_fetch(mail_uid, '(FLAGS %s)' % cmd)
        self.__cache.msg_meta_set(mail_uid, meta)
        self.__cache.msg_data_set(mail_uid, source)
        return meta, source


    def _imap_fetch_flags(self, mail_uid):
        self.log.dbg('Mdir imap fetch flags: %d' % int(mail_uid))
        meta = self._imap_fetch(mail_uid, 'FLAGS')
        self.__cache.msg_meta_set(mail_uid, meta)
        return meta

    def subs_list(self):
        mbox = self.__cache.subs_list_get()
        if mbox is not None:
            self.log.dbg('CACHE hit: subs list')
        else:
            mbox = self.imap.lsub()
            self.__cache.subs_list_set(mbox)
        self.log.dbg('subs list mbox: ', mbox)
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
            name_encode = urlsafe_b64encode(c).decode()
            show_name = c
            if show_name.startswith(b'"'):
                show_name = show_name[1:]
            if show_name.endswith(b'"'):
                show_name = show_name[:-1]
            r.append({
                'name': show_name,
                'imap_name': c.decode(),
                'name_encode': name_encode,
                'attr': self._mdir_attribs(c, name_encode)
            })
        return r


    def _cache_init(self):
        self.__cache = JMailMDirCache
        self.__cache.init(self.name_encode)
