import os
import re
from enum import IntEnum

from .parsers import WebVTTParser, SRTParser, SBVParser
from .writers import WebVTTWriter, SRTWriter, SBVWriter
from webvtt.exceptions import MissingFilenameError


class Captions(object):

    FORMAT_EXTENSION_PATTERN = re.compile('.+\(\.(.+)\)')
    OUR_PARSER = None

    def __init__(self, parse_options=None):
        self._captions = []
        self._styles = []
        self.file = ''
        self.extension = ''
        self.parse_options = parse_options or {}

    def __len__(self):
        return len(self._captions)

    def __getitem__(self, index):
        return self._captions[index]

    def save(self, output=''):
        """Save the document.
        If no output is provided the file will be saved in the same location. Otherwise output
        can determine a target directory or file.
        """
        if not output:
            if not self.file:
                raise MissingFilenameError
            # saving an original vtt file will overwrite the file
            # and for files read from other formats will save as vtt
            # with the same name and location
            self.file = os.path.splitext(self.file)[0] + '.' + self.extension
        else:
            target = os.path.join(os.getcwd(), output)
            if os.path.isdir(target):
                # if an output is provided and it is a directory
                # the file will be saved in that location with the same name
                filename = os.path.splitext(os.path.basename(self.file))[0]
                self.file = os.path.join(target, '{}.{}'.format(filename, self.extension))
            else:
                if target[-3:].lower() != self.extension:
                    target += '.' + self.extension
                # otherwise the file will be written in the specified location
                self.file = target

        self.save_format()

    def save_format(self):
        raise NotImplementedError


class OutputFormat(IntEnum):
    WebVTT = 1
    SRT = 2
    SBV = 3


class WebVTT(object):
    """
    Parse captions in WebVTT format and also from other formats like SRT.

    To read WebVTT:

        WebVTT().read('captions.vtt')

    For other formats like SRT, use from_[format in lower case]:

        WebVTT().from_srt('captions.srt')

    A list of all supported formats is available calling supported_formats().
    """

    def __init__(self):
        self.file = None
        self._captions = []
        self._styles = None

    def __len__(self):
        return len(self._captions)

    def __getitem__(self, index):
        return self._captions[index]

    def from_srt(self, file):
        """Reads captions from a file in SubRip format."""
        self.file = file
        self._captions = SRTParser().read(file).captions
        return self

    def from_sbv(self, file):
        """Reads captions from a file in YouTube SBV format."""
        self.file = file
        self._captions = SBVParser().read(file).captions
        return self

    def read(self, file):
        """Reads a WebVTT captions file."""
        parser = WebVTTParser().read(file)
        self.file = file
        self._captions = parser.captions
        self._styles = parser.styles
        return self

    def _get_output_file(self, output, extension='vtt'):
        if not output:
            if not self.file:
                raise MissingFilenameError
            # saving an original vtt file will overwrite the file
            # and for files read from other formats will save as vtt
            # with the same name and location
            return os.path.splitext(self.file)[0] + '.' + extension
        else:
            target = os.path.join(os.getcwd(), output)
            if os.path.isdir(target):
                # if an output is provided and it is a directory
                # the file will be saved in that location with the same name
                filename = os.path.splitext(os.path.basename(self.file))[0]
                return os.path.join(target, '{}.{}'.format(filename, extension))
            else:
                if target[-3:].lower() != extension:
                    target += '.' + extension
                # otherwise the file will be written in the specified location
                return target

    def save(self, output=''):
        """Save the document.
        If no output is provided the file will be saved in the same location. Otherwise output
        can determine a target directory or file.
        """
        self.file = self._get_output_file(output)
        with open(self.file, 'w', encoding='utf-8') as f:
            self.write(f)

    def save_as_srt(self, output=''):
        self.file = self._get_output_file(output, extension='srt')
        with open(self.file, 'w', encoding='utf-8') as f:
            self.write(f, output_format=OutputFormat.SRT)

    def write(self, f, output_format=OutputFormat.WebVTT):
        if output_format == OutputFormat.WebVTT:
            WebVTTWriter().write(self._captions, f)
        elif output_format == OutputFormat.SRT:
            SRTWriter().write(self._captions, f)
#        elif output_format == OutputFormat.SBV:
#            SBVWriter().write(self._captions, f)

    # def write(self, f):
    #     f.write('WEBVTT\n')
    #     for c in self._captions:
    #         f.write('\n{} --> {}\n'.format(c.start, c.end))
    #         f.writelines(['{}\n'.format(l) for l in c.lines])
    #
    # def save_format(self):
    #     with open(self.file, 'w', encoding='utf-8') as f:
    #         self.write(f)

    @staticmethod
    def supported_formats():
        """Provides a list of supported formats that this class can read from."""
        return ['WebVTT (.vtt)', 'SubRip (.srt)', 'YouTube SBV (.sbv)']

    @property
    def captions(self):
        """Returns the list of captions."""
        return self._captions

    @property
    def total_length(self):
        """Returns the total length of the captions."""
        if not self._captions:
            return 0
        return int(self._captions[-1].end_in_seconds) - int(self._captions[0].start_in_seconds)

    @property
    def styles(self):
        return self._styles
