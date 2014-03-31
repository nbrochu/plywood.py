#!/usr/bin/env python
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as f:
    version = f.read()

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    long_description = f.read()

setup(
    name='plywood-python',
    version=version,
    description='Logstash Websocket Multiplexer (Python)',
    long_description=long_description,
    url='http://github.com/nbrochu/plywood.py',
    author='Nicholas Brochu',
    author_email='info@nicholasbrochu.com',
    maintainer='Nicholas Brochu',
    maintainer_email='info@nicholasbrochu.com',
    keywords=['Logstash', 'WebSocket', 'Multiplexing'],
    license='MIT',
    packages=['plywood'],
    install_requires=[
        'pyzmq==14.1.1',
        'autobahn[twisted]==0.8.6',
        'redis==2.9.1'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7'
    ]
)