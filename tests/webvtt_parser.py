# -*- coding: utf-8 -*-

from __future__ import absolute_import
from .generic import GenericParserTestCase

import webvtt
from webvtt.parsers import WebVTTParser
from webvtt.structures import Caption
from webvtt.errors import MalformedFileError, MalformedCaptionError


class WebVTTParserTestCase(GenericParserTestCase):

    def test_webvtt_parse_invalid_file(self):
        self.assertRaises(
            MalformedFileError,
            webvtt.read,
            self._get_file(u'invalid.vtt')
        )

    def test_webvtt_captions_not_found(self):
        self.assertRaises(
            OSError,
            webvtt.read,
            u'some_file'
        )

    def test_webvtt_total_length(self):
        self.assertEqual(
            webvtt.read(self._get_file(u'sample.vtt')).total_length,
            64
        )

    def test_webvtt_total_length_no_parser(self):
        self.assertEqual(
            webvtt.WebVTT().total_length,
            0
        )

    def test_webvtt__parse_captions(self):
        self.assertTrue(webvtt.read(self._get_file(u'sample.vtt')).captions)

    def test_webvtt_parse_empty_file(self):
        self.assertRaises(
            MalformedFileError,
            webvtt.read,
            self._get_file(u'empty.vtt')
        )

    def test_webvtt_parse_get_captions(self):
        self.assertEqual(
            len(webvtt.read(self._get_file(u'sample.vtt')).captions),
            16
        )

    def test_webvtt_parse_invalid_timeframe_line(self):
        self.assertRaises(
            MalformedCaptionError,
            webvtt.read,
            self._get_file(u'invalid_timeframe.vtt')
        )

    def test_webvtt_parse_invalid_timeframe_in_cue_text(self):
        self.assertRaises(
            MalformedCaptionError,
            webvtt.read,
            self._get_file(u'invalid_timeframe_in_cue_text.vtt')
        )

    def test_webvtt_parse_get_caption_data(self):
        vtt = webvtt.read(self._get_file(u'one_caption.vtt'))
        self.assertEqual(vtt.captions[0].start_in_seconds, 0.5)
        self.assertEqual(vtt.captions[0].start, u'00:00:00.500')
        self.assertEqual(vtt.captions[0].end_in_seconds, 7)
        self.assertEqual(vtt.captions[0].end, u'00:00:07.000')
        self.assertEqual(vtt.captions[0].lines[0], u'Caption text #1')
        self.assertEqual(len(vtt.captions[0].lines), 1)

    def test_webvtt_caption_without_timeframe(self):
        self.assertRaises(
            MalformedCaptionError,
            webvtt.read,
            self._get_file(u'missing_timeframe.vtt')
        )

    def test_webvtt_caption_without_cue_text(self):
        vtt = webvtt.read(self._get_file(u'missing_caption_text.vtt'))
        self.assertEqual(len(vtt.captions), 5)

    def test_webvtt_timestamps_format(self):
        vtt = webvtt.read(self._get_file(u'sample.vtt'))
        self.assertEqual(vtt.captions[2].start, u'00:00:11.890')
        self.assertEqual(vtt.captions[2].end, u'00:00:16.320')

    def test_parse_timestamp(self):
        caption = Caption(start=u'02:03:11.890')
        self.assertEqual(
            caption.start_in_seconds,
            7391.89
        )

    def test_captions_attribute(self):
        self.assertListEqual([], webvtt.WebVTT().captions)

    def test_webvtt_timestamp_format(self):
        self.assertTrue(WebVTTParser()._validate_timeframe_line(u'00:00:00.000 --> 00:00:00.000'))
        self.assertTrue(WebVTTParser()._validate_timeframe_line(u'00:00.000 --> 00:00.000'))

    def test_metadata_headers(self):
        vtt = webvtt.read(self._get_file(u'metadata_headers.vtt'))
        self.assertEqual(len(vtt.captions), 2)

    def test_metadata_headers_multiline(self):
        vtt = webvtt.read(self._get_file(u'metadata_headers_multiline.vtt'))
        self.assertEqual(len(vtt.captions), 2)

    def test_parse_identifiers(self):
        vtt = webvtt.read(self._get_file(u'using_identifiers.vtt'))
        self.assertEqual(len(vtt.captions), 6)

        self.assertEqual(vtt.captions[1].identifier, u'second caption')
        self.assertEqual(vtt.captions[2].identifier, None)
        self.assertEqual(vtt.captions[3].identifier, u'4')

    def test_parse_with_comments(self):
        vtt = webvtt.read(self._get_file(u'comments.vtt'))
        self.assertEqual(len(vtt.captions), 3)
        self.assertListEqual(
            vtt.captions[0].lines,
            [u'- Ta en kopp varmt te.',
             u'- Det är inte varmt.']
        )
        self.assertEqual(
            vtt.captions[2].text,
            u'- Ta en kopp'
        )

    def test_parse_styles(self):
        vtt = webvtt.read(self._get_file(u'styles.vtt'))
        self.assertEqual(len(vtt.captions), 1)
        self.assertEqual(
            vtt.styles[0].text,
            u'::cue {background-image: linear-gradient(to bottom, dimgray, lightgray);color: papayawhip;}'
        )

    def test_clean_cue_tags(self):
        vtt = webvtt.read(self._get_file(u'cue_tags.vtt'))
        self.assertEqual(
            vtt.captions[1].text,
            u'Like a big-a pizza pie'
        )
        self.assertEqual(
            vtt.captions[2].text,
            u'That\'s amore'
        )

    def test_parse_captions_with_bom(self):
        vtt = webvtt.read(self._get_file(u'captions_with_bom.vtt'))
        self.assertEqual(len(vtt.captions), 4)
