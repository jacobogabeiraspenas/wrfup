# wrfup (WRF Urban Parameters Toolkit)

**wrfup** is a Python package designed to help users ingest real-world, high-resolution urban morphology data into WRF (Weather Research and Forecasting) geo_em files. It provides robust functionalities to **download**, **calculate**, and **ingest** crucial urban fields such as **FRC_URB2D** (Urban Fraction) and **URB_PARAM** (Urban Parameters). These fields are essential for accurate urban weather modeling and are compatible with several WRF urban parameterizations, including **BEP (Building Energy Parameterization)**, **BEP+BEM (Building Energy Model)**, and **SLUCM (Single-Layer Urban Canopy Model)**.

The package allows for the ingestion of data related to urban canopy features, such as building fraction, heights, and urban area coverage, from multiple high-resolution sources (e.g., **World Settlement Footprint 3D**, **Microsoft Buildings**). These detailed datasets significantly improve the representation of urban surfaces in WRF, leading to more precise simulations of urban heat islands, microclimates, and energy exchanges.

## Features

- **Download Urban Data:** Easily download urban fraction and urban parameter tiles for any area of interest.
- **Calculate Fields:** Compute the necessary fields (e.g., FRC_URB2D, URB_PARAM) for WRF urban simulations.
- **Ingest Data:** Automatically insert the calculated fields into WRF geo_em files.
- **Command-line Tool:** Provides a user-friendly CLI to facilitate all operations.

## Installation

To install the `wrfup` package, simply use `pip`:

```bash
pip install wrfup
```

## Usage

### Command-Line Interface (CLI)

You can use `wrfup` as a command-line tool to work with WRF geo_em files:

```bash
wrfup geo_em.d0X.nc URB_PARAM --work_dir YOUR_DIRECTORY
```

## Modules

`wrfup` includes the following modules:

- **`main`**: The entry point for the command-line interface.
- **`download`**: Functions to download urban data tiles.
- **`calculation`**: Functions to compute required fields (e.g., FRC_URB2D, URB_PARAM).
- **`utils`**: Utility functions like file cleanup and validation.
- **`info`**: Handles configuration and argument parsing.

## Requirements

`wrfup` relies on the following Python packages:

- `numpy`
- `tqdm`
- `requests`
- `netCDF4`
- `pandas`
- `shapely`
- `fiona`
- `xarray`
- `scipy`

## Development

To set up a development environment for `wrfup`, clone the repository and install the dependencies:

```bash
git clone https://github.com/jacobogabeiraspenas/wrfup.git
cd wrfup
pip install -r requirements.txt
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

If you have any questions or suggestions, feel free to open an issue or reach out to the author:

**Jacobo Gabeiras Penas**  
Email: jacobogabeiras@gmail.com

