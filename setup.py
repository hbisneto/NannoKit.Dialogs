# setup.py

from setuptools import setup, find_namespace_packages

setup(
    name="supernanno.dialogs",
    version="0.0.0",
    packages=find_namespace_packages(include=["supernanno.*"]),
    include_package_data=True,
    package_data={
        "supernanno.dialogs": [
            "styles/*.tcss"
        ]
    },
    install_requires=[
        "textual==8.2.3",
        "supernanno>=0.0.23"
    ],
    author="Heitor Bardemaker A. Bisneto",
    author_email="bisnetoinc@gmail.com",
    description="Dialogs extension for SuperNanno",
    python_requires=">=3.10",
)