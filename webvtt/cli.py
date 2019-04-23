u"""
Usage:
  webvtt segment <file> [--target-duration=SECONDS] [--mpegts=OFFSET] [--output=<dir>]
  webvtt -h | --help
  webvtt --version

Options:
  -h --help                  Show this screen.
  --version                  Show version.
  --target-duration=SECONDS  Target duration of each segment in seconds [default: 10].
  --mpegts=OFFSET            Presentation timestamp value [default: 900000].
  --output=<dir>             Output to directory [default: ./].

Examples:
  webvtt segment captions.vtt --output destination/directory
"""

from __future__ import absolute_import
from docopt import docopt

from . import WebVTTSegmenter, __version__


def main():
    u"""Main entry point for CLI commands."""
    options = docopt(__doc__, version=__version__)
    if options[u'segment']:
        segment(
            options[u'<file>'],
            options[u'--output'],
            options[u'--target-duration'],
            options[u'--mpegts'],
        )


def segment(f, output, target_duration, mpegts):
    u"""Segment command."""
    try:
        target_duration = int(target_duration)
    except ValueError:
        exit(u'Error: Invalid target duration.')

    try:
        mpegts = int(mpegts)
    except ValueError:
        exit(u'Error: Invalid MPEGTS value.')

    WebVTTSegmenter().segment(f, output, target_duration, mpegts)