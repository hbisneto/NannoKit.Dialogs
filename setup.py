# setup.py (melhorado)
from setuptools import setup, find_namespace_packages

setup(
    name="supernanno.dialogs",
    version="0.0.1",                    # aumente quando lançar
    description="Official dialogs extension for SuperNanno",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Heitor Bardemaker A. Bisneto",
    author_email="bisnetoinc@gmail.com",
    license="BSD-3-Clause",
    url="https://github.com/hbisneto/SuperNanno",
    packages=find_namespace_packages(include=["supernanno.*"]),
    include_package_data=True,
    package_data={
        "supernanno.dialogs": ["styles/*.tcss"],
    },
    install_requires=[
        "textual>=8.2.7",
        "supernanno>=0.0.23",   # dependência do core
    ],
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Textual",
        "Intended Audience :: Developers",
        "Topic :: Text Editors",
        "License :: OSI Approved :: BSD License",
    ],
)