# wrfup/main.py
import argparse
import logging
import os
from wrfup.info import Info
from wrfup.download import download_tiles, get_tile_names_in_aoi
from wrfup.ingest import ingest_fields
from wrfup.utils import clean_up, check_geo_em_file, get_lat_lon_extent, first_checks
from wrfup.calculation import calculate_frc_urb2d, calculate_urb_param

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("wrfup.log"),
        logging.StreamHandler()
    ]
)

# Hardcoded download URLs for urban fraction and URB_PARAM tiles
FRC_URB2D_URL = "https://github.com/jacobogabeiraspenas/UrbanData01/raw/main/data/00_UrbanFraction/zoom_4_complete"
URB_PARAM_URL = "https://github.com/jacobogabeiraspenas/UrbanData01/raw/main/data/01_URB_PARAM/zoom_4"

def main(argv=None):
    """Main entry point for wrfup package."""
    
    parser = argparse.ArgumentParser(
        description="Ingest urban data (FRC_URB2D, URB_PARAM) into geo_em.d0X.nc file."
    )

    # Required arguments
    parser.add_argument('geo_em_file', type=str, help="Path to the WRF geo_em.d0X.nc file.")
    parser.add_argument('field', type=str, choices=['FRC_URB2D', 'URB_PARAM'], 
                        help="Field to ingest into the geo_em file.")
    
    # Optional arguments
    parser.add_argument('--work_dir', type=str, default='./workdir', 
                        help="Working directory where geo_em files and output will be stored (default: ./workdir).")
    parser.add_argument('--temp_dir', type=str, default='./temp', 
                        help="Directory for temporary files (default: ./temp).")

    args = parser.parse_args(argv)

    # Create an Info object to store paths and configuration
    info = Info.from_argparse(args)

    # Step 1: First checks. Check the geo_em file for required fields and return the dataset
    if first_checks(info) != 0:
        return 1

    # Step 2: Check the geo_em file for required fields and return the dataset
    geo_em_path = os.path.join(info.work_dir, info.geo_em_file)
    ds = check_geo_em_file(geo_em_path, info.field)
    
    # Step 3: Create field-specific directory inside the work directory
    field_dir = os.path.join(info.temp_dir, info.field)
    if not os.path.exists(field_dir):
        os.makedirs(field_dir)

    # Step 4: Get latitude/longitude extent from geo_em file
    lat_min, lat_max, lon_min, lon_max = get_lat_lon_extent(geo_em_path)

    # Step 5: Get tile names based on geo_em file’s extent
    tile_names = get_tile_names_in_aoi(lat_min, lat_max, lon_min, lon_max, info.field)

    # Step 6: Download the necessary tiles based on field
    if info.field == 'FRC_URB2D':
        merged_tiff_path = download_tiles(tile_names, field_dir, FRC_URB2D_URL)
    elif info.field == 'URB_PARAM':
        merged_tiff_path = download_tiles(tile_names, field_dir, URB_PARAM_URL)

    # Step 7: Perform calculations to prepare data for ingestion
    # merged_tiff_path = os.path.join(field_dir, 'merged_tiles.tif')
    if info.field == 'FRC_URB2D':
        # logging.info("Calculating FRC_URB2D field...")
        ds = calculate_frc_urb2d(info, ds, merged_tiff_path)
    elif info.field == 'URB_PARAM':
        # logging.info("Calculating URB_PARAM fields...")
        ds = calculate_urb_param(info, ds, merged_tiff_path)

    # Step 8: Write the modified dataset to a new file
    output_geo_em_path = geo_em_path.replace('.nc', f'_{info.field}.nc')
    # logging.info(f"Ingesting {info.field} into the geo_em file...")
    ds.to_netcdf(output_geo_em_path)
    logging.info(f"Modified geo_em file saved to {output_geo_em_path}")

    # # Step 8: Clean up temporary files
    # logging.info("Cleaning up temporary files...")
    # clean_up(info.temp_dir)

    logging.info("Process completed successfully.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
