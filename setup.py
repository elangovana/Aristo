from setuptools import setup

setup(
    name='aristo',
    version='.1',
    packages=['aristo.core', 'aristo.test'],
    url='',
    license='',
    author='Team bluebird',
    author_email='',
    description='',
    tests_require = ['pytest', 'coverage'],
    install_requires=['pandas', 'nltk', 'mwapi',  ]
)
