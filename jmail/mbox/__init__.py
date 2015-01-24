from base64 import urlsafe_b64decode, urlsafe_b64encode

from .. import JMailBase
from ..mail import JMailMessage


class JMailMBox(JMailBase):
    name_enc = None
    name = None


    def __init__(self, mbox_name, name_encoded=False):
        if type(mbox_name) is str:
            mbox_name = mbox_name.encode()
        if name_encoded:
            self.name_enc = mbox_name
            self.name = urlsafe_b64decode(mbox_name)
        else:
            self.name = mbox_name
            self.name_enc = urlsafe_b64encode(mbox_name)
        self.imap.select(self.name)


    def __del__(self):
        if self.imap is not None:
            self.imap.close()


    def messages(self, headers_only=False):
        typ, msgs_ids = self.imap.uid('SEARCH', 'ALL')
        self.log.dbg('msgs_ids: ', msgs_ids)
        msgs = list()
        for muid in msgs_ids[0].split():
            if muid != b'':
                msg = JMailMessage(muid, self.name, headers_only=True)
                msg.fetch()
                msgs.append(msg)
        return msgs


    def tmpl_data(self):
        return {
            'name': self.name,
            'name_encode': self.name_enc,
        }
