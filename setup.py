from setuptools import setup
setup(
    name = 'classification-pipeline',
    version = '0.1.0',
    packages = ['classpipe'],
    entry_points = {
        'console_scripts': [
            'classpipe = classpipe.__main__:main'
        ]
    })