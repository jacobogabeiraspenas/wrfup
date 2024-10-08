"""
wrfup - A Python package for ingesting urban data into WRF geo_em files.

This package helps to:
- Download fields like FRC_URB2D and URB_PARAM.
- Calculate required fields for ingestion.
- Ingest those fields into the geo_em file.

Modules:
    - main: Entry point for the command-line tool.
    - info: Handles configuration and argument parsing.
    - download: Functions to download required fields.
    - calculation: Functions to calculate fields for ingestion.
    - ingest: Functions to ingest fields into the WRF geo_em file.
    - utils: Utility functions (e.g., clean-up and file validation).
"""
from .main import main
from .info import Info
from .download import download_tiles, download_and_extract_zip, get_tile_names_in_aoi, get_total_download_size, lat_lon_to_tile_indices, merge_tiles
from .calculation import add_frc_urb2d_field_if_not_exists, add_urb_param_fields_if_not_exists, calculate_frc_urb2d, calculate_urb_param, crop_opened_tiff_by_lat_lon_bounds_and_return_mosaic
from .utils import clean_up, check_geo_em_file, get_lat_lon_extent


# # Import essential components of the package
# from .main import main
# from .info import Info
# from .download import download_fields
# from .calculation import calculate_fields
# from .ingest import ingest_fields
# from .utils import clean_up, check_geo_em_file

# # Define the package version
# __version__ = "0.1.0"
# # wrfup module initialization
