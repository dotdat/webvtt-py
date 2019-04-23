from __future__ import with_statement
from __future__ import division
from __future__ import absolute_import
import os
from math import ceil, floor

from .errors import InvalidCaptionsError
from .webvtt import WebVTT
from .structures import Caption
from io import open

MPEGTS = 900000
SECONDS = 10  # default number of seconds per segment

__all__ = [u'WebVTTSegmenter']


class WebVTTSegmenter(object):
    u"""
    Provides segmentation of WebVTT captions for HTTP Live Streaming (HLS).
    """
    def __init__(self):
        self._total_segments = 0
        self._output_folder = u''
        self._seconds = 0
        self._mpegts = 0
        self._segments = []

    def _validate_webvtt(self, webvtt):
        # Validates that the captions is a list and all the captions are instances of Caption.
        if not isinstance(webvtt, WebVTT):
            return False
        for c in webvtt.captions:
            if not isinstance(c, Caption):
                return False
        return True

    def _slice_segments(self, captions):
        self._segments = [[] for _ in xrange(self.total_segments)]

        for c in captions:
            segment_index_start = int(floor(c.start_in_seconds / self.seconds))
            self.segments[segment_index_start].append(c)

            # Also include a caption in other segments based on the end time.
            segment_index_end = int(floor(c.end_in_seconds / self.seconds))
            if segment_index_end > segment_index_start:
                for i in xrange(segment_index_start + 1, segment_index_end + 1):
                    self.segments[i].append(c)

    def _write_segments(self):
        for index in xrange(self.total_segments):
            segment_file = os.path.join(self._output_folder, u'fileSequence{}.webvtt'.format(index))

            with open(segment_file, u'w', encoding=u'utf-8') as f:
                f.write(u'WEBVTT\n')
                f.write(u'X-TIMESTAMP-MAP=MPEGTS:{},LOCAL:00:00:00.000\n'.format(self._mpegts))

                for caption in self.segments[index]:
                    f.write(u'\n{} --> {}\n'.format(caption.start, caption.end))
                    f.writelines([u'{}\n'.format(l) for l in caption.lines])

    def _write_manifest(self):
        manifest_file = os.path.join(self._output_folder, u'prog_index.m3u8')
        with open(manifest_file, u'w', encoding=u'utf-8') as f:
            f.write(u'#EXTM3U\n')
            f.write(u'#EXT-X-TARGETDURATION:{}\n'.format(self.seconds))
            f.write(u'#EXT-X-VERSION:3\n')
            f.write(u'#EXT-X-PLAYLIST-TYPE:VOD\n')

            for i in xrange(self.total_segments):
                f.write(u'#EXTINF:30.00000\n')
                f.write(u'fileSequence{}.webvtt\n'.format(i))

            f.write(u'#EXT-X-ENDLIST\n')

    def segment(self, webvtt, output=u'', seconds=SECONDS, mpegts=MPEGTS):
        u"""Segments the captions based on a number of seconds."""
        if isinstance(webvtt, unicode):
            # if a string is supplied we parse the file
            captions = WebVTT().read(webvtt).captions
        elif not self._validate_webvtt(webvtt):
            raise InvalidCaptionsError(u'The captions provided are invalid')
        else:
            # we expect to have a webvtt object
            captions = webvtt.captions

        self._total_segments = 0 if not captions else int(ceil(captions[-1].end_in_seconds / seconds))
        self._output_folder = output
        self._seconds = seconds
        self._mpegts = mpegts

        output_folder = os.path.join(os.getcwdu(), output)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        self._slice_segments(captions)
        self._write_segments()
        self._write_manifest()

    @property
    def seconds(self):
        u"""Returns the number of seconds used for segmenting captions."""
        return self._seconds

    @property
    def total_segments(self):
        u"""Returns the total of segments."""
        return self._total_segments

    @property
    def segments(self):
        u"""Return the list of segments."""
        return self._segments
