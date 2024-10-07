import rasterio
import numpy as np
import xarray as xr
from tqdm.auto import tqdm
from rasterio.windows import from_bounds


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
