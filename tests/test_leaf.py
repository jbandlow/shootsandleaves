"""Test utility functions."""

from shootsandleaves.leaf import get_field

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
    selector_list = ['II', 'A', '1', 'a']
    assert get_field(dict_blob, selector_list) == 'deep'

    # Dictionary selectors with integer
    selector_list = ['II', 'A', 2]
    assert get_field(dict_blob, selector_list) == 'integer_key'
    field_str = 'II.A.2'
    assert get_field(dict_blob, field_str) == 'integer_key'

    # Integer list selectors only
    selector_list = [1, 2]
    assert get_field(list_blob, selector_list) == 5
    field_str = '1.2'
    assert get_field(list_blob, field_str) == 5

    # List selectors with slice selector
    selector_list = [1, slice(1, None)]
    assert get_field(list_blob, selector_list) == [4, 5]
    field_str = '1.1:'
    assert get_field(list_blob, field_str) == [4, 5]

    # None is returned instead of default
    selector_list = ['I', 'B']
    assert get_field(dict_blob, selector_list, 'default') is None

    # Mixed indices
    selector_list = [slice(2), 0, 'I', 'A', 0, '1', 0, 'a']
    assert get_field(list_blob, selector_list) == 'nested_deep'

    # Deep objects are returned
    selector_list = [0]
    assert get_field(list_blob, selector_list) is dict_blob

    # Empty indexing returns the input
    selector_list = []
    assert get_field(dict_blob, selector_list) is dict_blob
    assert get_field(list_blob, selector_list) is list_blob


def test_get_field_when_field_is_missing():
    """Extraction does not raise exceptions on missing or malformed fields."""
    # Missing key returns default value
    selector_list = ['missing']
    assert get_field(dict_blob, selector_list) is None
    assert get_field(dict_blob, selector_list, 'default') == 'default'

    # Deep missing keys return default value
    selector_list = ['II', 'missing']
    assert get_field(dict_blob, selector_list, 'default') == 'default'

    # Unhashable dict keys returns default value
    selector_list = [slice(1, None)]
    assert get_field(dict_blob, selector_list, 'default') == 'default'

    # Non-integer index into list returns default value
    selector_list = ['string']
    assert get_field(list_blob, selector_list, 'default') == 'default'

    # Out of range index into list returns default value
    selector_list = [100000]
    assert get_field(list_blob, selector_list, 'default') == 'default'

    # Out of range slice into list returns empty list
    selector_list = [slice(10000, None)]
    assert get_field(list_blob, selector_list, 'default') == []

    # Index into empty list returns default value
    selector_list = ['I', 'A', 0, '2', 0]
    assert get_field(dict_blob, selector_list, 'default') == 'default'
