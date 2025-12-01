
import numpy as np
import pytest
import xarray as xr
import rasterio
from rasterio.transform import from_origin

from wrfup.calculation import (
    add_urb_param_fields_if_not_exists,
    add_frc_urb2d_field_if_not_exists,
    crop_opened_tiff_by_lat_lon_bounds_and_return_mosaic,
)


def _create_base_dataset():
    south_north = [0, 1]
    west_east = [0, 1]
    time = [0]

    ds = xr.Dataset(
        {
            "XLAT_M": (
                ("south_north", "west_east"),
                np.array([[45.0, 45.1], [45.2, 45.3]], dtype="float32"),
            ),
            "XLONG_M": (
                ("south_north", "west_east"),
                np.array([[5.0, 5.1], [5.2, 5.3]], dtype="float32"),
            ),
        },
        coords={
            "south_north": south_north,
            "west_east": west_east,
            "Time": time,
        },
    )
    return ds


def test_add_urb_param_fields_if_not_exists_creates_field():
    ds = _create_base_dataset()
    assert "URB_PARAM" not in ds

    ds_out = add_urb_param_fields_if_not_exists(ds)

    assert "URB_PARAM" in ds_out
    assert ds_out["URB_PARAM"].dtype == np.float32
    assert ds_out["URB_PARAM"].shape[0] == ds.dims["Time"]
    assert ds_out["URB_PARAM"].shape[2] == ds.dims["south_north"]
    assert ds_out["URB_PARAM"].shape[3] == ds.dims["west_east"]


def test_add_urb_param_fields_if_not_exists_preserves_existing():
    ds = _create_base_dataset()
    data = np.ones((1, 132, 2, 2), dtype="float32")
    ds["URB_PARAM"] = (
        ("Time", "urb_param_slices", "south_north", "west_east"),
        data,
    )

    ds_out = add_urb_param_fields_if_not_exists(ds)
    np.testing.assert_array_equal(ds_out["URB_PARAM"].values, data)


def test_add_frc_urb2d_field_if_not_exists_creates_field():
    ds = _create_base_dataset()
    assert "FRC_URB2D" not in ds

    ds_out = add_frc_urb2d_field_if_not_exists(ds, "FRC_URB2D")

    assert "FRC_URB2D" in ds_out
    assert ds_out["FRC_URB2D"].dtype == np.float32
    assert ds_out["FRC_URB2D"].shape == (
        ds.dims["Time"],
        ds.dims["south_north"],
        ds.dims["west_east"],
    )
    assert ds_out.attrs.get("FLAG_FRC_URB2D") == 1


def test_crop_opened_tiff_by_lat_lon_bounds_and_return_mosaic(tmp_path):
    data = np.arange(12, dtype="uint8").reshape(3, 4)
    transform = from_origin(0.0, 3.0, 1.0, 1.0)

    tif_path = tmp_path / "test.tif"
    with rasterio.open(
        tif_path,
        "w",
        driver="GTiff",
        height=data.shape[0],
        width=data.shape[1],
        count=1,
        dtype=data.dtype,
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(data, 1)

    with rasterio.open(tif_path) as src:
        mosaic, _ = crop_opened_tiff_by_lat_lon_bounds_and_return_mosaic(
            src,
            band=1,
            lat_min=0.0,
            lat_max=3.0,
            lon_min=0.0,
            lon_max=4.0,
        )

    assert mosaic.shape == data.shape
    np.testing.assert_array_equal(mosaic, data)
