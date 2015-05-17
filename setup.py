from setuptools import setup

__version__ = '1.0'

setup(
    name='linthints',
    version=__version__,
    install_requires=['pylint>=1.4.3'],
    py_modules=['linthints']
)
