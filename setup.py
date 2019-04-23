from __future__ import with_statement
from __future__ import absolute_import
import io
from setuptools import setup

from webvtt import __version__


def readme():
    with io.open(u'README.rst', u'r', encoding=u'utf-8') as f:
        return f.read()

setup(
    name=u'webvtt-py',
    version=__version__,
    description=u'WebVTT reader, writer and segmenter',
    long_description=readme(),
    author=u'Alejandro Mendez',
    author_email=u'amendez23@gmail.com',
    url=u'https://github.com/glut23/webvtt-py',
    packages=[
        u'webvtt',
    ],
    include_package_data=True,
    install_requires=[u'docopt'],
    entry_points={
        u'console_scripts': [
            u'webvtt=webvtt.cli:main'
        ]
    },
    license=u'MIT',
    classifiers=[
        u'Development Status :: 3 - Alpha',
        u'Intended Audience :: Developers',
        u'License :: OSI Approved :: MIT License',
        u'Programming Language :: Python',
        u'Programming Language :: Python :: 3',
        u'Programming Language :: Python :: 3.3',
        u'Programming Language :: Python :: 3.4',
        u'Programming Language :: Python :: 3.5',
        u'Operating System :: OS Independent',
        u'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=u'webvtt captions',
    test_suite=u'tests'
)