import sys
import json

from django.shortcuts import render


class JMailLog:
    _tag = 'JMail'
    _outfile = sys.stderr

    def _log(self, tag, *line_items, sep=' '):
        print(self._tag, '[{}]: '.format(tag), sep='', end='', file=self._outfile)
        for li in line_items:
            print(str(li), sep=sep, end='', file=self._outfile)
        print(file=self._outfile)

    def dbg(self, *line_items, sep=' '):
        self._log('DGB', *line_items)


class JMailBase:
    log = None
    _req = None
    _tmpl_path = None
    _tmpl_data = None

    def __str__(self):
        r = '{\n'
        r += '    tmpl_path: {}\n'.format(self._tmpl_path)
        r += '}\n'
        return r


class JMail(JMailBase):
    def __init__(self, req):
        JMailBase.log = JMailLog()
        self.log.dbg('start')
        JMailBase._req = req
        JMailBase._tmpl_path = self._tmpl_path_get()
        JMailBase._tmpl_data = self._tmpl_data_init()

    def end(self):
        self.log.dbg('end')

    def _tmpl_path_get(self):
        p = self._req.path
        if p.startswith('/'):
            p = p[1:]
        if p.endswith('/'):
            p = p[:-1]
        if p == '':
            p = 'home'
        return '{}.html'.format(p)

    def _tmpl_data_init(self):
        doc = dict(title='JMail - {}'.format(self._req.path))
        td = dict(
            doc=doc,
        )
        return td

    def render(self):
        self.end()
        return render(self._req, self._tmpl_path, self._tmpl_data)

    def tmpl_data(self, data):
        self._tmpl_data.update(data)

    def debug_data(self):
        dd = list()
        dd.append('JMail: {}'.format(str(self)))
        dd.append('')
        dd.append('tmpl_data: {}'.format(json.dumps(self._tmpl_data, indent=4)))
        dd.append('')
        return dd
