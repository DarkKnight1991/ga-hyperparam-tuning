import numpy as np


def get_key_in_nested_dict(nested_dict, target_key):
    for key in nested_dict:
        if key == target_key:
            return nested_dict[key]
        elif type(nested_dict[key]) is dict:
            return get_key_in_nested_dict(nested_dict[key], target_key)
        elif type(nested_dict[key]) is list:
            if type(nested_dict[key][0]) is dict:
                for item in nested_dict[key]:
                    res = get_key_in_nested_dict(item, target_key)
                    if res:
                        return res


def choose_from_search_space(search_space_mlp: dict, key="params", params={}):
    if type(search_space_mlp) is dict:
        keys = search_space_mlp.keys()
        for key in keys:
            choose_from_search_space(search_space_mlp[key], key, params)
    elif type(search_space_mlp) is list:  # or type(search_space_mlp) is tuple:
        choose_from_search_space(search_space_mlp[np.random.randint(0, len(search_space_mlp))], key, params)
    else:
        params[key] = search_space_mlp
    return params


def filter_list_by_prefix(_list, prefix, negation: bool):
    if negation:
        return [item for item in _list if not item.startswith(prefix)]
    else:
        return [item for item in _list if item.startswith(prefix)]


def log(*args):
    print(" ".join(args))