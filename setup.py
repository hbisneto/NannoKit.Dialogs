# -*- coding: utf-8 -*-
from setuptools import setup, find_namespace_packages

setup(
    name="nannokit_dialogs",
    version="0.0.19",
    description="Official dialogs extension for SuperNanno",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Heitor Bardemaker A. Bisneto",
    author_email="bisnetoinc@gmail.com",
    license="BSD-3-Clause",
    url="https://github.com/hbisneto/SuperNanno",

    packages=find_namespace_packages(include=["nannokit*"]),
    include_package_data=True,
    package_data={
        "nannokit.dialogs.styles": ["*.tcss"],
    },

    install_requires=["textual>=8.2.7"],
    python_requires=">=3.10",

    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Text Editors",
        "Typing :: Typed",
    ],

    zip_safe=False,
)