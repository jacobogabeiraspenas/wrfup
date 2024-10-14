
# wrfup: WRF Urban Parameters Toolkit
## A Python Tool for Ingesting Urban Morphology Data into WRF Simulations

<p align="center">
  <img src="https://raw.githubusercontent.com/jacobogabeiraspenas/wrfup/main/docs/source/_static/logo_wrfup.png" alt="wrfup logo" width="300">
</p>

**wrfup** is a Python package that ingests high-resolution urban morphology data into **WRF** (Weather Research and Forecasting). It automatically **downloads**, **calculates**, and **ingests** urban fields like **FRC_URB2D** (Urban Fraction) and **URB_PARAM** (Urban Parameters) directly into WRF's **geo_em** files. These fields are essential for accurate urban weather simulations and are compatible with WRF parameterizations like **BEP**, **BEP+BEM**, and **SLUCM**, by following the system of National Urban Data and Access Portal Tool (NUDAPT).

The package integrates urban data such as urban fraction, building heights, building surface fraction and others from high-resolution sources like **World Settlement Footprint 3D**, **Global Urban Fraction**, and the **UrbanSurfAce Project**. This data improves the representation of urban surfaces, leading to more precise simulations of urban heat islands, microclimates, and energy exchanges.

## Features

The package automatically:

- **Downloads** urban morphology data like building heights and urban fraction.
- **Calculates** the necessary urban fields for WRF: **URB_PARAM** and **FRC_URB2D**.
- **Ingests** these fields directly into WRF's **geo_em** files.

## Installation

To install the `wrfup` package:

```bash
pip install wrfup
```

or install from TestPyPI:

```bash
pip install -i https://test.pypi.org/simple/ wrfup
```

## Workflow

This diagram shows how **wrfup** integrates into the WRF preprocessing workflow:

![wrfup workflow](https://raw.githubusercontent.com/jacobogabeiraspenas/wrfup/main/docs/source/_static/workflow_wrfup.png)

## Usage

### Command-Line Interface (CLI)

You can use `wrfup` to calculate and ingest **URB_PARAM** or **FRC_URB2D** fields into **geo_em** files:

```bash
wrfup geo_em.d0X.nc URB_PARAM --work_dir YOUR_DIRECTORY
```

or

```bash
wrfup geo_em.d0X.nc FRC_URB2D --work_dir YOUR_DIRECTORY
```

## Example Use Case

1. Prepare your `geo_em.d0X.nc` file.
2. Run the following command to compute the **URB_PARAM** field:

```bash
wrfup geo_em.d03.nc URB_PARAM --work_dir /path/to/working_directory
```

3. The updated file will be saved as `geo_em_URB_PARAM.d03.nc`. 
4. To compute **FRC_URB2D**, run the command:

```bash
wrfup geo_em_URB_PARAM.d03.nc FRC_URB2D --work_dir /path/to/working_directory
```

5. Rename the final file for **metgrid**:

```bash
mv geo_em_URB_PARAM_FRC_URB2D.d03.nc geo_em.d03.nc
```

## Documentation

For detailed instructions and documentation, visit the [wrfup Documentation](https://wrfup.readthedocs.io/en/latest/).


## Development

Clone the repository and install the dependencies:

```bash
git clone https://github.com/jacobogabeiraspenas/wrfup.git
cd wrfup
pip install -r requirements.txt
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

Questions or suggestions? Open an issue or reach out:

**Jacobo Gabeiras Penas**  
Email: jacobogabeiras@gmail.com

