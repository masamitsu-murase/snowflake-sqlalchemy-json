from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='snowflake-sqlalchemy-json',
    version='0.1.0',
    description='A library to handle JSON with snowflake-sqlalchemy.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/masamitsu-murase/snowflake-sqlalchemy-json',
    author='Masamitsu MURASE',
    author_email='masamitsu.murase@gmail.com',
    license='MIT',
    keywords='snowflake sqlalchemy',
    py_modules=["snowflake_sqlalchemy_json"],
    package_dir={"": "src"},
    zip_safe=True,
    python_requires='>=3.7.*, <4',
    install_requires=['snowflake-sqlalchemy'],
    extras_require={'test': [], 'package': ['wheel', 'twine']},
    project_urls={
        'Bug Reports':
        'https://github.com/masamitsu-murase/snowflake-sqlalchemy-json/issues',
        'Source':
        'https://github.com/masamitsu-murase/snowflake-sqlalchemy-json',
    },
)
