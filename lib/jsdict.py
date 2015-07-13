# coding:utf-8


class JsDict(dict):
    def __getitem__(self, item):
        if not item in self: return None
        else: return dict.__getitem__(self, item)

    def __repr__(self):
        return '<jsDict ' + dict.__repr__(self) + '>'

    __getattr__ = __getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
