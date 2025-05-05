from setuptools import setup


def get_long_description():
    with open('README.md') as f:
        return f.read()


setup(
    name='uniswap-viewer',
    version="0.1.0",
    packages=['uniswap_viewer'],
    author="Alexander Fomalhaut",
    url="https://github.com/fomalhaut88/uniswap-viewer",
    license="MIT",
    description="Lightweight Python library for reading Uniswap V3 prices and tick data via Web3.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    install_requires=[
        'aiohttp>=3.11',
        'pdoc>=15.0',
        'requests>=2.32',
        'web3>=7.11',
    ],
    package_data={
        'uniswap_viewer': ['source/*.json'],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="uniswap v3 web3 defi ethereum blockchain async",
)
