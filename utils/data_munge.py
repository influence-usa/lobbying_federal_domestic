

def get_key(my_dict, key):
    return reduce(dict.get, key.split("."), my_dict)


def set_key(my_dict, key, value):
    keys = key.split(".")
    my_dict = reduce(dict.get, keys[:-1], my_dict)
    my_dict[keys[-1]] = value


def del_key(my_dict, key):
    keys = key.split(".")
    my_dict = reduce(dict.get, keys[:-1], my_dict)
    del my_dict[keys[-1]]


def map_vals(copy_map, original, template={}):
    _original = original.copy()
    _transformed = template
    for orig_loc, trans_loc in copy_map:
        val = get_key(_original, orig_loc)
        set_key(_transformed, trans_loc, val)
    return _transformed
