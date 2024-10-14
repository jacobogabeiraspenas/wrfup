wrfup: WRF Urban Parameters Toolkit
====================================

Welcome to the **wrfup** documentation! This tool enables users to integrate high-resolution, real-world urban data into WRF simulations efficiently. It provides the functionalities to download, calculate, and ingest urban fields directly into WRF geo_em files. Using wrfup, users can enhance urban weather simulations with advanced support for urban parameterizations, including SLUCM, BEP, and BEP+BEM.

.. image:: _static/logo_wrfup.png
   :alt: wrfup logo
   :align: center
   :width: 300px


Overview
--------

**wrfup** is a Python tool designed for urban climate modeling. It allows you to:

- **Download** urban morphology data like building heights and urban fraction.
- **Calculate** the necessary urban fields for WRF, such as **URB_PARAM** and **FRC_URB2D**.
- **Ingest** these fields directly into WRF’s **geo_em** files, ensuring precise representation of urban areas in your simulations. 

.. toctree::
   :maxdepth: 2
   :caption: Sections:

   installation
   usage
   features
   modules

---

Indices and tables
===================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


