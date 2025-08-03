"""
    ExtremeCloudIQ Site Engine SDK
"""

from setuptools import setup, find_packages

NAME = "XIQSE"
VERSION = "25.8.0-1"

REQUIRES = [
    "urllib3 ~= 1.26.7",
]

setup(
    name=NAME,
    version=VERSION,
    description="ExtremeClouqIQ Site Engine",
    author="Thibault CHEVALLERAUD",
    author_email="tchevalleraud@extremenetworks.com",
    packages=find_packages(include=["XIQSE", "XIQSE.*"]),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent"
    ]
)