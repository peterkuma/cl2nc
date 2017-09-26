#!/usr/bin/env python2.7

from setuptools import setup, find_packages

setup(
    name='cl2nc',
    version='1.0.3',
    description='Convert Vaisala CL51 and CL31 dat files to NetCDF',
    author='Peter Kuma',
    author_email='peter.kuma@fastmail.com',
    license='MIT',
    scripts=['cl2nc'],
    install_requires=['netCDF4>=1.2.9'],
    keywords=['vaisala', 'ceilometer', 'cl51', 'cl31', 'netcdf'],
    url='https://github.com/peterkuma/cl2nc',
)
