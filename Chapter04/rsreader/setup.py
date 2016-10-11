from ez_setup import use_setuptools
use_setuptools(version='0.6c7')

from setuptools import setup, find_packages


setup(
    # basic package data
    name = "RSReader_chapter04",
    version = "0.1",

    # package structure and dependencies
    packages=find_packages('src'),
    package_dir={'':'src'},
    entry_points = {
	'console_scripts': [
		'rsreader = rsreader.application:main'
		]
	},
    install_requires = [
                        'docutils == 0.4',
                        'nose == 0.10.0',
                        ],

    # metadata for upload to PyPI
    author = "Jeff Younker",
    author_email = "nobody@example.com",
    description = "The sample rss reader for agile methods in python",
    license = "BSD",
    keywords = "continuous integration release engineering scm automation",
    url = "http://www.example.com/",   # project home page, if any
)
 
