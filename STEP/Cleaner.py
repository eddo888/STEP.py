#!/usr/bin/env python3

from collections import OrderedDict
from suds.sudsobject import asdict, Factory as SudsFactory

def suds2dict(d):
    """
    Suds object serializer
    Borrowed from https://stackoverflow.com/questions/2412486/serializing-a-suds-object-in-python/15678861#15678861
    """
    if type(d) in [dict, OrderedDict]: return d

    out = {'__class__': d.__class__.__name__}
    for k, v in asdict(d).items():
        if hasattr(v, '__keylist__'):
            out[k] = suds2dict(v)
        elif isinstance(v, list):
            out[k] = []
            for item in list(v):
                if hasattr(item, '__keylist__'):
                    out[k].append(suds2dict(item))
                else:
                    out[k].append(item)
        else:
            out[k] = v
    return out


def dict2suds(d):
    """
    Suds object deserializer
    """
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out[k] = dict2suds(v)
        elif isinstance(v, list):
            out[k] = []
            for item in list(v):
                if isinstance(item, dict):
                    out[k].append(dict2suds(item))
                else:
                    out[k].append(item)
        else:
            out[k] = v
    return SudsFactory.object(out.pop('__class__'), out)

