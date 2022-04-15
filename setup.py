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
        "dev": [
            "black",
            "moonworm >= 0.1.9",
        ],
        "distribute": ["setuptools", "twine", "wheel"],
    },
    description="Inspector Facet - What methods is your EIP2535 Diamond proxy contract serving?",
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
    package_data={"inspector_facet": ["version.txt", "abis/*.json"]},
    include_package_data=True,
)
