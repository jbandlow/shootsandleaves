r"""A specification for extracting a dataframe column from JSON.

I am losing semantic clarity here. What is the precise definition of a
leaf, and should it be a class by itself?
There can be a top-level shortcut which constructs the Leaf:
```
def get_field(obj, leaf_constructor, default):
    return Leaf(leaf_constructor, default).extract_from(object)
```
"""
from copy import deepcopy
from shootsandleaves.leaf import Leaf


def _default_transform(args):
    r"""Return a single argument by itself, o/w a tuple."""
    if len(args) == 1:
        return args[0]
    return args


class Shoot():
    r"""TODO."""

    def __init__(self,
                 column_name,
                 leaves=None,
                 transform=None,
                 default=None,
                 explicit_leaves=None,
                 strict=True,
                 dtype=None,
                 **kwargs):
        r"""TODO."""
        self.column_name = column_name

        if explicit_leaves is None:
            if leaves is None:
                leaves = column_name
            if type(leaves) not in (list, tuple):
                leaves = [leaves]
            self.explicit_leaves = [Leaf(_, default) for _ in leaves]
        else:
            self.explicit_leaves = explicit_leaves

        self.transform = transform or _default_transform
        self.strict = strict
        self.default = default
        self.dtype = dtype

    def copy(self):
        r"""Return a copy of self."""
        # TODO: Do this properly
        return Shoot(
            self.column_name,
            transform=self.transform,
            default=deepcopy(self.default),
            explicit_leaves=deepcopy(self.explicit_leaves))

    def rename(self, name):
        r"""Return a copy of self with new name."""
        # TODO: Do this properly
        rv = self.copy()
        rv.column_name = name
        return rv

    def project(self, obj):
        r"""TODO."""
        return [leaf.extract_from(obj) for leaf in self.explicit_leaves]

    def extract(self, obj):
        r"""TODO."""
        try:
            return self.transform(self.project(obj))
        except Exception:
            if self.strict:
                raise
            return self.default
