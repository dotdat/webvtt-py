from __future__ import absolute_import
import webvtt

from .generic import GenericParserTestCase


class SRTParserTestCase(GenericParserTestCase):

    def test_srt_parse_empty_file(self):
        self.assertRaises(
            webvtt.errors.MalformedFileError,
            webvtt.from_srt,
            self._get_file(u'empty.vtt')  # We reuse this file as it is empty and serves the purpose.
        )

    def test_srt_invalid_format(self):
        for i in xrange(1, 5):
            self.assertRaises(
                webvtt.errors.MalformedFileError,
                webvtt.from_srt,
                self._get_file(u'invalid_format{}.srt'.format(i))
            )

    def test_srt_total_length(self):
        self.assertEqual(
            webvtt.from_srt(self._get_file(u'sample.srt')).total_length,
            23
        )

    def test_srt_parse_captions(self):
        self.assertTrue(webvtt.from_srt(self._get_file(u'sample.srt')).captions)

    def test_srt_missing_timeframe_line(self):
        self.assertRaises(
            webvtt.errors.MalformedCaptionError,
            webvtt.from_srt,
            self._get_file(u'missing_timeframe.srt')
        )

    def test_srt_empty_caption_text(self):
        self.assertTrue(webvtt.from_srt(self._get_file(u'missing_caption_text.srt')).captions)

    def test_srt_empty_gets_removed(self):
        captions = webvtt.from_srt(self._get_file(u'missing_caption_text.srt')).captions
        self.assertEqual(len(captions), 4)

    def test_srt_invalid_timestamp(self):
        self.assertRaises(
            webvtt.errors.MalformedCaptionError,
            webvtt.from_srt,
            self._get_file(u'invalid_timeframe.srt')
        )

    def test_srt_timestamps_format(self):
        vtt = webvtt.from_srt(self._get_file(u'sample.srt'))
        self.assertEqual(vtt.captions[2].start, u'00:00:11.890')
        self.assertEqual(vtt.captions[2].end, u'00:00:16.320')

    def test_srt_parse_get_caption_data(self):
        vtt = webvtt.from_srt(self._get_file(u'one_caption.srt'))
        self.assertEqual(vtt.captions[0].start_in_seconds, 0.5)
        self.assertEqual(vtt.captions[0].start, u'00:00:00.500')
        self.assertEqual(vtt.captions[0].end_in_seconds, 7)
        self.assertEqual(vtt.captions[0].end, u'00:00:07.000')
        self.assertEqual(vtt.captions[0].lines[0], u'Caption text #1')
        self.assertEqual(len(vtt.captions[0].lines), 1)
