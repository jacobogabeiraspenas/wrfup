# utils.py in wrfup
import os
import shutil
import logging
import xarray as xr

def check_geo_em_file(geo_em_file, field):
    """
    Check the geo_em file for the required fields before processing.
    
    Args:
        geo_em_file (str): Path to the geo_em file.
        field (str): The field to check for (FRC_URB2D or URB_PARAM).
    
    Returns:
        dataset (xarray.Dataset): The opened geo_em dataset if the file is valid and all required fields are present.
        None: If the file is invalid or fields are missing.
    """
    try:
        # Open the geo_em file using xarray
        ds = xr.open_dataset(geo_em_file)

        # Common fields to check
        required_fields = ['XLAT_M', 'XLONG_M', 'XLAT_C', 'XLONG_C']

        # Add specific fields based on user selection
        if field == 'FRC_URB2D':
            required_fields.append('FRC_URB2D')
        elif field == 'URB_PARAM':
            required_fields.append('URB_PARAM')

        # Check if all required fields are present
        missing_fields = [f for f in required_fields if f not in ds.data_vars]
        if missing_fields:
            logging.warning(f"Missing fields in geo_em file: {missing_fields}")
            ds.close()
            return None

        logging.info("All required fields are present in the geo_em file.")
        return ds

    except FileNotFoundError:
        logging.error(f"geo_em file not found: {geo_em_file}")
        return None

    except Exception as e:
        logging.error(f"An error occurred while checking the geo_em file: {e}")
        return None
    
def get_lat_lon_extent(geo_em_file):
    """
    Extract the latitude and longitude extents from the geo_em file using xarray.
    
    Args:
        geo_em_file (str): Path to the geo_em file.
    
    Returns:
        tuple: Tuple containing min/max latitudes and longitudes.
    """
    try:
        ds = xr.open_dataset(geo_em_file)
        lat_min = ds['XLAT_M'].min().item()
        lat_max = ds['XLAT_M'].max().item()
        lon_min = ds['XLONG_M'].min().item()
        lon_max = ds['XLONG_M'].max().item()
        ds.close()

        return lat_min, lat_max, lon_min, lon_max

    except Exception as e:
        logging.error(f"An error occurred while extracting lat/lon from geo_em file: {e}")
        return None
    

def clean_up(temp_dir):
    """
    Remove temporary files and directories.
    
    Args:
        temp_dir (str): The directory where temporary files are stored.
    """
    try:
        # Remove the entire temp directory and its contents
        shutil.rmtree(temp_dir)
        logging.info(f"Temporary files in {temp_dir} removed.")
    except FileNotFoundError:
        logging.info("No temporary files to remove.")
    except Exception as e:
        logging.error(f"An error occurred during clean-up: {e}")
