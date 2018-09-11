r"""A specification for extracting a dataframe column from JSON."""
import uuid
from shootsandleaves.leaf import Leaf


class Shoot():
    r"""TODO. This is a test."""

    def __init__(self,
                 column_name=None,
                 leaves=None,
                 transform=None,
                 default=None,
                 explicit_leaves=None,
                 dtype=None,
                 expand_dict=False):
        r"""TODO."""
        if column_name is None:
            expand_dict = True
            self.column_name = str(uuid.uuid4())
        else:
            self.column_name = column_name

        assert (leaves is None) or (explicit_leaves is None)
        if explicit_leaves is None:
            if leaves is None:
                leaves = self.column_name
            if not isinstance(leaves, (list, tuple)):
                leaves = [leaves]
            self.explicit_leaves = [Leaf(_, default) for _ in leaves]
        else:
            assert all(isinstance(leaf, Leaf) for leaf in explicit_leaves)
            self.explicit_leaves = explicit_leaves

        if transform is None:
            transform = lambda arg: arg  # noqa
        # When there is only a single leaf value, the transform function
        # should act on that value, not on a list.
        if len(self.explicit_leaves) == 1:
            self.transform = lambda arg: transform(arg[0])
        else:
            self.transform = transform

        self.default = default
        self.dtype = dtype
        self.expand_dict = expand_dict

    def project(self, obj):
        r"""TODO."""
        return [leaf.get_from(obj) for leaf in self.explicit_leaves]

    def extract(self, obj):
        r"""TODO."""
        projection = self.project(obj)
        # Do not attempt to transform a singleton default value
        if len(projection) == 1 and projection[0] is self.default:
            return self.default

        return self.transform(projection)
