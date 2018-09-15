r"""TODO.

```
>>> dataframe_from_iterator(data, [S('a'), S('b')], kwargs)
>>> g = Grove([S('a'), S('b')], kwargs); g.from_iterator(data)
```
"""
from pandas import DataFrame, Series
from shootsandleaves.shoot import Shoot


def dataframe_from_iterator(data, shoots, **kwargs):
    r"""Construct and using a Grove."""
    return Grove(shoots, **kwargs).dataframe_from_iterator(data)


class Grove(object):
    r"""TODO."""

    def __init__(self, shoots, index=None, **kwargs):
        r"""TODO."""
        if not all(isinstance(s, Shoot) for s in shoots):
            raise ValueError('shoots must be a list of Shoots')
        self.shoots = shoots
        self.index = index

    def extract(self, obj):
        r"""Return a dict mapping column_names to extracted values."""
        out = {
            shoot.column_name: shoot.extract(obj)
            for shoot in self.shoots if not shoot.expand_dict
        }
        for shoot in self.shoots:
            if shoot.expand_dict:
                value = shoot.extract(obj)
                if isinstance(value, dict):
                    out.update(value)
        return out

    def dataframe_from_iterator(self, data):
        r"""TODO."""
        cols = {s.column_name: [] for s in self.shoots if not s.expand_dict}
        defaults = {
            s.column_name: s.default
            for s in self.shoots if not s.expand_dict
        }
        dtypes = {
            s.column_name: s.dtype
            for s in self.shoots if not s.expand_dict
        }
        for row, obj in enumerate(data):
            for shoot in self.shoots:
                if not shoot.expand_dict:
                    cols[shoot.column_name].append(shoot.extract(obj))
                else:
                    sub_object = shoot.extract(obj)
                    if isinstance(sub_object, dict):
                        for key, value in sub_object.items():
                            if key not in cols:
                                # Initialize
                                cols[key] = [shoot.default] * row
                                defaults[key] = shoot.default
                                dtypes[key] = shoot.dtype
                            cols[key].append(value)
            for col in cols:
                if len(cols[col]) != row + 1:
                    cols[col].append(defaults[col])

        for dt in dtypes:
            cols[dt] = Series(cols[dt], dtype=dtypes[dt])
        df = DataFrame(cols)
        if self.index:
            df.set_index(self.index, inplace=True)
        return df
