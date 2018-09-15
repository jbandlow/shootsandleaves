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
                 expand_dict=None):
        r"""TODO."""
        # Handle column_name x expand_dict incompatibility.
        if column_name is None:
            if expand_dict is False:
                raise ValueError('Cannot set `expand_dict=False` w/o a'
                                 'column name.')
            expand_dict = True

        # Set self.column_name
        self.column_name = column_name or str(uuid.uuid4())

        ################
        # Set self.explicit_leaves from the combination of `leaves` and
        # `explicit_leaves`. See below.

        # Case 1: Both `leaves` and `explicit_leaves` are specified.
        # This is an error.
        assert (leaves is None) or (explicit_leaves is None)

        # Case 2: Neither are specified. If `expand_dict`, we just use
        # an empty Leaf. Otherwise, we use a Leaf defined by the column
        # name.
        if leaves is None and explicit_leaves is None:
            if expand_dict:
                self.explicit_leaves = [Leaf((), default)]
            else:
                self.explicit_leaves = [Leaf(self.column_name, default)]

        # Case 3: Only `leaves` is specified. We have to make sure these
        # get placed into a list.
        elif explicit_leaves is None:
            if not isinstance(leaves, (list, tuple)):
                leaves = [leaves]
            self.explicit_leaves = [Leaf(_, default) for _ in leaves]

        # Case 4: Only `explicit_leaves` is specified. Sanity check it.
        else:
            assert all(isinstance(leaf, Leaf) for leaf in explicit_leaves)
            self.explicit_leaves = explicit_leaves
        ###################

        # Set self.transform.  When there is only a single leaf value,
        # the transform function should act on that value, not on a
        # list. The default function is the identity function.
        if transform is None:
            transform = lambda arg: arg  # noqa
        if len(self.explicit_leaves) == 1:
            self.transform = lambda arg: transform(arg[0])
        else:
            self.transform = transform

        # Store the remaining props.
        self.expand_dict = bool(expand_dict)
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
