#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    'Unidecode==1.0.23',
]

test_requirements = [
    'pytest',
]

setup(
    name='geotext',
    version='0.4.0',
    description='Geotext extracts country and city mentions from text',
    long_description=readme + '\n\n' + history,
    author='Denis Kovalev (fork from Yaser Martinez Palenzuela version)',
    author_email='aikikode@gmail.com',
    url='https://github.com/aikikode/geotext',
    packages=['geotext', 'geotext.models', 'geotext.tasks', ],
    package_dir={'geotext': 'geotext', },
    include_package_data=True,
    package_data={'geotext': ['geotext/data/*.txt', ], },
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='geotext',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    setup_requires=['pytest-runner', ],
    test_suite='tests',
    tests_require=test_requirements
)
