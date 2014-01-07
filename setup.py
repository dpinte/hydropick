"""
Hydropick
=========

Tool for automatic and interactive sediment analysis in hydrological surveys.

"""
import os.path
from setuptools import setup, find_packages

info = {}
execfile(os.path.join('hydropick', '__init__.py'), info)

setup(
    name='hydropick',
    version=info['__version__'],
    url='http://github.com/twdb/hydropick',
    author='Dharhas Pothina, Andy Wilson and Enthought developers',
    author_email='dharhas.pothina@twdb.texas.gov',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    description='Sediment analysis in hydrological surveys',
    long_description = open('README.md').read(),
    install_requires=info['__requires__'],
    license='BSD',
    maintainer='Dharhas Pothina',
    maintainer_email='dharhas.pothina@twdb.texas.gov',
    package_data={},
    packages=find_packages(),
    platforms=["Windows", "Linux", "Mac OS-X", "Unix"],
    zip_safe=False,
)
