r"""Utility functions for extracting data from dictionaries.

```
>>> lf = Leaf(['a', 'b', 1, slice(1,5)], default='foo')
>>> lf.extract_from(obj)
```

```
>>> lf = Leaf('a.b.1.3:5', default='bar')
>>> lf.extract_from(obj)
```

```
>>> get_field(obj, 'dot.notation.selector', default='d')
>>> get_field(obj, (1, '1', slice(1,3), 'foo'))
```
"""
from six import string_types

# We use `nan` for a missing value to avoid coincidental matching.
# In other words, we want the following behavior:
# {'a': float('nan')}.get('b', MISSING_VALUE) is MISSING_VALUE
# {'a': float('nan')}.get('a', MISSING_VALUE) is not MISSING_VALUE
MISSING_VALUE = float('nan')


def get_field(obj, selector, default=None):
    r"""Safely extract data from obj.

    Args:
        - obj: A possibly nested object.
        - selector: A list or dotted string of fields to recursively
          extract. slice objects are ok.
        - default: Value to return if the leaf value cannot be reached.

    If the leaf value is None, None will be returned (instead of
    whatever `default` happens to be).
    """
    lf = Leaf(selector, default=default)
    return lf.extract_from(obj)


class Leaf(object):
    r"""A specification for extracting data from an object."""

    def _extract_explicit_selector_list(self, selector_string):
        r"""TODO."""
        selector_list = []
        for selector in selector_string.split('.'):
            # If there's a :, interpret as a slice.
            if ':' in selector:
                slice_args = [
                    int(_) if _ != '' else None
                    for _ in selector.split(':')
                ]
                selector_list.append(slice(*slice_args))
            else:
                try:
                    # If it looks like an integer, make it one.
                    selector_list.append(int(selector))
                except ValueError:
                    # At this point, it can only be a string.
                    selector_list.append(selector)
        return selector_list

    def __init__(self, selector_list, default=None):
        r"""TODO."""
        if isinstance(selector_list, string_types):
            self.selector_list = self._extract_explicit_selector_list(
                selector_list)
        elif isinstance(selector_list, Leaf):
            # TODO: Implement a proper copy constructor
            other = selector_list
            self.selector_list = other.selector_list
            self.default = other.default
        else:
            self.selector_list = selector_list
        if '' in self.selector_list:
            raise ValueError('Empty selectors are invalid. '
                             f'Selector list: {self.selector_list}')

        self.default = default

    def extract_from(self, obj):
        r"""TODO."""
        if self.selector_list is None:
            return obj
        for selector in self.selector_list:
            if hasattr(obj, 'get'):
                try:
                    obj = obj.get(selector, MISSING_VALUE)
                    if obj is MISSING_VALUE:
                        return self.default
                except TypeError:
                    return self.default
            elif hasattr(obj, '__getitem__'):
                try:
                    obj = obj[selector]
                except (TypeError, IndexError):
                    return self.default
            else:
                return self.default
        return obj
