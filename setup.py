from setuptools import setup


def get_long_description():
    with open('README.md') as f:
        return f.read()


setup(
    name='uniswap-viewer',
    version="0.1.0",
    packages=['uniswap_viewer'],
    license="MIT",
    description="",
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
)
