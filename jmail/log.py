import sys

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
