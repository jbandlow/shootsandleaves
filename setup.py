r"""Simple setup.py file."""

import setuptools

with open('README.rst', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    author='Jason Bandlow',
    author_email='jbandlow@gmail.com',
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ),
    description='Declarative framework for loading JSON into Pandas',
    include_package_data=True,
    install_requires=['pandas', 'six'],
    long_description=long_description,
    name='shootsandleaves',
    packages=setuptools.find_packages(),
    url='https://github.com/jbandlow/shootsandleaves',
    version='0.0.1',
)
