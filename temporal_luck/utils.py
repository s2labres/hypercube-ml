import os


def make_file_path(root_dir, start_date, end_date):
    return os.path.join(root_dir, f"{start_date}-{end_date}")
