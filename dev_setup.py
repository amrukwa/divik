"""This just builds the native extension for testing purposes"""

from glob import glob
from setuptools import setup, Extension
import numpy

setup(
    name='gamred_native',
    version='0.0.1',
    packages=[],
    # @gmrukwa: https://packaging.python.org/discussions/install-requires-vs-requirements/
    install_requires=[
        'numpy>=0.12.1',
    ],
    setup_requires=[
        'numpy>=0.12.1',
    ],
    python_requires='>=3.6',
    ext_modules=[
        Extension('gamred_native',
                  sources=glob('gamred_native/*.c'),
                  include_dirs=['gamred_native', numpy.get_include()],
                  define_macros=[
                      ('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION'),
                  ]),
    ],
)
