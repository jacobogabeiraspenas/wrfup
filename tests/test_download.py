
import pytest

from wrfup.download import lat_lon_to_tile_indices, get_tile_names_in_aoi


@pytest.mark.parametrize(
    "lat, lon",
    [
        (-90.0, -200.0),
        (90.0, 400.0),
        (84.0, 180.0),
        (-60.0, -180.0),
        (0.0, 0.0),
    ],
)
def test_lat_lon_to_tile_indices_within_bounds(lat, lon):
    row, col = lat_lon_to_tile_indices(lat, lon)
    assert 0 <= row < 16
    assert 0 <= col < 16


def test_get_tile_names_in_aoi_frc_and_urb_param():
    lat_min, lat_max = 40.0, 41.0
    lon_min, lon_max = -3.0, -2.0

    names_frc = get_tile_names_in_aoi(lat_min, lat_max, lon_min, lon_max, "FRC_URB2D")
    names_urb = get_tile_names_in_aoi(lat_min, lat_max, lon_min, lon_max, "URB_PARAM")

    assert names_frc, "Expected at least one tile name for FRC_URB2D"
    assert names_urb, "Expected at least one tile name for URB_PARAM"

    assert len(names_frc) == len(names_urb)

    assert all(name.endswith("_urban_fraction_100m_int8") for name in names_frc)
    assert all(name.endswith("_URB_PARAM_100m") for name in names_urb)
