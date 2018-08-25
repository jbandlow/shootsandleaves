r"""Utility functions for extracting data from dictionaries.

```
>>> lf = Leaf(('a', 'b', 1, slice(1,5)), default='foo')
>>> lf.get_from(obj)
```

```
>>> lf = Leaf('a.b.1.3:5', default='bar')
>>> lf.get_from(obj)
```

```
>>> get(obj, 'dot.notation.selector', default='d')
>>> get(obj, (1, '1', slice(1,3), 'foo'))
```
"""
from collections import Hashable
from copy import deepcopy
from six import string_types

# Sentinel for missing values. This can never coincidentally equal
# external data.
_MISSING_VALUE = object()


def _create_explicit_selector(selector_string):
    r"""Return a selector list from a .-separated selector string."""
    selector = []
    for selector_field in selector_string.split('.'):
        # If there's a :, interpret as a slice.
        if ':' in selector_field:
            # Create arguments to `slice` like so: ':2' --> [None, 2]
            slice_args = [
                int(_) if _ != '' else None for _ in selector_field.split(':')
            ]
            selector.append(slice(*slice_args))
        else:
            try:
                # If it looks like an integer, make it one.
                selector.append(int(selector_field))
            except ValueError:
                # At this point, it can only be a string.
                selector.append(selector_field)
    return selector


def get(obj, selector, default=None):
    r"""Safely extract data from obj.

    Args:
        - obj: A possibly nested object.
        - selector: An iterator or dotted string of fields to
          recursively extract. `slice` objects are ok.
        - default: Value to return if the leaf value cannot be reached.

    For more details, see the documentation for `Leaf`.
    """
    return Leaf(selector, default=default).get_from(obj)


class Leaf(object):
    r"""A specification for extracting data from an object.

    A Leaf is an abstraction for extending `get` semantics to
    deeply-nested JSON-like objects. They are constructed with a
    selector and a default value (which itself defaults to `None`).  An
    example is probably helpful at this point:

    ```python
    >>> leaf = Leaf(('I', 'A', 2), default='missing')
    >>> outline = {'I': {'A': ['eats', 'shoots', 'leaves']}}
    >>> assert leaf.get_from(outline) == 'leaves'
    >>> assert leaf.get_from({}) == 'missing'
    >>> assert leaf.get_from(None) == 'missing'
    ```

    It is often convenient to specify the selector as a '.'-separated
    string. For example,

    ```python
    >>> leaf = Leaf('I.A.2', default='missing')
    ```

    is equivalent to the leaf described above.  For more details on
    this form, see the `__init__` docstring.

    When a field of a selector is a slice, we "step into" the iterable
    it is slicing, and apply the rest of the selector to each of those
    objects. Again, this will be more clear with an example:

    ```python
    >>> data = {'purchases': [{'_id': 1}, {'_id': 2}, {valid: False}]}
    >>> leaf = Leaf('purchases.:._id')
    >>> assert leaf.get_from(data) == [1, 2, None]
    ```
    """

    def __init__(self, selector=None, default=None):
        r"""Construct a Leaf.

        Args:
            - selector: A selector can be passed in one of these forms:
                1. An iterable of objects. Each of these objects must
                be either hashable or an instance of `slice`.

                2. Another Leaf. The selector **and default** from this
                Leaf will be used. Passing in a default parameter will
                raise an error when this form is used.

                3. A string. This will be split on '.'. If any of the
                elements contain ':', they will be parsed as a slice. If
                any of the elements can be parsed as an integer, they
                will be. The remaining elements will remain strings.

                4. None (the default). In this case, `get_from` will
                always return the object it is passed.

            - default: The value that `get_from` will return if the
              leaf field is not present in a given object.

        Internally, selectors are always stored as tuples, regardless of
        what form of the parameter was used.
        """
        self.default = default

        if isinstance(selector, string_types):
            self.selector = _create_explicit_selector(selector)
        elif isinstance(selector, slice):
            self.selector = [selector]
        elif isinstance(selector, Leaf):
            self.selector = deepcopy(selector.selector)
            if default is not None:
                raise ValueError('Setting the default value is not permitted '
                                 'when constructing a Leaf from another Leaf.')
            self.default = selector.default
        elif selector is None:
            self.selector = []
        else:
            self.selector = selector
        assert all(
            isinstance(field, (Hashable, slice)) for field in self.selector)

        self.selector = tuple(self.selector)
        self._internal_selector = [[]]
        index = 0
        for position, field in enumerate(self.selector):
            self._internal_selector[index].append(field)
            if (isinstance(field, slice)
                    and position != len(self.selector) - 1):
                self._internal_selector.append([])
                index += 1

    def __repr__(self):
        r"""Return repr string for self."""
        return f'Leaf({self.selector}, default={self.default})'

    def get_from(self, obj, idx=0):
        r"""Attempt to extract a leaf field from `obj`.

        Args:
            - obj: Any object
            - idx: The index of `self.selector` at which to start
              the extraction.

        Returns:
            - The value at the field of `obj` specified by
              `self.selector`, or `self.default` if this field is not
              accessible.

        """
        # The main loop walks through the fields in `selector`, updating
        # `obj` each time, and bailing if we need to return the default.
        # If the field is a slice, there is special handling, see below.
        while idx < len(self.selector):
            field = self.selector[idx]
            try:
                obj = obj[field]
            except (KeyError, IndexError, TypeError):
                return self.default
            idx += 1
            if isinstance(field, slice):
                # At this point, `field` is a slice, `obj` is an
                # iterable (the valid result of having sliced
                # something), and `idx` points to the next field to
                # select. We recursively select from each of the items
                # in `obj`, and then cast the result to be the same type
                # of iterator as `obj`.
                return type(obj)(self.get_from(item, idx=idx) for item in obj)
        return obj
