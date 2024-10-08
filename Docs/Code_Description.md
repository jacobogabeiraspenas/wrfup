## wrfup Python Package Documentation

### Overview

The **wrfup** package is designed to process and ingest urban data into the WRF (Weather Research and Forecasting) model's `geo_em.d0X.nc` file. It helps calculate and integrate urban canopy parameters like **urban fraction**, **building heights**, and **plan area fraction**, following the **NUDAPT 44** framework. The package automates tasks like downloading geospatial tiles, calculating urban parameters, and updating the `geo_em` dataset.

### Main Features
1. **Automatic Tile Downloading**: Downloads geospatial tiles (urban fraction, URB_PARAM) based on the geographical extent of the WRF model domain.
2. **Tile Merging**: Combines multiple downloaded tiles into a single GeoTIFF file, applying compression.
3. **Urban Parameter Calculations**: Calculates several urban canopy parameters, including Plan Area Fraction, Weighted Building Height, and Frontal Area Index (FAI) for four cardinal directions.
4. **Field Ingestion into WRF**: The calculated urban parameters are ingested into the `geo_em.d0X.nc` file, following the NUDAPT 44 structure.

---

### Code Modules

#### 1. `main.py`
The **entry point** for the package, responsible for handling the overall workflow, including downloading tiles, calculating parameters, and updating the WRF geo_em file.

- **Key Workflow**:
  1. Parse command-line arguments (input `geo_em.d0X.nc` file, field type).
  2. Check for required fields in the geo_em file.
  3. Download the necessary tiles for the urban fraction or URB_PARAM.
  4. Calculate parameters (urban fraction, building heights, etc.).
  5. Update the geo_em file with new urban parameters.

- **Important Functions**:
  - `check_geo_em_file`: Ensures that required fields (e.g., `FRC_URB2D`, `URB_PARAM`) exist in the geo_em file.
  - `calculate_frc_urb2d`: Computes the **urban fraction** for each grid cell in the WRF domain.
  - `calculate_urb_param`: Computes the **URB_PARAM** fields such as **LAMBDA_P**, **LAMBDA_B**, **building height distribution**, and **FAI**.

#### 2. `download.py`
Handles the **downloading and merging of geospatial tiles** based on the WRF model's lat/lon extent.

- **Key Features**:
  - **Tile Existence Check**: Before downloading, the function checks whether the tile already exists locally to avoid redundant downloads.
  - **Merge Tiles**: If multiple tiles are downloaded, the tiles are merged into a single compressed GeoTIFF.
  - **Download Tracking**: Uses `tqdm` to display a progress bar during the download process.

- **Important Functions**:
  - `download_tiles`: Downloads the tiles, either urban fraction or URB_PARAM, based on lat/lon extent.
  - `merge_tiles`: Merges multiple tiles into a single GeoTIFF file.
  - `lat_lon_to_tile_indices`: Converts lat/lon to tile indices to determine which tiles to download.

#### 3. `calculation.py`
Contains functions for calculating **urban canopy parameters** (e.g., LAMBDA_P, LAMBDA_B, building heights, FAI) from the downloaded tiles.

- **Urban Parameter Calculation**:
  - **LAMBDA_P (Plan Area Fraction)**: Fraction of the grid cell's area covered by building footprints.
  - **LAMBDA_B (Frontal Area Fraction)**: Fraction of the grid cell's frontal area occupied by building walls.
  - **Frontal Area Index (FAI)**: Ratio of wall area to dilated area, calculated for four directions (North, South, East, West).
  - **Building Height Distribution**: Distribution of building heights into predefined 5-meter bins.

- **Important Functions**:
  - `calculate_urb_param`: Computes the full set of **URB_PARAM** fields and updates the geo_em file.
  - `calculate_frc_urb2d`: Computes the **urban fraction** (FRC_URB2D) from the downloaded tiles and updates the geo_em file.

#### 4. `utils.py`
Utility functions for **checking the geo_em file**, extracting lat/lon extents, and cleaning up temporary files.

- **Key Functions**:
  - `check_geo_em_file`: Ensures that the geo_em file contains the required fields before processing.
  - `get_lat_lon_extent`: Extracts the latitude and longitude extent from the geo_em file, necessary for determining the area of interest.
  - `clean_up`: Removes temporary files after processing.

#### 5. `info.py`
Defines a class to store configuration and paths, including paths for the geo_em file, working directory, and temporary directory.

- **Important Class**:
  - `Info`: Stores the configuration details for the processing, including paths and field information.

---

### Key Urban Canopy Parameters
The **NUDAPT 44** format defines several urban canopy parameters. The wrfup package calculates these and ingests them into the WRF geo_em file.

1. **Plan Area Fraction (LAMBDA_P)**: Fraction of the grid cell's area covered by building footprints.
   - Stored in slice [90,:,:] of `URB_PARAM`.
   
2. **Frontal Area Fraction (LAMBDA_B)**: Fraction of the grid cell's frontal area occupied by building walls.
   - Stored in slice [94,:,:] of `URB_PARAM`.

3. **Building Height Distribution**: Distribution of building heights in the grid cell.
   - Stored in slices [117:132,:,:] of `URB_PARAM`.

4. **Frontal Area Index (FAI)**: Wall area divided by the dilated area, calculated for four directions (N, S, E, W).
   - Stored in slices [96:99,:,:] of `URB_PARAM`.

---

### Workflow Summary

1. **Command-Line Interface**: The user specifies the path to the geo_em file, the field to be ingested (`FRC_URB2D` or `URB_PARAM`), and optional working and temp directories.
2. **Geo_em File Check**: The package ensures that the geo_em file contains the necessary fields and extracts the lat/lon extent for tile downloading.
3. **Tile Download and Merge**: Based on the lat/lon extent, the necessary geospatial tiles are downloaded and merged into a single GeoTIFF file.
4. **Urban Canopy Calculations**: Urban parameters such as Plan Area Fraction, Building Height Distribution, and Frontal Area Index are calculated from the merged tile data.
5. **Field Ingestion**: The calculated urban parameters are ingested into the WRF geo_em file, following the NUDAPT 44 data structure.

---

### Conclusion

The **wrfup** package automates and simplifies the ingestion of urban data into the WRF model. It follows the NUDAPT 44 standard for urban canopy parameters and is designed to handle geospatial data downloading, merging, calculation, and ingestion in a single workflow. It helps ensure that urban parameters like **plan area fraction**, **building heights**, and **frontal area index** are correctly integrated into WRF simulations.

This package is highly useful for users needing detailed urban canopy parameterizations in their WRF simulations, especially when working with urban climate modeling.
