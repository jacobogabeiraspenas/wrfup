import rasterio
from rasterio.enums import Resampling

input_file = 'urban_fraction_100m.tif'
output_file = 'urban_fraction_100m_modified.tif'

print(f"Opening input file: {input_file}")
with rasterio.open(input_file) as src:
    print("Reading data...")
    data = src.read(out_dtype='float32', resampling=Resampling.bilinear)
    print("Data read successfully.")

    print("Scaling data by 100...")
    scaled_data = (data * 100).astype('int16')
    print("Data scaling complete.")

    profile = src.profile
    # Update the profile to reflect the changes: data type and compression
    profile.update(dtype=rasterio.int16, compress='lzw')

    print(f"Writing output file: {output_file}")
    with rasterio.open(output_file, 'w', **profile) as dst:
        dst.write(scaled_data)
    print("Output file written successfully.")

print("Process completed.")

