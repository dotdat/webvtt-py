from __future__ import division
from __future__ import absolute_import
import re

from .errors import MalformedCaptionError
from itertools import imap

TIMESTAMP_PATTERN = re.compile(u'(\d+)?:?(\d{2}):(\d{2})[.,](\d{3})')

__all__ = [u'Caption']


class Caption(object):

    CUE_TEXT_TAGS = re.compile(u'<.*?>')

    u"""
    Represents a caption.
    """
    def __init__(self, start=u'00:00:00.000', end=u'00:00:00.000', text=None):
        self.start = start
        self.end = end
        self.identifier = None

        # If lines is a string convert to a list
        if text and isinstance(text, unicode):
            text = text.splitlines()

        self._lines = text or []

    def __repr__(self):
        return u'<%(cls)s start=%(start)s end=%(end)s text=%(text)s>' % {
            u'cls': self.__class__.__name__,
            u'start': self.start,
            u'end': self.end,
            u'text': self.text.replace(u'\n', u'\\n')
        }

    def __str__(self):
        return u'%(start)s %(end)s %(text)s' % {
            u'start': self.start,
            u'end': self.end,
            u'text': self.text.replace(u'\n', u'\\n')
        }

    def add_line(self, line):
        self.lines.append(line)

    def _to_seconds(self, hours, minutes, seconds, milliseconds):
        return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000

    def _parse_timestamp(self, timestamp):
        res = re.match(TIMESTAMP_PATTERN, timestamp)
        if not res:
            raise MalformedCaptionError(u'Invalid timestamp: {}'.format(timestamp))

        values = list(imap(lambda x: int(x) if x else 0, res.groups()))
        return self._to_seconds(*values)

    def _to_timestamp(self, total_seconds):
        hours = int(total_seconds / 3600)
        minutes = int(total_seconds / 60 - hours * 60)
        seconds = total_seconds - hours * 3600 - minutes * 60
        return u'{:02d}:{:02d}:{:06.3f}'.format(hours, minutes, seconds)

    def _clean_cue_tags(self, text):
        return re.sub(self.CUE_TEXT_TAGS, u'', text)

    @property
    def start_in_seconds(self):
        return self._start

    @property
    def end_in_seconds(self):
        return self._end

    @property
    def start(self):
        return self._to_timestamp(self._start)

    @start.setter
    def start(self, value):
        self._start = self._parse_timestamp(value)

    @property
    def end(self):
        return self._to_timestamp(self._end)

    @end.setter
    def end(self, value):
        self._end = self._parse_timestamp(value)

    @property
    def lines(self):
        return self._lines

    @property
    def text(self):
        u"""Returns the captions lines as a text (without cue tags)"""
        return self._clean_cue_tags(self.raw_text)

    @property
    def raw_text(self):
        u"""Returns the captions lines as a text (may include cue tags)"""
        return u'\n'.join(self.lines)

    @text.setter
    def text(self, value):
        if not isinstance(value, unicode):
            raise AttributeError(u'String value expected but received {}.'.format(type(value)))

        self._lines = value.splitlines()


class GenericBlock(object):
    u"""Generic class that defines a data structure holding an array of lines"""
    def __init__(self):
        self.lines = []


class Block(GenericBlock):
    def __init__(self, line_number):
        super(Block, self).__init__()
        self.line_number = line_number


class Style(GenericBlock):

    @property
    def text(self):
        u"""Returns the style lines as a text"""
        return u''.join(imap(lambda x: x.strip(), self.lines))

    @text.setter
    def text(self, value):
        if type(value) != unicode:
            raise TypeError(u'The text value must be a string.')
        self.lines = value.split(u'\n')
