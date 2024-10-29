# wrfup/calculation.py
import rasterio
import numpy as np
import xarray as xr
from tqdm.auto import tqdm
from rasterio.windows import from_bounds


# wrfup/calculation.py
import rasterio
import numpy as np
import xarray as xr
from tqdm.auto import tqdm
from rasterio.windows import from_bounds
from scipy.ndimage import sobel

def calculate_urb_param(info, geo_em_ds, merged_tiff_path, field_name='URB_PARAM'):
    """
    Calculate the URB_PARAM field.

    This calculation follows the **NUDAPT 44** field structure:
    
    - **LAMBDA_P (Plan Area Fraction)**: 
      Stored in slice [90,:,:] of `URB_PARAM`. It represents the fraction of the grid cell's area covered by building footprints.

    - **Mean Building Height (Geometric Mean)**:
      Stored in slice [91,:,:] of `URB_PARAM`. It is the geometric mean of building heights within the grid cell.

    - **Standard Deviation of Building Heights**:
      Stored in slice [92,:,:] of `URB_PARAM`. It calculates the standard deviation of building heights.

    - **Weighted Building Height**:
      Stored in slice [93,:,:] of `URB_PARAM`. It represents the average building height weighted by the planar surface area (LAMBDA_P).
    
    - **LAMBDA_B (Frontal Area Fraction)**:
      Stored in slice [94,:,:] of `URB_PARAM`. It represents the fraction of the grid cell's frontal area occupied by building walls.

    - **Frontal Area Index (FAI)**:
      - **North**: Stored in slice [96,:,:] of `URB_PARAM`.
      - **South**: Stored in slice [97,:,:] of `URB_PARAM`.
      - **East**: Stored in slice [98,:,:] of `URB_PARAM`.
      - **West**: Stored in slice [99,:,:] of `URB_PARAM`.
    
    - **Building Height Distribution**:
      Stored in slices [117:132,:,:] of `URB_PARAM`.
    
    The building height distribution is computed using the following bin ranges (in meters):
    - 0-5, 5-10, 10-15, ..., up to 70+ meters.

    Args:
        info (Info): The configuration object containing paths and settings.
        geo_em_ds (xarray.Dataset): The opened geo_em dataset.
        merged_tiff_path (str): Path to the merged GeoTIFF file containing LAMBDA_B, LAMBDA_P, and Building Heights.
        field_name (str): The field name to store the data (default: 'URB_PARAM').

    Returns:
        xarray.Dataset: Updated geo_em dataset with calculated URB_PARAM fields.
    """


    # Ensure URB_PARAM fields exist in geo_em and are initialized
    geo_em_ds = add_urb_param_fields_if_not_exists(geo_em_ds)

    # Open the merged GeoTIFF containing LAMBDA_B, LAMBDA_P, and Building Heights
    with rasterio.open(merged_tiff_path) as src:
        # Define the lat/lon coordinates of the geo_em grid
        lats_c_geo_em = geo_em_ds['XLAT_C'][0].values  # Latitude corners
        lons_c_geo_em = geo_em_ds['XLONG_C'][0].values  # Longitude corners

        # Initialize arrays to store the URB_PARAM fields
        lambda_b_grid = np.zeros(geo_em_ds['XLAT_M'].shape[1:])
        lambda_p_grid = np.zeros(geo_em_ds['XLAT_M'].shape[1:])
        weighted_building_height_grid = np.zeros(geo_em_ds['XLAT_M'].shape[1:])
        mean_building_height_grid = np.zeros(geo_em_ds['XLAT_M'].shape[1:])
        std_building_height_grid = np.zeros(geo_em_ds['XLAT_M'].shape[1:])
        
        # Arrays for Frontal Area Index (FAI) for four directions
        frontal_area_index = np.zeros(geo_em_ds['XLAT_M'].shape[1:])

        # Define the bin edges and labels for building height distribution
        bin_edges = [2.5, 7.5, 12.5, 17.5, 22.5, 27.5, 32.5, 37.5, 42.5, 47.5, 52.5, 57.5, 62.5, 67.5, 72.5, 2000]
        bin_labels = range(117, 132)  # URB_PARAM slices for height distribution

        
        # Loop through each grid cell in geo_em and calculate the averages for LAMBDA_B, LAMBDA_P,
        # weighted building heights, mean building heights, standard deviation, FAI, and height distribution
        for i in tqdm(range(lats_c_geo_em.shape[0] - 1), desc="Calculating URB_PARAM"):
            for j in range(lons_c_geo_em.shape[1] - 1):
                # Define lat/lon bounds for the current grid cell
                lat_min, lat_max = lats_c_geo_em[i, j], lats_c_geo_em[i + 1, j + 1]
                lon_min, lon_max = lons_c_geo_em[i, j], lons_c_geo_em[i + 1, j + 1]

                # Crop the GeoTIFF based on these lat/lon bounds and return the mosaics
                lambda_b_mosaic, _ = crop_opened_tiff_by_lat_lon_bounds_and_return_mosaic(src, 1, lat_min, lat_max, lon_min, lon_max)
                lambda_p_mosaic, _ = crop_opened_tiff_by_lat_lon_bounds_and_return_mosaic(src, 2, lat_min, lat_max, lon_min, lon_max)
                building_height_mosaic, _ = crop_opened_tiff_by_lat_lon_bounds_and_return_mosaic(src, 3, lat_min, lat_max, lon_min, lon_max)

                # Replace invalid values (e.g., 255) with zero and calculate the averages
                lambda_b_mosaic = np.where(lambda_b_mosaic == 255, 0, lambda_b_mosaic) / 20.0  # Scale factor for LAMBDA_B
                lambda_p_mosaic = np.where(lambda_p_mosaic == 255, 0, lambda_p_mosaic) / 100.0  # Scale factor for LAMBDA_P
                building_height_mosaic = np.where(building_height_mosaic == 255, 0, building_height_mosaic)

                # Store the averaged LAMBDA_B and LAMBDA_P values
                lambda_b_grid[i, j] = np.nanmean(lambda_b_mosaic)
                lambda_p_grid[i, j] = np.nanmean(lambda_p_mosaic)
                
                # Weighted building height calculation
                if np.nansum(lambda_p_mosaic) > 0:
                    weighted_building_height_grid[i, j] = np.nansum(building_height_mosaic * lambda_p_mosaic) / np.nansum(lambda_p_mosaic)
                else:
                    weighted_building_height_grid[i, j] = 0  # Handle empty grid cells
                
                # Calculate geometric mean and standard deviation of building heights
                valid_heights = building_height_mosaic[building_height_mosaic > 1]  # Exclude invalid, zero or too small heights
                if valid_heights.size > 0:
                    mean_building_height_grid[i, j] = np.exp(np.mean(np.log(valid_heights))) # Geometric mean
                    std_building_height_grid[i, j] = np.std(valid_heights)  # Standard deviation
                else:
                    mean_building_height_grid[i, j] = 0
                    std_building_height_grid[i, j] = 0

                # Compute FAI for each direction
                fai_ij = np.nanmean(lambda_b_mosaic - lambda_p_mosaic)
                if fai_ij > 0:
                    frontal_area_index[i, j] = fai_ij / 4 # FAI for each direction 
                else:
                    frontal_area_index[i, j] = 0

                # Calculate building height distribution for this grid cell
                bin_indices = np.digitize(building_height_mosaic, bins=bin_edges)
                if np.nansum(lambda_p_mosaic) > 0:
                    for idx, bin_label in enumerate(bin_labels):
                        geo_em_ds['URB_PARAM'][0, bin_label, i, j] = np.nansum(lambda_p_mosaic * (bin_indices == (idx + 1))) / np.nansum(lambda_p_mosaic) * 100 # Convert to percentage
                else:
                    for bin_label in bin_labels:
                        geo_em_ds['URB_PARAM'][0, bin_label, i, j] = 0

    # Store the calculated values in the geo_em dataset
    geo_em_ds['URB_PARAM'][0, 90, :, :] = lambda_p_grid  # Field 90: LAMBDA_P
    geo_em_ds['URB_PARAM'][0, 91, :, :] = mean_building_height_grid  # Field 91: Geometric mean of building heights
    geo_em_ds['URB_PARAM'][0, 92, :, :] = std_building_height_grid  # Field 92: Standard deviation of building heights
    geo_em_ds['URB_PARAM'][0, 93, :, :] = weighted_building_height_grid  # Field 93: Building Height (weighted)
    geo_em_ds['URB_PARAM'][0, 94, :, :] = lambda_b_grid  # Field 94: LAMBDA_B
    
    # Store the Frontal Area Index for each direction
    geo_em_ds['URB_PARAM'][0, 96, :, :] = frontal_area_index  # Field 96: FAI North
    geo_em_ds['URB_PARAM'][0, 97, :, :] = frontal_area_index  # Field 97: FAI South
    geo_em_ds['URB_PARAM'][0, 98, :, :] = frontal_area_index  # Field 98: FAI East
    geo_em_ds['URB_PARAM'][0, 99, :, :] = frontal_area_index  # Field 99: FAI West

    return geo_em_ds

def add_urb_param_fields_if_not_exists(geo_em_ds):
    """Ensure that the geo_em file contains the URB_PARAM fields, initialized if necessary."""
    # Check if the URB_PARAM field exists
    if 'URB_PARAM' not in geo_em_ds:
        # Initialize the URB_PARAM field with zeros
        time_dim = geo_em_ds.dims['Time']
        num_slices = 132  # Number of slices (including lambda_b, lambda_p, etc.)
        south_north_dim = geo_em_ds.dims['south_north']
        west_east_dim = geo_em_ds.dims['west_east']
        urb_param_data = np.zeros((time_dim, num_slices, south_north_dim, west_east_dim), dtype=np.float32)

        # Create the DataArray and add it to the geo_em dataset
        geo_em_ds['URB_PARAM'] = xr.DataArray(
            urb_param_data,
            dims=['Time', 'urb_param_slices', 'south_north', 'west_east'],
            attrs={
                'FieldType': 104,
                'MemoryOrder': 'XYZ ',
                'units': 'various',
                'description': 'Urban canopy parameters',
                'stagger': 'M',
                'sr_x': 1,
                'sr_y': 1
            }
        )
    
    return geo_em_ds



def calculate_frc_urb2d(info, geo_em_ds, merged_tiff_path, field_name='FRC_URB2D'):
    """
    Calculate the FRC_URB2D field by averaging urban fraction values within each geo_em grid cell.
    
    Args:
        info (Info): The configuration object containing paths and settings.
        geo_em_ds (xarray.Dataset): The opened geo_em dataset.
        merged_tiff_path (str): Path to the merged GeoTIFF file containing urban fraction data.
        field_name (str): The field name to store the data (default: 'FRC_URB2D').
    
    Returns:
        np.ndarray: 2D array of calculated FRC_URB2D values.
    """
    # Ensure FRC_URB2D field exists in geo_em and is initialized
    geo_em_ds = add_frc_urb2d_field_if_not_exists(geo_em_ds, field_name)

    # Open the merged GeoTIFF containing urban fraction data
    with rasterio.open(merged_tiff_path) as src:
        # Initialize an array to store the urban fraction for each grid cell
        urban_fraction_geo_em = np.zeros(geo_em_ds['XLAT_M'].shape[1:])

        # Define the lat/lon coordinates of the geo_em grid
        lats_c_geo_em = geo_em_ds['XLAT_C'][0].values  # Latitude corners
        lons_c_geo_em = geo_em_ds['XLONG_C'][0].values  # Longitude corners

        # Loop through each grid cell in geo_em and calculate the average urban fraction from GeoTIFF
        for i in tqdm(range(lats_c_geo_em.shape[0] - 1), desc="Calculating FRC_URB2D"):
            for j in range(lons_c_geo_em.shape[1] - 1):
                # Define lat/lon bounds for the current grid cell
                lat_min, lat_max = lats_c_geo_em[i, j], lats_c_geo_em[i + 1, j + 1]
                lon_min, lon_max = lons_c_geo_em[i, j], lons_c_geo_em[i + 1, j + 1]

                # Crop the GeoTIFF based on these lat/lon bounds and return the mosaic
                mosaic, transform = crop_opened_tiff_by_lat_lon_bounds_and_return_mosaic(src, 1, lat_min, lat_max, lon_min, lon_max)

                # Replace invalid values (e.g., 255) with zero and calculate the average
                mosaic = np.where(mosaic == 255, 0, mosaic)  # Adjust based on your invalid value
                urban_fraction_geo_em[i, j] = np.nanmean(mosaic) / 100.0  # Convert to fraction (0-1)

        # Store the calculated urban fraction in the geo_em dataset
        geo_em_ds[field_name][0] = urban_fraction_geo_em

    return geo_em_ds


def add_frc_urb2d_field_if_not_exists(geo_em_ds, field_name):
    """Ensure that the geo_em file contains the FRC_URB2D field, initialized if necessary."""
    if field_name not in geo_em_ds:
        # Initialize the FRC_URB2D field with zeros
        time_dim = geo_em_ds.dims['Time']
        south_north_dim = geo_em_ds.dims['south_north']
        west_east_dim = geo_em_ds.dims['west_east']
        frc_urb2d_data = np.zeros((time_dim, south_north_dim, west_east_dim), dtype=np.float32)

        # Create the DataArray and add it to the geo_em dataset
        geo_em_ds[field_name] = xr.DataArray(
            frc_urb2d_data,
            dims=['Time', 'south_north', 'west_east'],
            attrs={
                'FieldType': 104,
                'MemoryOrder': 'XY ',
                'units': 'fraction',
                'description': 'Urban Fraction',
                'stagger': 'M',
                'sr_x': 1,
                'sr_y': 1
            }
        )
        geo_em_ds.attrs['FLAG_FRC_URB2D'] = 1  # Mark the flag for FRC_URB2D field

    return geo_em_ds


def crop_opened_tiff_by_lat_lon_bounds_and_return_mosaic(src, band, lat_min, lat_max, lon_min, lon_max):
    """
    Crop an open rasterio dataset to the specified latitude and longitude bounds and return the cropped mosaic as a numpy array.
    
    Args:
        src: rasterio.io.DatasetReader, an open rasterio dataset.
        band: int, the band to read.
        lat_min: float, minimum latitude of the cropping boundary.
        lat_max: float, maximum latitude of the cropping boundary.
        lon_min: float, minimum longitude of the cropping boundary.
        lon_max: float, maximum longitude of the cropping boundary.
    
    Returns:
        numpy.ndarray: The cropped mosaic array.
        rasterio.transform.Affine: The transformation of the cropped mosaic.
    """
    # Convert lat/lon bounds to pixel coordinates within the GeoTIFF
    row_min, col_min = src.index(lon_min, lat_max)
    row_max, col_max = src.index(lon_max, lat_min)

    # Read the data from the calculated window
    window = ((row_min, row_max + 1), (col_min, col_max + 1))
    mosaic = src.read(band, window=window)

    # Return the cropped mosaic and its affine transformation
    return mosaic, src.window_transform(window)
