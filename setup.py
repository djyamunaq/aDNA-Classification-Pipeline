from setuptools import setup
setup(
    name = 'classification-pipeline',
    version = '0.1.0',
    packages = ['src'],
    entry_points = {
        'console_scripts': [
            'classpipe = src.__main__:main'
        ]
    })