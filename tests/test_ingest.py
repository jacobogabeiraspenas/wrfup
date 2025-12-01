
import numpy as np
import xarray as xr

from wrfup.info import Info
from wrfup.ingest import ingest_fields


def test_ingest_fields_writes_to_disk(tmp_path):
    # Create a dummy geo_em dataset with an FRC_URB2D field
    time = [0]
    south_north = [0, 1]
    west_east = [0, 1]

    data = np.zeros((len(time), len(south_north), len(west_east)), dtype="float32")

    ds = xr.Dataset(
        {
            "FRC_URB2D": (
                ("Time", "south_north", "west_east"),
                data,
            )
        },
        coords={
            "Time": time,
            "south_north": south_north,
            "west_east": west_east,
        },
    )

    geo_em_path = tmp_path / "geo_em.nc"
    ds.to_netcdf(geo_em_path)
    ds.close()

    # Open again for passing into ingest_fields
    ds_open = xr.open_dataset(geo_em_path)

    info = Info(
        geo_em_file=str(geo_em_path),
        field="FRC_URB2D",
        work_dir=str(tmp_path),
        temp_dir=str(tmp_path / "temp"),
    )

    calculated_data = np.ones_like(ds_open["FRC_URB2D"].values)

    ingest_fields(info, calculated_data, ds_open)
    ds_open.close()

    # Reopen the file and check the data was updated
    ds_new = xr.open_dataset(geo_em_path)
    np.testing.assert_array_equal(ds_new["FRC_URB2D"].values, calculated_data)
    ds_new.close()
