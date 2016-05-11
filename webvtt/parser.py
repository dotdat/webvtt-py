from .exceptions import MalformedFileError


class WebVTTParser:

    def _parse(self, content):
        self.content = content

    def read(self, file):
        with open(file, encoding='utf-8') as f:
            self._parse(f.readlines())
        if len(self.content) == 0:
            raise MalformedFileError('The file is empty')
        if not self.is_valid():
            raise MalformedFileError('The file does not have a valid format')

        return self

    def is_valid(self):
        return 'WEBVTT' in self.content[0]