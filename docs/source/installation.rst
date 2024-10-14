Installation
============

To install the latest stable release of **wrfup**, use `pip`:

.. code-block:: bash

   pip install wrfup

You can also install from TestPyPI:

.. code-block:: bash

   pip install -i https://test.pypi.org/simple/ wrfup



System Requirements
--------------------
- Python 3.8 or above.
- The package is compatible with major operating systems (Linux, macOS, Windows).
- Dependencies: The `requirements.txt` includes necessary dependencies such as `xarray`, `scipy`, `netCDF4`, and others.
  
Make sure to set up your environment before installing the package by running:

.. code-block:: bash

   pip install -r https://raw.githubusercontent.com/jacobogabeiraspenas/wrfup/main/requirements.txt

Or you can install the dependencies manually:

.. code-block:: bash

   numpy==1.24.4
   tqdm==4.64.0
   requests==2.32.2
   netCDF4==1.5.7
   pandas==2.2.3
   shapely==2.0.2
   fiona==1.8.22
   rasterio==1.3.6
   xarray==2024.7.0
   scipy==1.9.3
