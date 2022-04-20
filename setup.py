from setuptools import find_packages, setup

long_description = ""
with open("README.md") as ifp:
    long_description = ifp.read()

with open("inspector_facet/version.txt") as ifp:
    VERSION = ifp.read().strip()

setup(
    name="inspector-facet",
    version=VERSION,
    packages=find_packages(),
    install_requires=["eth-brownie", "tqdm"],
    extras_require={
        "dev": ["black"],
        "distribute": ["setuptools", "twine", "wheel"],
    },
    description="Inspector Facet - Inspection utility for EIP2535 Diamond proxies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Moonstream",
    author_email="engineering@moonstream.to",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.6",
    url="https://github.com/bugout-dev/inspector-facet",
    entry_points={
        "console_scripts": [
            "inspector-facet=inspector_facet.cli:main",
        ]
    },
    package_data={
        "inspector_facet": [
            "version.txt",
            "abis/*.json",
            "fixtures/*.json",
            "fixtures/*.jsonl",
        ]
    },
    include_package_data=True,
)
