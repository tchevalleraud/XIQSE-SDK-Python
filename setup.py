"""
    ExtremeCloudIQ Site Engine SDK
"""

from setuptools import setup, find_packages

NAME = "xiqse"
VERSION = "25.0.0-1"

REQUIRES = [
    "urllib3 ~= 1.26.7",
]

setup(
    name=NAME,
    version=VERSION,
    description="ExtremeClouqIQ Site Engine",
    author="Thibault CHEVALLERAUD",
    author_email="tchevalleraud@extremenetworks.com",
)