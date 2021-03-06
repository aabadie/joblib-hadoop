"""Test the hdfs backend."""

from __future__ import print_function

import os
import os.path
import array
import numpy as np

from pytest import mark

from joblib import Memory
from joblibhadoop.hdfs import register_hdfs_store_backend

__namenode__ = os.environ['NAMENODE']


@mark.parametrize("compress", [True, False])
@mark.parametrize("arg", ["test",
                          b"test",
                          (1, 2, 3),
                          {"1": 1, "2": 2},
                          [1, 2, 3, 4],
                          array.array('d', [1, 2, 3]),
                          np.arange(10)])
def test_store_and_retrieve(capsys, tmpdir, compress, arg):
    """Test that any types can be cached in hdfs store."""
    def func(arg):
        """Dummy function."""
        print("executing function")
        return arg

    register_hdfs_store_backend()

    mem = Memory(location=tmpdir.strpath[1:], host=__namenode__,
                 backend='hdfs', user='test', verbose=0, compress=compress)

    assert mem.store.cachedir == os.path.join(tmpdir.strpath[1:], "joblib")

    func = mem.cache(func)

    # First call executes and persists result
    result = func(arg)

    if isinstance(arg, np.ndarray):
        np.testing.assert_array_equal(arg, result)
    else:
        assert result == arg

    out, err = capsys.readouterr()
    assert out == "executing function\n"
    assert not err

    # Second call returns the cached result
    result = func(arg)
    if isinstance(arg, np.ndarray):
        np.testing.assert_array_equal(arg, result)
    else:
        assert result == arg

    out, err = capsys.readouterr()
    assert not out
    assert not err


def test_root_location_replacement(tmpdir):
    """Test that root location is correctly replaced."""
    location = tmpdir.strpath

    register_hdfs_store_backend()

    mem = Memory(location=location, host=__namenode__,
                 backend='hdfs', user='test', verbose=100)

    assert mem.store.cachedir == os.path.join(tmpdir.strpath[1:], "joblib")


def test_passing_backend_base_to_memory(tmpdir):
    """Test passing a store as location in memory is correctly handled."""

    register_hdfs_store_backend()

    mem = Memory(location=tmpdir.strpath, host=__namenode__,
                 backend='hdfs', user='test', verbose=100)

    assert mem.store.cachedir == os.path.join(tmpdir.strpath[1:], "joblib")

    mem2 = Memory(location=mem.store, host=__namenode__,
                  backend='hdfs', user='test', verbose=100)

    assert mem2.store.cachedir == mem.store.cachedir


def test_clear_cache(tmpdir):
    """Test clearing cache."""
    def func(arg):
        """Dummy function."""
        print("executing function")
        return arg

    register_hdfs_store_backend()

    mem = Memory(location=tmpdir.strpath, host=__namenode__,
                 backend='hdfs', user='test', verbose=100, compress=False)
    cached_func = mem.cache(func)
    cached_func("test")

    mem.clear()

    assert not mem.store.object_exists(mem.store.cachedir)


def test_get_cache_items(tmpdir):
    """Test cache items listing."""
    def func(arg):
        """Dummy function."""
        return arg

    register_hdfs_store_backend()

    mem = Memory(location=tmpdir.strpath, host=__namenode__,
                 backend='hdfs', user='test', verbose=100, compress=False)
    assert not mem.store.get_cache_items()

    cached_func = mem.cache(func)
    for arg in ["test1", "test2", "test3"]:
        cached_func(arg)

    # get_cache_items always returns an empty list for the moment
    assert len(mem.store.get_cache_items()) == 3

    mem.clear()
    assert not mem.store.get_cache_items()
