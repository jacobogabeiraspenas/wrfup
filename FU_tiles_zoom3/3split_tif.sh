#!/bin/bash

# Input TIFF file
input_tif="../urban_fraction_100m.tif"

# Get the dimensions of the input image
width=$(gdalinfo $input_tif | grep "Size is" | awk '{print $3}' | sed 's/,//')
height=$(gdalinfo $input_tif | grep "Size is" | awk '{print $4}')

# Define the number of splits along each dimension (8x8 for 64 parts)
num_splits=8

# Calculate the width and height of each chunk
chunk_width=$((width / num_splits))
chunk_height=$((height / num_splits))

# Loop to create the 64 tiles
for i in {0..7}; do
    for j in {0..7}; do
        # Calculate offsets
        xoff=$((chunk_width * j))
        yoff=$((chunk_height * i))

        # Output filename with zoom level
        output_tif=$(printf "02_%02d_%02d_zoom3_urban_fraction_100m.tif" $i $j)

        # Use gdal_translate to extract the chunk with LZW compression
        gdal_translate -of GTiff -co "COMPRESS=LZW" -srcwin $xoff $yoff $chunk_width $chunk_height $input_tif $output_tif

        echo "Created $output_tif"
    done
done

