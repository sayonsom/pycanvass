from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='pycanvass',
      version='0.0.2.10',
      description='Python API for Cyber Attack and Network Vulnerability Assessment Software for Smartgrid',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
      ],
      keywords='smartgrid power system substation cyber-attack simulation rtds gridlabd python',
      url='http://github.com/sayonsom/pycanvass',
      author='Sayonsom Chanda',
      author_email='sayon@ieee.org',
      license='GPL',
      packages=['pycanvass'],
      install_requires=[
          'numpy',
          'networkx',
          'matplotlib',
          'scapy',
          'pandas',
          'sklearn',
          'graphviz',
          'progressbar2',
      ],
      extras_require = {
            'test': ['coverage', 'pytest', 'pytest-cov'],
        },
      entry_points = {
            'console_scripts': [
                'pycanvass=pycanvass.all:main',
            ],
        },
      )