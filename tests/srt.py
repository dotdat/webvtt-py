# -*- coding: utf-8 -*-

from __future__ import with_statement
from __future__ import absolute_import
import os
import unittest
from shutil import rmtree, copy

import webvtt

from .generic import GenericParserTestCase
from io import open


BASE_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(BASE_DIR, u'output')


class SRTCaptionsTestCase(GenericParserTestCase):

    def setUp(self):
        os.makedirs(OUTPUT_DIR)

    def tearDown(self):
        if os.path.exists(OUTPUT_DIR):
            rmtree(OUTPUT_DIR)

    def test_convert_from_srt_to_vtt_and_back_gives_same_file(self):
        copy(self._get_file(u'sample.srt'), OUTPUT_DIR)

        vtt = webvtt.from_srt(os.path.join(OUTPUT_DIR, u'sample.srt'))
        vtt.save_as_srt(os.path.join(OUTPUT_DIR, u'sample_converted.srt'))

        with open(os.path.join(OUTPUT_DIR, u'sample.srt'), u'r', encoding=u'utf-8') as f:
            original = f.read()

        with open(os.path.join(OUTPUT_DIR, u'sample_converted.srt'), u'r', encoding=u'utf-8') as f:
            converted = f.read()

        self.assertEqual(original.strip(), converted.strip())
