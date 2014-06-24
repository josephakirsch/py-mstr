
from setuptools import find_packages, setup

tests_require=['mox==0.5.3']
if platform.python_version() < '2.7':
    tests_require.append("unittest2")
setup(name='py-mstr',
    packages=find_packages(),  
    description = 'Python API for Microstrategy Web Tasks',
    url = 'http://github.com/infoscout/py-mstr',
    install_requires=[
        'pyquery==1.2.8',
        'requests==2.3.0',
    ],
    tests_require=tests_require
    test_suite= "tests.run_tests",
)
