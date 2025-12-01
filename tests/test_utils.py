
import os

import numpy as np
import pytest
import xarray as xr

from wrfup.info import Info
from wrfup.utils import (
    first_checks,
    get_lat_lon_extent,
    clean_up,
    check_geo_em_file,
)


def _create_dummy_geo_em(path):
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

    ds.to_netcdf(path)
    return path


def _create_dummy_geo_em_with_field(path, field):
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

    if field == "FRC_URB2D":
        data = np.zeros((len(time), len(south_north), len(west_east)), dtype="float32")
        ds["FRC_URB2D"] = (("Time", "south_north", "west_east"), data)
    elif field == "URB_PARAM":
        urb_param_slices = np.arange(131)
        data = np.zeros(
            (len(time), len(urb_param_slices), len(south_north), len(west_east)),
            dtype="float32",
        )
        ds["URB_PARAM"] = (
            ("Time", "urb_param_slices", "south_north", "west_east"),
            data,
        )
        ds = ds.assign_coords(urb_param_slices=urb_param_slices)

    ds.to_netcdf(path)
    return path


def test_first_checks_success(tmp_path):
    work_dir = tmp_path
    geo_em_name = "geo_em.d01.nc"
    geo_em_path = work_dir / geo_em_name
    _create_dummy_geo_em(geo_em_path)

    info = Info(
        geo_em_file=geo_em_name,
        field="FRC_URB2D",
        work_dir=str(work_dir),
        temp_dir=str(work_dir / "temp"),
    )

    assert first_checks(info) == 0


def test_first_checks_invalid_field(tmp_path):
    work_dir = tmp_path
    geo_em_name = "geo_em.d01.nc"
    geo_em_path = work_dir / geo_em_name
    _create_dummy_geo_em(geo_em_path)

    info = Info(
        geo_em_file=geo_em_name,
        field="INVALID",
        work_dir=str(work_dir),
        temp_dir=str(work_dir / "temp"),
    )

    assert first_checks(info) == 1


def test_get_lat_lon_extent(tmp_path):
    path = tmp_path / "geo_em.nc"
    _create_dummy_geo_em(path)

    lat_min, lat_max, lon_min, lon_max = get_lat_lon_extent(str(path))
    ds = xr.open_dataset(path)

    assert lat_min == pytest.approx(ds["XLAT_M"].min().item())
    assert lat_max == pytest.approx(ds["XLAT_M"].max().item())
    assert lon_min == pytest.approx(ds["XLONG_M"].min().item())
    assert lon_max == pytest.approx(ds["XLONG_M"].max().item())

    ds.close()


def test_clean_up(tmp_path):
    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    (temp_dir / "file.txt").write_text("test", encoding="utf-8")

    assert temp_dir.exists()
    clean_up(str(temp_dir))
    assert not temp_dir.exists()


def test_check_geo_em_file_frc_ok(tmp_path):
    path = tmp_path / "geo_em.nc"
    _create_dummy_geo_em_with_field(path, "FRC_URB2D")

    ds = check_geo_em_file(str(path), "FRC_URB2D")
    assert "FRC_URB2D" in ds
    ds.close()


def test_check_geo_em_file_urb_param_wrong_shape_prompts(monkeypatch, tmp_path):
    # Create a URB_PARAM field with wrong number of slices to trigger the warning and prompt
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

    data = np.zeros((len(time), 10, len(south_north), len(west_east)), dtype="float32")
    ds["URB_PARAM"] = (
        ("Time", "urb_param_slices", "south_north", "west_east"),
        data,
    )
    ds = ds.assign_coords(urb_param_slices=np.arange(10))

    path = tmp_path / "geo_em_wrong.nc"
    ds.to_netcdf(path)
    ds.close()

    # Avoid blocking on input; simulate answering "n" (do not rewrite)
    monkeypatch.setattr("builtins.input", lambda _: "n")

    ds_checked = check_geo_em_file(str(path), "URB_PARAM")
    assert "URB_PARAM" in ds_checked
    ds_checked.close()
