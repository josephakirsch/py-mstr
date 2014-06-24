
from setuptools import find_packages, setup

setup(name='py-mstr',
    packages=find_packages(),  
    description = 'Python API for Microstrategy Web Tasks',
    url = 'http://github.com/infoscout/py-mstr',
    install_requires=[
        'pyquery==1.2.8',
        'requests==2.3.0',
    ],
    tests_require=[
        'mox==0.5.3',
    ],
)