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
      # Abhängigkeiten
      install_requires = [],
      # PyPI metadata
      author = "Peter Schär",
      author_email = "peter.schaer@bve.be.ch",
      description = "Synchronisation aus GeoDBmeta in das DataDictionary der GeoDB",
      url = "http://www.be.ch/geoportal",
      # TODO: entry_points einfügen (console_script)
      # https://pythonhosted.org/setuptools/setuptools.html#automatic-script-creation
)
