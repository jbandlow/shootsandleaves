r"""A specification for extracting a dataframe column from JSON."""
from copy import deepcopy
from shootsandleaves.leaf import Leaf


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

        assert (leaves is None) or (explicit_leaves is None)
        if explicit_leaves is None:
            if leaves is None:
                leaves = column_name
            if type(leaves) not in (list, tuple):
                leaves = [leaves]
            self.explicit_leaves = [Leaf(_, default) for _ in leaves]
        else:
            assert all(type(leaf) is Leaf for leaf in explicit_leaves)
            self.explicit_leaves = explicit_leaves

        if transform is None:
            transform = lambda arg: arg  # noqa
        # When there is only a single leaf value, the transform function
        # should act on that value, not on a list.
        if len(self.explicit_leaves) == 1:
            self.transform = lambda arg: transform(arg[0])
        else:
            self.transform = transform

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
        return [leaf.get_from(obj) for leaf in self.explicit_leaves]

    def extract(self, obj):
        r"""TODO."""
        projection = self.project(obj)
        # Do not attempt to transform a singleton default value
        if len(projection) == 1 and projection[0] is self.default:
            return self.default

        try:
            return self.transform(projection)
        except Exception:
            if self.strict:
                raise
            return self.default
