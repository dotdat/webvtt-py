from __future__ import absolute_import
import os
import unittest


class GenericParserTestCase(unittest.TestCase):

    SUBTITLES_DIR = os.path.join(os.path.dirname(__file__), u'subtitles')

    def _get_file(self, filename):
        return os.path.join(self.SUBTITLES_DIR, filename)
