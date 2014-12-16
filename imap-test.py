import getpass, imaplib

#~ m = imaplib.IMAP4('localhost')
m = imaplib.IMAP4_SSL('jrms.com.ar', 993)
m.debug = 0

#~ m.login('jmaildev@jrms.com.ar', getpass.getpass())
m.login('jmaildev@jrms.com.ar', 'LiJXLK4akFfCgtLs')

m.select()
typ, data = m.search(None, 'ALL')
for num in data[0].split():
    typ, data = m.fetch(num, '(RFC822)')
    #~ print('Message: {}\n{}\n'.format(num, data[0][1]))
    print('Message: {}'.format(num))

m.close()
m.logout()
