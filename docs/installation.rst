Installation
============

Python
------

This package is working on Python version 3.6+.

* On Windows, we recommend to install Python through the distribution Anaconda: https://www.anaconda.com/ 
* On older versions of Windows (before Windows 7), we recommend to install Python manually: https://www.python.org/
* On Linux, we recommend to install Python through the apt-get command.

Additional required packages (installed automatically with Autolab):

* numpy
* pandas
* pyvisa
* python-vxi11

Autolab package
---------------

This project is hosted in the global python repository PyPi at the following address : https://pypi.org/project/autolab/
To install the Autolab python package on your computer, we then advice you to use the Python package manager ``pip`` in a Python environnement:	

.. code-block:: none

	pip install autolab
	
If the package is already installed, you can check the current version installed and upgrade it to the last official version with the following commands:

.. code-block:: none
	
	pip show autolab
	pip install autolab --upgrade
	
Import the Autolab package in a Python shell to check that the installation is correct.

.. code-block:: python

	>>> import autolab
	
	
PyQt5 for the GUI
-----------------

The GUI requires the package PyQt5. But depending if you are using Anaconda or not, the installation is different:

With Anaconda:

.. code-block:: none

	conda install pyqt
	
Without:

.. code-block:: none

	pip install pyqt5
	
	
Development version
-------------------

You can install the latest development version (at your own risk) directly form GitHub:

.. code-block:: none

	pip install http://github.com/qcha41/autolab/zipball/master
	



