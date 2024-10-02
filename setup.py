from setuptools import find_packages, setup

setup(
    name="url-snapshotter",
    version="1.0.0",
    description="A tool to capture and compare snapshots of URLs.",
    author="Vince van Daal",
    author_email="vince-os@vandaal.io",
    url="git@github.com:vvdaal/url-snaphotter.git",
    packages=find_packages(),
    install_requires=[
        "aiohappyeyeballs>=2.4.3",
        "aiohttp>=3.10.8",
        "aiosignal>=1.3.1",
        "attrs>=24.2.0",
        "certifi>=2024.8.30",
        "charset-normalizer>=3.3.2",
        "click>=8.1.7",
        "frozenlist>=1.4.1",
        "greenlet>=3.1.1",
        "idna>=3.10",
        "iniconfig>=2.0.0",
        "inquirerpy>=0.3.4",
        "multidict>=6.1.0",
        "packaging>=24.1",
        "pfzy>=0.3.4",
        "pluggy>=1.5.0",
        "prompt_toolkit>=3.0.48",
        "pytest>=8.3.3",
        "pytest-asyncio>=0.24.0",
        "requests>=2.32.3",
        "SQLAlchemy>=2.0.35",
        "termcolor>=2.3.0",
        "typing_extensions>=4.12.2",
        "urllib3>=2.2.3",
        "wcwidth>=0.2.13",
        "yarl>=1.13.1",
        "yaspin>=3.1.0",
    ],
    entry_points={
        "console_scripts": [
            "url-snapshotter=url_snapshotter.cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
