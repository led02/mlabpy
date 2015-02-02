"""
MlabPy installation script (requires setuptools).

Copyright (C) 2015, led02 <mlabpy@led-inc.eu>
"""
from setuptools import setup, find_packages

setup(
    # Meta data
    name="mlabpy",
    version="0.0.1",
    description="A MatLAB frontend for Python.",
    url="https://github.com/led02/mlabpy",
    author="led02",
    author_email="mlabpy@led-inc.eu",

    # Extended meta data
    license="MIT",
    keywords='python matlab runtime parser interpreter compiler',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Indended Audience :: Scientists',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: MatLAB',
    ],

    # Dependencies
    install_requires=[
        'setuptools',
        'numpy>=1.9',
        'ply>=3.4',
    ],
    extras_require={
        'scipy': ['scipy>=1.9'],
    },
    
    # Contents
    packages=find_packages('src'),
    package_dir={
        '': 'src',
    },
    package_data={
        'mlabpy.samples': ['test.m', 'mybench.m'],
    },
    entry_points={
        'console_scripts': ['mlabpy=mlabpy.run:main'],
    },
)
