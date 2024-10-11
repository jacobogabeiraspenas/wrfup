Usage
=====

**wrfup** is primarily used through its command-line interface (CLI) to work with WRF geo_em files.

Basic Command Structure
-----------------------
You can use `wrfup` to calculate and ingest the **URB_PARAM** or **FRC_URB2D** fields directly into WRF’s geo_em files.

To calculate and ingest **URB_PARAM** fields:
.. code-block:: bash

   wrfup geo_em.d0X.nc URB_PARAM --work_dir YOUR_DIRECTORY

To calculate and ingest **FRC_URB2D** fields:
.. code-block:: bash

   wrfup geo_em.d0X.nc FRC_URB2D --work_dir YOUR_DIRECTORY

### Options:
- `geo_em.d0X.nc`: The WRF geo_em file for the target domain (replace X with domain number).
- `--work_dir`: Specify the directory where intermediate and final files will be stored.

Example Use Case
----------------
Let's say you're working on an urban climate simulation for a specific city. After downloading the necessary urban morphology data, you'd want to insert that data into the WRF model:

1. Prepare your `geo_em.d0X.nc` file.
2. Run the following command to compute the **URB_PARAM** field:

.. code-block:: bash

   wrfup geo_em.d01.nc URB_PARAM --work_dir /path/to/working_directory

3. You can now visualize and analyze the results in the modified **geo_em** file.

