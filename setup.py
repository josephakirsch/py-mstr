
from setuptools import find_packages, setup

setup(name='py-mstr',
    packages=find_packages(),  
    description = 'Python API for Microstrategy Web Tasks',
    url = 'http://github.com/infoscout/py-mstr',
    install_requires=[
        'pyquery',
        'requests',
    ],
)