# -*- coding: utf-8 -*-
# übernommen aus: https://pythonhosted.org/setuptools/setuptools.html#id24
import ez_setup


ez_setup.use_setuptools()

from setuptools import setup, find_packages
setup(
      name = "DDSync",
      packages = find_packages(where="src"),
      version = '1.5.0',
      package_data={'': ["*.fmw"]},
      package_dir = {"": "src"},
      # Abhängigkeiten
      install_requires = ["configobj==5.0.6", "cx-Oracle>=5.1.3", "requests>=2.20.0", "PyMySQL==0.7.4", "lxml==4.6.2", "python-keyczar==0.715", "psycopg2>=2.7.3.1"],
      # PyPI metadata
      author = "Peter Schär",
      author_email = "peter.schaer@bve.be.ch",
      description = "Synchronisation aus GeoDBmeta in das DataDictionary der GeoDB",
      url = "https://www.be.ch/geoportal",
      entry_points={
           'console_scripts': [
                'DDSync = DDSync.__main__:main'
            ]         
      }
      # https://pythonhosted.org/setuptools/setuptools.html#automatic-script-creation
)
