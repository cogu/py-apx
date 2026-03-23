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

setup(name='py-apx',
      version='0.4.4',
      description='A framework for sending AUTOSAR signal data to non-AUTOSAR applications',
      long_description=readme(),
      long_description_content_type='text/x-rst',

      classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
      ],
      url='http://github.com/cogu/py-apx',
      project_urls={
        'Documentation': 'https://py-apx.readthedocs.io/'
      },
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