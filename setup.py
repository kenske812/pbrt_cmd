from glob import glob
 
from distutils.core import setup
from setuptools import find_packages
 
setup(
    name='pbrt_cmd',
    version='0.1.0',
    url = 'http://10.9.158.35:8080/kuchida/pbrt_cmd',
    description='PBRT interface for python',
    author='Uchida',
    author_email='kensuke.uchida@omron.com',
    packages=find_packages(),
    python_requires='>=3.7.*'
)