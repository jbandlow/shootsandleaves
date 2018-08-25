"""Test utility functions."""
from pytest import raises

from shootsandleaves.leaf import get, Leaf

dict_blob = {
    'I': {
        'A': [
            {
                '1': [
                    {
                        'a': 'nested_deep',
                    },
                    {
                        'b': 'nested_deep_too',
                    },
                ],
                '2': [],
            },
        ],
        'B':
        None,
    },
    'II': {
        'A': {
            '1': {
                'a': 'deep',
            },
            2: 'integer_key',
        },
    },
    'III': 'shallow',
}

list_blob = [dict_blob, [[1, 2, 3], 4, 5]]


def test_get_field_when_field_exists():
    """Extract fields that are present."""
    # Dictionary selectors only
    selector = ['II', 'A', '1', 'a']
    assert get(dict_blob, selector) == 'deep'

    # Dictionary selectors with integer
    selector = ['II', 'A', 2]
    assert get(dict_blob, selector) == 'integer_key'
    selector = 'II.A.2'
    assert get(dict_blob, selector) == 'integer_key'

    # Integer list selectors only
    selector = [1, 2]
    assert get(list_blob, selector) == 5
    selector = '1.2'
    assert get(list_blob, selector) == 5

    # None is returned instead of default
    selector = ['I', 'B']
    assert get(dict_blob, selector, 'default') is None

    # Deep objects are returned
    selector = [0]
    assert get(list_blob, selector) is dict_blob

    # Empty indexing returns the input
    selector = []
    assert get(dict_blob, selector) is dict_blob
    assert get(list_blob, selector) is list_blob

    selector = None
    assert get(dict_blob, selector) is dict_blob
    assert get(list_blob, selector) is list_blob


def test_slice_indices():
    """Test extraction when one or more field selectors is a slice."""
    # Slice and stop.
    selector = [1, slice(1, None)]
    assert get(list_blob, selector) == [4, 5]
    selector = '1.1:'
    assert get(list_blob, selector) == [4, 5]

    # Slice and continue.
    selector = [slice(2), 'I', 'A', 0, '1', 0, 'a']
    assert get(list_blob, selector) == ['nested_deep', None]

    # Multiple slices.
    selector = [slice(2), 'I', 'A', slice(None), '1', 0, 'a']
    assert get(list_blob, selector) == [['nested_deep'], None]

    # Single slice
    selector = slice(1, None)
    assert get(list_blob, selector) == [list_blob[1]]


def test_get_field_when_field_is_missing():
    """Extraction does not raise exceptions on missing or malformed fields."""
    # Missing key returns default value
    selector = ['missing']
    assert get(dict_blob, selector) is None
    assert get(dict_blob, selector, 'default') == 'default'

    # Deep missing keys return default value
    selector = ['II', 'missing']
    assert get(dict_blob, selector, 'default') == 'default'

    # Unhashable dict keys returns default value
    selector = [slice(1, None)]
    assert get(dict_blob, selector, 'default') == 'default'

    # Non-integer index into list returns default value
    selector = ['string']
    assert get(list_blob, selector, 'default') == 'default'

    # Out of range index into list returns default value
    selector = [100000]
    assert get(list_blob, selector, 'default') == 'default'

    # Out of range slice into list returns empty list
    selector = [slice(10000, None)]
    assert get(list_blob, selector, 'default') == []

    # Index into empty list returns default value
    selector = ['I', 'A', 0, '2', 0]
    assert get(dict_blob, selector, 'default') == 'default'

    # Iteration into default value does not occur
    selector = ['a', 'b']
    default = {'b': 'c'}
    # These are NOT the semantics we want:
    assert {}.get('a', default).get('b', default) == 'c'
    # We want this instead:
    assert get({}, selector, default=default) is default


def test_repr():
    r"""Test that repr returns a useful string version of Leaf."""
    lf = Leaf('a.-1.2:3.x', default=0)
    assert repr(lf) == "Leaf(('a', -1, slice(2, 3, None), 'x'), default=0)"


def test_copy_construction():
    r"""Test the construction of a Leaf from another Leaf."""
    leaf1 = Leaf('a.x', default=0)
    leaf2 = Leaf(leaf1)
    assert leaf1.selector == leaf2.selector
    assert leaf1.default == leaf2.default
    assert repr(leaf1) == repr(leaf2)

    with raises(ValueError):
        Leaf(leaf1, default=1)
