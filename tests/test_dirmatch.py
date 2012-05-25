from unittest import TestCase
import clonevirtualenv

class TestVirtualenvDirmatch(TestCase):

    def test_dirmatch(self):
        assert clonevirtualenv._dirmatch('/home/foo/bar', '/home/foo/bar')
        assert clonevirtualenv._dirmatch('/home/foo/bar/', '/home/foo/bar')
        assert clonevirtualenv._dirmatch('/home/foo/bar/etc', '/home/foo/bar')
        assert clonevirtualenv._dirmatch('/home/foo/bar/etc/', '/home/foo/bar')
        assert not clonevirtualenv._dirmatch('/home/foo/bar2', '/home/foo/bar')
        assert not clonevirtualenv._dirmatch('/home/foo/bar2/etc', '/home/foo/bar')
        assert not clonevirtualenv._dirmatch('/home/foo/bar/', '/home/foo/bar/etc')
        assert not clonevirtualenv._dirmatch('/home/foo/bar', '/home/foo/bar/etc')
