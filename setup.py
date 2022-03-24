#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

try:
    with open('HISTORY.rst') as history_file:
        history = history_file.read()
except FileNotFoundError:
    history = ""

requirements = ["j-chess-lib>=0.7.0", "asciimatics", "pyperclip"]

test_requirements = [ ]

setup(
    author="RedRem95",
    author_email='redrem@botschmot.de',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    description="Manager for clients designed for the awesome j-chess-server using the j-chess-lib for python",
    entry_points={
        'console_scripts': [
            'j_chess_client_manager=j_chess_client_manager.__main__:main',
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + ('\n\n' if len(history) > 0 else '') + history,
    include_package_data=True,
    keywords='j_chess_client_manager',
    name='j_chess_client_manager',
    packages=find_packages(include=['j_chess_client_manager', 'j_chess_client_manager.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/RedRem95/j_chess_client_manager',
    version='0.3.1',
    zip_safe=False,
)
