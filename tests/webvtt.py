from __future__ import with_statement
from __future__ import absolute_import
import os
import io
from shutil import rmtree, copy

import webvtt
from webvtt.structures import Caption, Style
from .generic import GenericParserTestCase
from io import open


BASE_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(BASE_DIR, u'output')


class WebVTTTestCase(GenericParserTestCase):

    def tearDown(self):
        if os.path.exists(OUTPUT_DIR):
            rmtree(OUTPUT_DIR)

    def test_create_caption(self):
        caption = Caption(u'00:00:00.500', u'00:00:07.000', [u'Caption test line 1', u'Caption test line 2'])
        self.assertEqual(caption.start, u'00:00:00.500')
        self.assertEqual(caption.start_in_seconds, 0.5)
        self.assertEqual(caption.end, u'00:00:07.000')
        self.assertEqual(caption.end_in_seconds, 7)
        self.assertEqual(caption.lines, [u'Caption test line 1', u'Caption test line 2'])

    def test_write_captions(self):
        os.makedirs(OUTPUT_DIR)
        copy(self._get_file(u'one_caption.vtt'), OUTPUT_DIR)

        out = io.StringIO()
        vtt = webvtt.read(os.path.join(OUTPUT_DIR, u'one_caption.vtt'))
        new_caption = Caption(u'00:00:07.000', u'00:00:11.890', [u'New caption text line1', u'New caption text line2'])
        vtt.captions.append(new_caption)
        vtt.write(out)

        out.seek(0)
        lines = [line.rstrip() for line in out.readlines()]

        expected_lines = [
            u'WEBVTT',
            u'',
            u'00:00:00.500 --> 00:00:07.000',
            u'Caption text #1',
            u'',
            u'00:00:07.000 --> 00:00:11.890',
            u'New caption text line1',
            u'New caption text line2'
        ]

        self.assertListEqual(lines, expected_lines)

    def test_save_captions(self):
        os.makedirs(OUTPUT_DIR)
        copy(self._get_file(u'one_caption.vtt'), OUTPUT_DIR)

        vtt = webvtt.read(os.path.join(OUTPUT_DIR, u'one_caption.vtt'))
        new_caption = Caption(u'00:00:07.000', u'00:00:11.890', [u'New caption text line1', u'New caption text line2'])
        vtt.captions.append(new_caption)
        vtt.save()

        with open(os.path.join(OUTPUT_DIR, u'one_caption.vtt'), u'r', encoding=u'utf-8') as f:
            lines = [line.rstrip() for line in f.readlines()]

        expected_lines = [
            u'WEBVTT',
            u'',
            u'00:00:00.500 --> 00:00:07.000',
            u'Caption text #1',
            u'',
            u'00:00:07.000 --> 00:00:11.890',
            u'New caption text line1',
            u'New caption text line2'
        ]

        self.assertListEqual(lines, expected_lines)

    def test_srt_conversion(self):
        os.makedirs(OUTPUT_DIR)
        copy(self._get_file(u'one_caption.srt'), OUTPUT_DIR)

        vtt = webvtt.from_srt(os.path.join(OUTPUT_DIR, u'one_caption.srt'))
        vtt.save()

        self.assertTrue(os.path.exists(os.path.join(OUTPUT_DIR, u'one_caption.vtt')))

        with open(os.path.join(OUTPUT_DIR, u'one_caption.vtt'), u'r', encoding=u'utf-8') as f:
            lines = [line.rstrip() for line in f.readlines()]

        expected_lines = [
            u'WEBVTT',
            u'',
            u'00:00:00.500 --> 00:00:07.000',
            u'Caption text #1',
        ]

        self.assertListEqual(lines, expected_lines)

    def test_sbv_conversion(self):
        os.makedirs(OUTPUT_DIR)
        copy(self._get_file(u'two_captions.sbv'), OUTPUT_DIR)

        vtt = webvtt.from_sbv(os.path.join(OUTPUT_DIR, u'two_captions.sbv'))
        vtt.save()

        self.assertTrue(os.path.exists(os.path.join(OUTPUT_DIR, u'two_captions.vtt')))

        with open(os.path.join(OUTPUT_DIR, u'two_captions.vtt'), u'r', encoding=u'utf-8') as f:
            lines = [line.rstrip() for line in f.readlines()]

        expected_lines = [
            u'WEBVTT',
            u'',
            u'00:00:00.378 --> 00:00:11.378',
            u'Caption text #1',
            u'',
            u'00:00:11.378 --> 00:00:12.305',
            u'Caption text #2 (line 1)',
            u'Caption text #2 (line 2)',
        ]

        self.assertListEqual(lines, expected_lines)

    def test_save_to_other_location(self):
        target_path = os.path.join(OUTPUT_DIR, u'test_folder')
        os.makedirs(target_path)

        webvtt.read(self._get_file(u'one_caption.vtt')).save(target_path)
        self.assertTrue(os.path.exists(os.path.join(target_path, u'one_caption.vtt')))

    def test_save_specific_filename(self):
        target_path = os.path.join(OUTPUT_DIR, u'test_folder')
        os.makedirs(target_path)
        output_file = os.path.join(target_path, u'custom_name.vtt')

        webvtt.read(self._get_file(u'one_caption.vtt')).save(output_file)
        self.assertTrue(os.path.exists(output_file))

    def test_save_specific_filename_no_extension(self):
        target_path = os.path.join(OUTPUT_DIR, u'test_folder')
        os.makedirs(target_path)
        output_file = os.path.join(target_path, u'custom_name')

        webvtt.read(self._get_file(u'one_caption.vtt')).save(output_file)
        self.assertTrue(os.path.exists(os.path.join(target_path, u'custom_name.vtt')))

    def test_caption_timestamp_update(self):
        c = Caption(u'00:00:00.500', u'00:00:07.000')
        c.start = u'00:00:01.750'
        c.end = u'00:00:08.250'

        self.assertEqual(c.start, u'00:00:01.750')
        self.assertEqual(c.end, u'00:00:08.250')

    def test_caption_timestamp_format(self):
        c = Caption(u'01:02:03.400', u'02:03:04.500')
        self.assertEqual(c.start, u'01:02:03.400')
        self.assertEqual(c.end, u'02:03:04.500')

        c = Caption(u'02:03.400', u'03:04.500')
        self.assertEqual(c.start, u'00:02:03.400')
        self.assertEqual(c.end, u'00:03:04.500')

    def test_caption_text(self):
        c = Caption(text=[u'Caption line #1', u'Caption line #2'])
        self.assertEqual(
            c.text,
            u'Caption line #1\nCaption line #2'
        )

    def test_caption_receive_text(self):
        c = Caption(text=u'Caption line #1\nCaption line #2')

        self.assertEqual(
            len(c.lines),
            2
        )
        self.assertEqual(
            c.text,
            u'Caption line #1\nCaption line #2'
        )

    def test_update_text(self):
        c = Caption(text=u'Caption line #1')
        c.text = u'Caption line #1 updated'
        self.assertEqual(
            c.text,
            u'Caption line #1 updated'
        )

    def test_update_text_multiline(self):
        c = Caption(text=u'Caption line #1')
        c.text = u'Caption line #1\nCaption line #2'

        self.assertEqual(
            len(c.lines),
            2
        )

        self.assertEqual(
            c.text,
            u'Caption line #1\nCaption line #2'
        )

    def test_update_text_wrong_type(self):
        c = Caption(text=u'Caption line #1')

        self.assertRaises(
            AttributeError,
            setattr,
            c,
            u'text',
            123
        )

    def test_manipulate_lines(self):
        c = Caption(text=[u'Caption line #1', u'Caption line #2'])
        c.lines[0] = u'Caption line #1 updated'
        self.assertEqual(
            c.lines[0],
            u'Caption line #1 updated'
        )

    def test_captions(self):
        vtt = webvtt.read(self._get_file(u'sample.vtt'))
        self.assertIsInstance(vtt.captions, list)

    def test_captions_prevent_write(self):
        vtt = webvtt.read(self._get_file(u'sample.vtt'))
        self.assertRaises(
            AttributeError,
            setattr,
            vtt,
            u'captions',
            []
        )

    def test_sequence_iteration(self):
        vtt = webvtt.read(self._get_file(u'sample.vtt'))
        self.assertIsInstance(vtt[0], Caption)
        self.assertEqual(len(vtt), len(vtt.captions))

    def test_save_no_filename(self):
        vtt = webvtt.WebVTT()
        self.assertRaises(
            webvtt.errors.MissingFilenameError,
            vtt.save
        )

    def test_malformed_start_timestamp(self):
        self.assertRaises(
            webvtt.errors.MalformedCaptionError,
            Caption,
            u'01:00'
        )

    def test_set_styles_from_text(self):
        style = Style()
        style.text = u'::cue(b) {\n  color: peachpuff;\n}'
        self.assertListEqual(
            style.lines,
            [u'::cue(b) {', u'  color: peachpuff;', u'}']
        )

    def test_get_styles_as_text(self):
        style = Style()
        style.lines = [u'::cue(b) {', u'  color: peachpuff;', u'}']
        self.assertEqual(
            style.text,
            u'::cue(b) {color: peachpuff;}'
        )

    def test_save_identifiers(self):
        os.makedirs(OUTPUT_DIR)
        copy(self._get_file(u'using_identifiers.vtt'), OUTPUT_DIR)

        vtt = webvtt.read(os.path.join(OUTPUT_DIR, u'using_identifiers.vtt'))
        vtt.save(os.path.join(OUTPUT_DIR, u'new_using_identifiers.vtt'))

        with open(os.path.join(OUTPUT_DIR, u'new_using_identifiers.vtt'), u'r', encoding=u'utf-8') as f:
            lines = [line.rstrip() for line in f.readlines()]

        expected_lines = [
            u'WEBVTT',
            u'',
            u'00:00:00.500 --> 00:00:07.000',
            u'Caption text #1',
            u'',
            u'second caption',
            u'00:00:07.000 --> 00:00:11.890',
            u'Caption text #2',
            u'',
            u'00:00:11.890 --> 00:00:16.320',
            u'Caption text #3',
            u'',
            u'4',
            u'00:00:16.320 --> 00:00:21.580',
            u'Caption text #4',
            u'',
            u'00:00:21.580 --> 00:00:23.880',
            u'Caption text #5',
            u'',
            u'00:00:23.880 --> 00:00:27.280',
            u'Caption text #6'
        ]

        self.assertListEqual(lines, expected_lines)

    def test_save_updated_identifiers(self):
        os.makedirs(OUTPUT_DIR)
        copy(self._get_file(u'using_identifiers.vtt'), OUTPUT_DIR)

        vtt = webvtt.read(os.path.join(OUTPUT_DIR, u'using_identifiers.vtt'))
        vtt.captions[0].identifier = u'first caption'
        vtt.captions[1].identifier = None
        vtt.captions[3].identifier = u'44'
        last_caption = Caption(u'00:00:27.280', u'00:00:29.200', u'Caption text #7')
        last_caption.identifier = u'last caption'
        vtt.captions.append(last_caption)
        vtt.save(os.path.join(OUTPUT_DIR, u'new_using_identifiers.vtt'))

        with open(os.path.join(OUTPUT_DIR, u'new_using_identifiers.vtt'), u'r', encoding=u'utf-8') as f:
            lines = [line.rstrip() for line in f.readlines()]

        expected_lines = [
            u'WEBVTT',
            u'',
            u'first caption',
            u'00:00:00.500 --> 00:00:07.000',
            u'Caption text #1',
            u'',
            u'00:00:07.000 --> 00:00:11.890',
            u'Caption text #2',
            u'',
            u'00:00:11.890 --> 00:00:16.320',
            u'Caption text #3',
            u'',
            u'44',
            u'00:00:16.320 --> 00:00:21.580',
            u'Caption text #4',
            u'',
            u'00:00:21.580 --> 00:00:23.880',
            u'Caption text #5',
            u'',
            u'00:00:23.880 --> 00:00:27.280',
            u'Caption text #6',
            u'',
            u'last caption',
            u'00:00:27.280 --> 00:00:29.200',
            u'Caption text #7'
        ]

        self.assertListEqual(lines, expected_lines)
