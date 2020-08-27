#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='cl2nc',
    version='3.3.0',
    description='Convert Vaisala CL51 and CL31 dat files to NetCDF',
    author='Peter Kuma',
    author_email='peter@peterkuma.net',
    license='MIT',
    py_modules=['cl2nc'],
    entry_points={
        'console_scripts': ['cl2nc=cl2nc:main'],
    },
    data_files=[('share/man/man1', ['cl2nc.1'])],
    install_requires=['netCDF4>=1.2.9'],
    keywords=['vaisala', 'ceilometer', 'cl51', 'cl31', 'netcdf', 'lidar'],
    url='https://github.com/peterkuma/cl2nc',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
    ]
)
