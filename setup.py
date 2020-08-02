import os
import sys
from setuptools import setup, find_packages
from shutil import rmtree

setup(
    name="Cartridge QuickBooks Payment Processor",
    version="0.0.2",
    author="John Groszko",
    author_email="john@tinythunk.com",
    description="A payment processor for cartridge that integrates with QuickBooks Payments API",
    license="BSD",
    url="http://github.com/jgroszko/cartridge-quickbooks",
    zip_safe=False,
    packages=['quickbooks',],
    install_requires=[
        'intuit-oauth==1.2.2',
        ],
    )
