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
        return {s.column_name: s.extract(obj) for s in self.shoots}

    def dataframe_from_iterator(self, data):
        r"""TODO."""
        cols = {s.column_name: [] for s in self.shoots}
        for obj in data:
            for s in self.shoots:
                cols[s.column_name].append(s.extract(obj))
        cols = {
            s.column_name: Series(cols[s.column_name], dtype=s.dtype)
            for s in self.shoots
        }
        df = DataFrame(cols)
        if self.index:
            df.set_index(self.index, inplace=True)
        return df
