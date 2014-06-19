
from setuptools import find_packages, setup, current_version

setup(name='py-mstr',
    packages=find_packages(),  
    description = 'Python API for Microstrategy Web Tasks',
    url = 'http://github.com/infoscout/py-mstr',
    version = current_version(),   
    install_requires=[
        'pyquery',
        'requests',
    ],
)