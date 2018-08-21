r"""Tests for the Shoot class.

The basic pattern in this file is to construct Shoots in many different
ways, and verify that s.column_name, s.project, and s.extract all behave
as expected.
"""
from pytest import raises
from shootsandleaves.leaf import Leaf
from shootsandleaves.shoot import Shoot


def argspread(f):
    r"""Transform functions with single arg to accept many."""
    return lambda *args: f(args)


data = {
    'first_name':
    'Apple',
    'second_name':
    'Baker',
    'coordinates': {
        'x': 10,
        'y': 20,
    },
    'emails': [
        {
            'address': 'test@example.com',
        },
        {
            'address': 'test1@example.com',
        },
    ],
    'time':
    '2018-01-02 03:45',
    'value':
    1.2,
}


def test_column_name_only():
    r"""Define a shoot with only column_name."""
    tests = {
        'first_name': data['first_name'],
        'coordinates.x': data['coordinates']['x'],
        'missing': None,
    }
    for key, value in tests.items():
        s = Shoot(key)
        assert s.column_name is key
        assert s.project(data) == [value]
        assert s.extract(data) is value


def test_leaves():
    r"""Test one or multiple leaves defined implicitly."""
    s = Shoot('name', leaves='first_name')
    assert s.column_name == 'name'
    assert s.project(data) == ['Apple']
    assert s.extract(data) == 'Apple'

    s = Shoot('name', leaves=['first_name', 'second_name'])
    assert s.column_name == 'name'
    assert s.project(data) == ['Apple', 'Baker']
    assert s.extract(data) == ['Apple', 'Baker']


def test_default():
    r"""Test that the default value is used for missing data."""
    default = 'DEF'
    tests = {
        'first_name': data['first_name'],
        'missing': default,
    }
    for key, value in tests.items():
        s = Shoot(key, default=default)
        assert s.column_name is key
        assert s.project(data) == [value]
        assert s.extract(data) is value

    s = Shoot('mixed_data', ['first_name', 'missing'], default=default)
    assert s.project(data) == [data['first_name'], default]
    assert s.extract(data) == [data['first_name'], default]


def test_single_argument_transform():
    r"""Test explicit transforms with a single argument."""
    s = Shoot('first_name', transform=lambda _: _.upper())
    assert s.project(data) == [data['first_name']]
    assert s.extract(data) == data['first_name'].upper()

    # Without strict=False (tested elsewhere), transform exceptions
    # bubble up.
    s = Shoot('coordinates.x', transform=lambda _: _.upper())
    assert s.project(data) == [10]
    with raises(AttributeError):
        s.extract(data)

    # Transforms are not applied to default values.
    s = Shoot('missing', default=None, transform=lambda _: _.upper())
    assert s.project(data) == [None]
    assert s.extract(data) is None


def test_multiple_argument_transform():
    r"""Test explicit transforms with multiple arguments."""
    s = Shoot('name', leaves=['first_name', 'second_name'], transform=' '.join)
    assert s.project(data) == [data['first_name'], data['second_name']]
    assert s.extract(data) == ' '.join((data['first_name'],
                                        data['second_name']))
    default = 100
    s = Shoot(
        'total',
        leaves=['coordinates.x', 'coordinates.y', 'coordinates.z'],
        default=default,
        transform=sum)
    assert s.project(data) == [
        data['coordinates']['x'], data['coordinates']['y'], default
    ]
    assert s.extract(data) == sum(s.project(data))


def test_non_strict_transform():
    r"""Test that the default is returned when strict is false."""
    s = Shoot(
        'coordinates.x',
        transform=lambda _: _.upper(),
        strict=False,
        default=float('nan'))
    assert s.project(data) == [10]
    assert s.extract(data) is s.default


def test_explicit_leaves():
    r"""Test specifying explicit leaves."""
    s = Shoot('x', explicit_leaves=[Leaf('coordinates.x')])
    assert s.extract(data) is data['coordinates']['x']

    with raises(AssertionError):
        s = Shoot('a', leaves='a', explicit_leaves=[Leaf('a')])

    with raises(AssertionError):
        s = Shoot('a', explicit_leaves=['a'])
