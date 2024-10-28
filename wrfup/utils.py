# utils.py in wrfup
import os
import shutil
import logging
import xarray as xr

def first_checks(info):
    """
    Perform the first checks before processing the geo_em file. 
    This includes checking if the geo_em file exists, the work directory exists, and the field is valid.

    Args:
        info (Info): An Info object containing the paths and configuration.
    
    Returns:
        int: 1 if there is an error
    """
    # Check if the work directory and geo_em file exist
    path_to_geo_em = os.path.join(info.work_dir, info.geo_em_file)

    if not os.path.exists(info.work_dir):
        logging.error(f"Work directory not found: {info.work_dir}")
        return 1

    if not os.path.exists(path_to_geo_em):
        logging.error(f"geo_em file not found: {info.geo_em_file}")
        return 1

    if info.field not in ['FRC_URB2D', 'URB_PARAM']:
        logging.error(f"Invalid field: {info.field}. Please choose from FRC_URB2D or URB_PARAM.")
        return 1
    
    return 0

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

        # Fields to check
        required_fields = ['XLAT_M', 'XLONG_M', 'XLAT_C', 'XLONG_C']

        # Add specific fields based on user selection
        required_fields.append(field)

        # Check if all required fields are present
        missing_fields = [f for f in required_fields if f not in ds.data_vars]
        if missing_fields:
            logging.warning(f"Missing fields in geo_em file: {missing_fields}")
        else:
            pass
            #logging.info("All required fields are present in the geo_em file.")

        # Check if field is the correct shape
        if field == 'FRC_URB2D':
            if len(ds[field].shape) != 3:
                logging.warning(f"Field {field} is not the correct shape. Expected 2D array.")
        elif field == 'URB_PARAM':
            if ds[field].shape[1] != 131:
                logging.warning(f"Field {field} is not the correct shape. Expected array with shape (1, 131, nx, ny). Instead got shape {ds[field].shape}. This can cause issues.")
                rewrite_confirm = input(f"Would you like to rewrite this field? (y/n): ").lower()
                if rewrite_confirm == 'y':
                    logging.info(f"Rewriting field {field}...")
                    # Rewrite the field
                    ds = ds.drop_vars(field)
                else:
                    pass

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
