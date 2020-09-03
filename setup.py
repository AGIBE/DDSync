# -*- coding: utf-8 -*-
# übernommen aus: https://pythonhosted.org/setuptools/setuptools.html#id24
import ez_setup
from DDSync import __version__

ez_setup.use_setuptools()

from setuptools import setup, find_packages
setup(
      name = "DDSync",
      packages = find_packages(),
      version = __version__,
      package_data={'': ["*.fmw"]},
      # Abhängigkeiten
      install_requires = ["configobj==5.0.6", "cx-Oracle>=5.1.3", "requests>=2.20.0", "PyMySQL==0.7.4", "lxml==3.4.4", "python-keyczar==0.715", "psycopg2>=2.7.3.1"],
      # PyPI metadata
      author = "Peter Schär",
      author_email = "peter.schaer@bve.be.ch",
      description = "Synchronisation aus GeoDBmeta in das DataDictionary der GeoDB",
      url = "https://www.be.ch/geoportal",
      entry_points={
           'console_scripts': [
                'DDSync = DDSync.helpers.commandline_helper:main'
            ]         
      }
      # https://pythonhosted.org/setuptools/setuptools.html#automatic-script-creation
)
