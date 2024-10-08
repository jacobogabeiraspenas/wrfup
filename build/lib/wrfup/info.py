# info.py in wrfup
# info.py

class Info:
    """
    Store configuration and paths for processing.
    """
    
    def __init__(self, geo_em_file, field, work_dir, temp_dir):
        self.geo_em_file = geo_em_file
        self.field = field
        self.work_dir = work_dir  # Add this line to store work_dir
        self.temp_dir = temp_dir

    @classmethod
    def from_argparse(cls, args):
        return cls(
            geo_em_file=args.geo_em_file,
            field=args.field,
            work_dir=args.work_dir,  # Add this to capture from argparse
            temp_dir=args.temp_dir,
        )
