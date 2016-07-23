import sys

class JMailLog:
    _tag = 'JMail'
    _outfile = None

    def __init__(self, outfile=sys.stderr):
        self._outfile = outfile

    def _log(self, tag, *line_items):
        print(self._tag, '[{}] - '.format(tag), sep='', end='', file=self._outfile)
        for li in line_items:
            print(str(li), sep='', end='', file=self._outfile)
        print(file=self._outfile)

    def dbg(self, *line_items):
        self._log('DGB', *line_items)

    def err(self, *line_items):
        self._log('ERR', *line_items)

    def warn(self, *line_items):
        self._log('WRN', *line_items)
