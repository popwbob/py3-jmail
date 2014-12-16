import imaplib

IMAP_DEBUG = 4


def imap_connect(macct):
    use_ssl = macct.get('imap_server_ssl')
    if use_ssl:
        m = imaplib.IMAP4_SSL(macct.get('imap_server'), macct.get('imap_server_port'))
    else:
        m = imaplib.IMAP(macct.get('imap_server'), macct.get('imap_server_port'))
    m.debug = IMAP_DEBUG
    m.login(macct.get('address'), macct.get('password', 'LiJXLK4akFfCgtLs'))
    return m


def imap_end(m):
    m.logout()
