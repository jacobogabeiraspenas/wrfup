
import types

from wrfup.info import Info


def test_info_from_argparse():
    args = types.SimpleNamespace(
        geo_em_file="geo_em.d01.nc",
        field="FRC_URB2D",
        work_dir="/tmp/work",
        temp_dir="/tmp/work/temp",
    )
    info = Info.from_argparse(args)

    assert info.geo_em_file == args.geo_em_file
    assert info.field == args.field
    assert info.work_dir == args.work_dir
    assert info.temp_dir == args.temp_dir
