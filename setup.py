import unittest
import tests
from setuptools import setup,find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

def test_suite():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(tests)
    return suite

setup(name='apx',
      version='0.4.4b1',
      description='Official APX python toolchain and client',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
      ],
      url='http://github.com/cogu/apx/python3',
      author='Conny Gustafsson',
      author_email='congus8@gmail.com',
      license='MIT',
      install_requires=[
         'cfile==0.2.0',
         'autosar<0.5.0'
      ],
      packages=['apx','remotefile'],
      py_modules=['numheader'],
      test_suite = 'tests',
      zip_safe=False)