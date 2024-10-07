#!/bin/bash

# Input TIFF file
input_tif="../lambda_b_v3_real2d_correct_account_int8_3_bands.tiff"

# Get the dimensions of the input image
width=$(gdalinfo $input_tif | grep "Size is" | awk '{print $3}' | sed 's/,//')
height=$(gdalinfo $input_tif | grep "Size is" | awk '{print $4}')

# Define the number of splits for the final zoom level (16x16 grid)
num_splits=16

# Calculate the width and height of each chunk
chunk_width=$((width / num_splits))
chunk_height=$((height / num_splits))

# Loop to create the tiles for the 16x16 grid
for i in {0..15}; do
    for j in {0..15}; do
        # Calculate offsets
        xoff=$((chunk_width * j))
        yoff=$((chunk_height * i))

        # Output filename
        output_tif=$(printf "%02d_%02d_zoom4_URB_PARAM_100m.tif" $i $j)

        # Use gdal_translate to extract the chunk with LZW compression
        gdal_translate -of GTiff -co "COMPRESS=LZW" -srcwin $xoff $yoff $chunk_width $chunk_height $input_tif $output_tif

        echo "Created $output_tif"
    done
done

