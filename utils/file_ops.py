import os
import errno


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise


def translate_dir(path, from_dir=None, to_dir=None):
    destination_dir = os.path.dirname(path.replace(from_dir, to_dir))
    if not os.path.exists(destination_dir):
        mkdir_p(destination_dir)
    return (path, destination_dir)
