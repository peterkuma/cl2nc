#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='cl2nc',
    version='3.7.1',
    description='Convert Vaisala CL51, CL31 and CT25K DAT and HIS L2 files to NetCDF',
    author='Peter Kuma',
    author_email='peter@peterkuma.net',
    license='MIT',
    py_modules=['cl2nc'],
    entry_points={
        'console_scripts': ['cl2nc=cl2nc:main'],
    },
    data_files=[('share/man/man1', ['cl2nc.1'])],
    install_requires=[
        'numpy',
        'netCDF4>=1.2.9'
    ],
    keywords=['vaisala', 'ceilometer', 'cl51', 'cl31', 'ct25k', 'netcdf', 'lidar'],
    url='https://github.com/peterkuma/cl2nc',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
    ]
)
