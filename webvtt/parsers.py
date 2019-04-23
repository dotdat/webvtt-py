from __future__ import with_statement
from __future__ import absolute_import
import re
import os
import codecs

from .errors import MalformedFileError, MalformedCaptionError
from .structures import Block, Style, Caption
from io import open
from itertools import ifilter
from itertools import imap


class TextBasedParser(object):
    u"""
    Parser for plain text caption files.
    This is a generic class, do not use directly.
    """

    TIMEFRAME_LINE_PATTERN = u''
    PARSER_OPTIONS = {}

    def __init__(self, parse_options=None):
        self.captions = []
        self.parse_options = parse_options or {}

    def read(self, file):
        u"""Reads the captions file."""
        content = self._read_content(file)
        self._validate(content)
        self._parse(content)

        return self

    def _read_content(self, file):

        first_bytes = min(32, os.path.getsize(file))
        with open(file, u'rb') as f:
            raw = f.read(first_bytes)

        if raw.startswith(codecs.BOM_UTF8):
            encoding = u'utf-8-sig'
        else:
            encoding = u'utf-8'

        with open(file, encoding=encoding) as f:
            lines = [line.rstrip(u'\n') for line in f.readlines()]

        if not lines:
            raise MalformedFileError(u'The file is empty.')

        return lines

    def _parse_timeframe_line(self, line):
        u"""Parse timeframe line and return start and end timestamps."""
        tf = self._validate_timeframe_line(line)
        if not tf:
            raise MalformedCaptionError(u'Invalid time format')

        return tf.group(1), tf.group(2)

    def _validate_timeframe_line(self, line):
        return re.match(self.TIMEFRAME_LINE_PATTERN, line)

    def _is_timeframe_line(self, line):
        u"""
        This method returns True if the line contains the timeframes.
        To be implemented by child classes.
        """
        raise NotImplementedError

    def _validate(self, lines):
        u"""
        Validates the format of the parsed file.
        To be implemented by child classes.
        """
        raise NotImplementedError

    def _should_skip_line(self, line, index, caption):
        u"""
        This method returns True for a line that should be skipped.
        Implement in child classes if needed.
        """
        return False

    def _parse(self, lines):
        self.captions = []
        c = None

        for index, line in enumerate(lines):
            if self._is_timeframe_line(line):
                try:
                    start, end = self._parse_timeframe_line(line)
                except MalformedCaptionError, e:
                    raise MalformedCaptionError(u'{} in line {}'.format(e, index + 1))
                c = Caption(start, end)
            elif self._should_skip_line(line, index, c):  # allow child classes to skip lines based on the content
                continue
            elif line:
                if c is None:
                    raise MalformedCaptionError(
                        u'Caption missing timeframe in line {}.'.format(index + 1))
                else:
                    c.add_line(line)
            else:
                if c is None:
                    continue
                if not c.lines:
                    if self.PARSER_OPTIONS.get(u'ignore_empty_captions', False):
                        c = None
                        continue
                    raise MalformedCaptionError(u'Caption missing text in line {}.'.format(index + 1))

                self.captions.append(c)
                c = None

        if c is not None and c.lines:
            self.captions.append(c)


class SRTParser(TextBasedParser):
    u"""
    SRT parser.
    """

    TIMEFRAME_LINE_PATTERN = re.compile(u'\s*(\d+:\d{2}:\d{2},\d{3})\s*-->\s*(\d+:\d{2}:\d{2},\d{3})')

    PARSER_OPTIONS = {
        u'ignore_empty_captions': True
    }

    def _validate(self, lines):
        if len(lines) < 2 or lines[0] != u'1' or not self._validate_timeframe_line(lines[1]):
            raise MalformedFileError(u'The file does not have a valid format.')

    def _is_timeframe_line(self, line):
        return u'-->' in line

    def _should_skip_line(self, line, index, caption):
        return caption is None and line.isdigit()


class WebVTTParser(TextBasedParser):
    u"""
    WebVTT parser.
    """

    TIMEFRAME_LINE_PATTERN = re.compile(u'\s*((?:\d+:)?\d{2}:\d{2}.\d{3})\s*-->\s*((?:\d+:)?\d{2}:\d{2}.\d{3})')
    COMMENT_PATTERN = re.compile(u'NOTE(?:\s.+|$)')
    STYLE_PATTERN = re.compile(u'STYLE[ \t]*$')

    def __init__(self):
        super(WebVTTParser, self).__init__()
        self.styles = []

    def _compute_blocks(self, lines):
        blocks = []

        for index, line in enumerate(lines, start=1):
            if line:
                if not blocks:
                    blocks.append(Block(index))
                if not blocks[-1].lines:
                    blocks[-1].line_number = index
                blocks[-1].lines.append(line)
            else:
                blocks.append(Block(index))

        # filter out empty blocks and skip signature
        self.blocks = list(ifilter(lambda x: x.lines, blocks))[1:]

    def _parse_cue_block(self, block):
        caption = Caption()
        cue_timings = None

        for line_number, line in enumerate(block.lines):
            if self._is_cue_timings_line(line):
                if cue_timings is None:
                    try:
                        cue_timings = self._parse_timeframe_line(line)
                    except MalformedCaptionError, e:
                        raise MalformedCaptionError(
                            u'{} in line {}'.format(e, block.line_number + line_number))
                else:
                    raise MalformedCaptionError(
                        u'--> found in line {}'.format(block.line_number + line_number))
            elif line_number == 0:
                caption.identifier = line
            else:
                caption.add_line(line)

        caption.start = cue_timings[0]
        caption.end = cue_timings[1]
        return caption

    def _parse(self, lines):
        self.captions = []
        self._compute_blocks(lines)

        for block in self.blocks:
            if self._is_cue_block(block):
                caption = self._parse_cue_block(block)
                self.captions.append(caption)
            elif self._is_comment_block(block):
                continue
            elif self._is_style_block(block):
                if self.captions:
                    raise MalformedFileError(
                        u'Style block defined after the first cue in line {}.'
                        .format(block.line_number))
                style = Style()
                style.lines = block.lines[1:]
                self.styles.append(style)
            else:
                if len(block.lines) == 1:
                    raise MalformedCaptionError(
                        u'Standalone cue identifier in line {}.'.format(block.line_number))
                else:
                    raise MalformedCaptionError(
                        u'Missing timing cue in line {}.'.format(block.line_number+1))

    def _validate(self, lines):
        if not re.match(u'WEBVTT', lines[0]):
            raise MalformedFileError(u'The file does not have a valid format')

    def _is_cue_timings_line(self, line):
        return u'-->' in line

    def _is_cue_block(self, block):
        u"""Returns True if it is a cue block
        (one of the two first lines being a cue timing line)"""
        return any(imap(self._is_cue_timings_line, block.lines[:2]))

    def _is_comment_block(self, block):
        u"""Returns True if it is a comment block"""
        return re.match(self.COMMENT_PATTERN, block.lines[0])

    def _is_style_block(self, block):
        u"""Returns True if it is a style block"""
        return re.match(self.STYLE_PATTERN, block.lines[0])


class SBVParser(TextBasedParser):
    u"""
    YouTube SBV parser.
    """

    TIMEFRAME_LINE_PATTERN = re.compile(u'\s*(\d+:\d{2}:\d{2}.\d{3}),(\d+:\d{2}:\d{2}.\d{3})')

    def _validate(self, lines):
        if not self._validate_timeframe_line(lines[0]):
            raise MalformedFileError(u'The file does not have a valid format')

    def _is_timeframe_line(self, line):
        return self._validate_timeframe_line(line)
