
__all__ = [u'MalformedFileError', u'MalformedCaptionError', u'InvalidCaptionsError', u'MissingFilenameError']


class MalformedFileError(Exception):
    u"""Error raised when the file is not well formatted"""


class MalformedCaptionError(Exception):
    u"""Error raised when a caption is not well formatted"""


class InvalidCaptionsError(Exception):
    u"""Error raised when passing wrong captions to the segmenter"""


class MissingFilenameError(Exception):
    u"""Error raised when saving a file without filename."""
