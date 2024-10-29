# download.py in wrfup
import os
import requests
import zipfile
import io
import logging
import rasterio
from tqdm.auto import tqdm
from rasterio.merge import merge

def merge_tiles(tile_paths, output_path):
    """
    Merge multiple tiles into a single mosaic and save as a compressed GeoTIFF.

    Args:
        tile_paths (list): List of file paths for the tiles to be merged.
        output_path (str): Path to save the compressed merged file.
    """
    # Open the raster files
    src_files_to_mosaic = [rasterio.open(tile) for tile in tile_paths]

    # Merge the files into one mosaic
    mosaic, out_trans = merge(src_files_to_mosaic)

    # Define metadata for the output file, based on one of the inputs
    out_meta = src_files_to_mosaic[0].meta.copy()

    # Update the metadata to reflect the mosaic's properties and add compression
    out_meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_trans,
        "compress": "lzw"  # Use LZW compression
    })

    # Close all the source files after merging
    for src in src_files_to_mosaic:
        src.close()

    # Write the compressed merged file to the output path
    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(mosaic)

    logging.info(f"Compressed merged file saved at {output_path}")


def download_tiles(tile_names, save_dir, download_url):
    """
    Download the urban fraction or URB_PARAM tiles for the given tile names.
    
    Args:
        tile_names (list): List of tile names to download.
        save_dir (str): Directory to save the downloaded tiles.
        download_url (str): Base URL for downloading the tiles.
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    tile_paths = []

    # Calculate the total size of all the tiles to be downloaded
    total_size_in_bytes, unknown_size = get_total_download_size(tile_names, download_url)
    total_size_in_mb = total_size_in_bytes / (1024 * 1024)

    # Ask the user for confirmation before downloading
    if unknown_size:
        confirm = input(f"Total download size is at least {total_size_in_mb:.2f} MB, but some sizes are unknown. Do you want to proceed? (y/n): ").lower()
    else:
        confirm = input(f"Total download size is {total_size_in_mb:.2f} MB. Do you want to proceed? (y/n): ").lower()

    if confirm != 'y':
        confirm2 = input(f"Download canceled by the user, would you still like to proceed with the field calculation? (y/n): ").lower()
        if confirm2 != 'y':
            logging.warning("Exiting process.")
            return
        
    
    # Use tqdm to display the progress of the download
    for file_num, tile_name in enumerate(tile_names):
        file_name = f"{tile_name}.zip"
        zip_file_url = f"{download_url}/{file_name}"
        if confirm == 'y':
            download_and_extract_zip(zip_file_url, save_dir, file_num + 1, len(tile_names))
        tile_paths.append(os.path.join(save_dir, f"{tile_name}.tif"))


    # If multiple tiles were downloaded, merge them
    if len(tile_paths) > 1:
        output_path = os.path.join(save_dir, "merged_tiles.tif")
        if confirm == 'y':
            merge_tiles(tile_paths, output_path)
    else:
        logging.info("Only one tile downloaded. No merging required.")
        output_path = tile_paths[0]

    return output_path

def lat_lon_to_tile_indices(lat, lon, grid_rows=16, grid_cols=16):
    """
    Convert latitude and longitude to grid tile index based on zoom level.

    Args:
        lat (float): Latitude in degrees.
        lon (float): Longitude in degrees.
        grid_rows (int): Number of rows in the grid.
        grid_cols (int): Number of columns in the grid.

    Returns:
        (int, int): Row and column index of the tile.
    """
    lat_min = -60
    lat_max = 84
    lat_relative = (lat - lat_max) / (lat_min - lat_max)
    lon_relative = (lon + 180) / 360

    row_index = int(lat_relative * grid_rows)
    col_index = int(lon_relative * grid_cols)

    return min(max(row_index, 0), grid_rows - 1), min(max(col_index, 0), grid_cols - 1)


def get_tile_names_in_aoi_deprecated(lat_min, lat_max, lon_min, lon_max, field):
    """
    Get the list of tile names for the area of interest (AOI) based on latitude and longitude,
    with different naming conventions for FRC_URB2D and URB_PARAM fields.
    
    Args:
        lat_min (float): Minimum latitude of AOI.
        lat_max (float): Maximum latitude of AOI.
        lon_min (float): Minimum longitude of AOI.
        lon_max (float): Maximum longitude of AOI.
        field (str): The field type ('FRC_URB2D' or 'URB_PARAM').

    Returns:
        list: List of tile names.
    """
    tile_names = set()

    for lat in [lat_min, lat_max]:
        for lon in [lon_min, lon_max]:
            row_idx, col_idx = lat_lon_to_tile_indices(lat, lon)

            if field == 'FRC_URB2D':
                tile_name = f"{row_idx:02d}_{col_idx:02d}_zoom4_urban_fraction_100m_int8"
            elif field == 'URB_PARAM':
                tile_name = f"{row_idx:02d}_{col_idx:02d}_zoom4_URB_PARAM_100m"
            else:
                raise ValueError(f"Unknown field type: {field}")
            
            tile_names.add(tile_name)

    return list(tile_names)

def get_tile_names_in_aoi(lat_min, lat_max, lon_min, lon_max, field):
    """
    Get the list of tile names for the area of interest (AOI) based on latitude and longitude,
    with different naming conventions for FRC_URB2D and URB_PARAM fields.

    Args:
        lat_min (float): Minimum latitude of AOI.
        lat_max (float): Maximum latitude of AOI.
        lon_min (float): Minimum longitude of AOI.
        lon_max (float): Maximum longitude of AOI.
        field (str): The field type ('FRC_URB2D' or 'URB_PARAM').

    Returns:
        list: List of tile names covering the entire AOI.
    """
    tile_names = set()

    # Calculate tile indices for each corner
    min_row_idx, min_col_idx = lat_lon_to_tile_indices(lat_max, lon_min)
    max_row_idx, max_col_idx = lat_lon_to_tile_indices(lat_min, lon_max)

    # Generate all tile names within the AOI range
    for row_idx in range(min_row_idx, max_row_idx + 1):
        for col_idx in range(min_col_idx, max_col_idx + 1):
            # Set naming convention based on the field type
            if field == 'FRC_URB2D':
                tile_name = f"{row_idx:02d}_{col_idx:02d}_zoom4_urban_fraction_100m_int8"
            elif field == 'URB_PARAM':
                tile_name = f"{row_idx:02d}_{col_idx:02d}_zoom4_URB_PARAM_100m"
            else:
                raise ValueError(f"Unknown field type: {field}")
            
            tile_names.add(tile_name)

    return list(tile_names)




def download_and_extract_zip(zip_url, extraction_path, file_num, total_files):
    """Download and extract a zip file from a URL with real-time progress tracking."""
    response = requests.get(zip_url, stream=True)
    
    if response.status_code == 200:
        # Get the total file size from the headers
        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kilobyte chunks

        # Create a progress bar using tqdm
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=f"Downloading file {file_num} of {total_files}")

        # Create a buffer to store the downloaded file
        buffer = io.BytesIO()

        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            buffer.write(data)

        progress_bar.close()

        # Once the file is fully downloaded, we can extract it
        buffer.seek(0)  # Reset buffer position to the start
        with zipfile.ZipFile(buffer) as thezip:
            thezip.extractall(extraction_path)
        logging.info(f"File downloaded and extracted: {zip_url}")
    else:
        logging.error(f"Failed to download the file: {zip_url}")

def get_total_download_size(tile_names, download_url):
    """
    Calculate the total size of all tiles to be downloaded.

    Args:
        tile_names (list): List of tile names.
        download_url (str): Base URL to check file size.

    Returns:
        int: Total size in bytes.
    """
    total_size = 0
    unknown_size = False
    for tile_name in tile_names:
        file_name = f"{tile_name}.zip"
        zip_file_url = f"{download_url}/{file_name}"

        # Try a GET request to fetch the content-length header
        try:
            response = requests.get(zip_file_url, stream=True)
            if response.status_code == 200:
                file_size = int(response.headers.get('content-length', 0))
                if file_size > 0:
                    total_size += file_size
                else:
                    logging.warning(f"Could not retrieve size for {zip_file_url}. Marking as unknown size.")
                    unknown_size = True
            else:
                logging.warning(f"Could not retrieve size for {zip_file_url}. Skipping...")
        except requests.RequestException as e:
            logging.error(f"Error fetching file size for {zip_file_url}: {e}")
            unknown_size = True
    
    return total_size, unknown_size

# def download_and_extract_zip(zip_url, extraction_path):
#     """Download and extract a zip file from a URL with real-time progress tracking."""
#     response = requests.get(zip_url, stream=True)
    
#     if response.status_code == 200:
#         total_size_in_bytes = int(response.headers.get('content-length', 0))
#         block_size = 1024  # 1 Kilobyte chunks

#         # Create a progress bar using tqdm
#         progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=f"Downloading {zip_url}")

#         buffer = io.BytesIO()

#         for data in response.iter_content(block_size):
#             progress_bar.update(len(data))
#             buffer.write(data)

#         progress_bar.close()

#         # Extract the downloaded zip file
#         buffer.seek(0)  # Reset buffer position to the start
#         with zipfile.ZipFile(buffer) as thezip:
#             thezip.extractall(extraction_path)
#         logging.info(f"File downloaded and extracted: {zip_url}")
#     else:
#         logging.error(f"Failed to download the file: {zip_url}")

