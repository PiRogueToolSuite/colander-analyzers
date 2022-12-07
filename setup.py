#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='colander-analyzers',
    version='1.0',
    author='Esther Onfroy',
    author_email='esther@pts-project.org',
    maintainer='Esther Onfroy',
    url='https://github.com/PiRogueToolSuite/colander-analyzers',
    description='Observables enrichment and artifact analysis for Colander based on MISP-modules',
    packages=find_packages(),
    entry_points={'console_scripts': ['colander-analyzers = colander_analyzers:main']},
    test_suite="tests",
    classifiers=[
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'Topic :: Security',
    ],
    install_requires=[
        'tornado',
        'psutil',
        'redis>=3',
        'pyparsing==2.4.7'
    ],
)
