#!/usr/bin/env python3
# coding: utf-8

from glob import glob
from setuptools import setup

desc = """jmail - lightweight HTML5 django webmail"""

install_requires = [
    'Django>=1.9,<1.10',
]

def _version():
    with open('jmail/version.py', 'r') as fh:
        for l in fh.readlines():
            if l.startswith('VERSION ='):
                v = l.split('=')[1].strip().replace("'", "")
                break
        fh.close()
    print('jmail v%s' % v)
    return v

setup(
    name='jmail',
    version=_version(),

    description=desc,
    long_description=desc,

    license='BSD',
    url='https://github.com/jrmsgit/py3-jmail',

    author='Jeremías Casteglione',
    author_email='git@jrms.com.ar',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
    ],

    install_requires=install_requires,

    packages=[
        'jmail',
        'jmail.macct',
        'jmail.mdir',
        'jmail.msg',
        'jmail.user',
        'jmailcmd',
    ],

    package_dir={
        'jmail': 'jmail',
        'jmailcmd': 'jmailcmd',
        'themes': 'themes',
    },

    data_files=[
        ('themes/default/static/js', glob('themes/default/static/js/*.js')),
        ('themes/default/static/css', glob('themes/default/static/css/*.css')),
        ('themes/default/templates', glob('themes/default/templates/*.html')),
        ('themes/default/templates/macct',
                glob('themes/default/templates/macct/*.html')),
        ('themes/default/templates/mdir',
                glob('themes/default/templates/mdir/*.html')),
        ('themes/default/templates/msg',
                glob('themes/default/templates/msg/*.html')),
        ('themes/default/templates/user',
                glob('themes/default/templates/user/*.html')),
    ],

    entry_points={
        'console_scripts': [
            'jmail=jmailcmd:main',
        ],
    },
)
