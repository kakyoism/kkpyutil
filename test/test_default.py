"""
tests that don't need external data
"""
import getpass
import platform
import sys
import os
import os.path as osp
# 3rd party
import types

import pytest
# project
_script_dir = osp.abspath(osp.dirname(__file__))
sys.path.insert(0, repo_root := osp.abspath(f'{_script_dir}/..'))
import kkpyutil as util


def test_get_platform_home_dir():
    plat = platform.system()
    if plat == 'Windows':
        expected = osp.abspath(f'C:\\Users\\{getpass.getuser()}')
        assert util.get_platform_home_dir() == expected
    elif plat == 'Darwin':
        expected = osp.abspath(f'/Users/{getpass.getuser()}')
        assert util.get_platform_home_dir() == expected
    elif plat == 'Linux':
        expected = osp.abspath(f'/home/{getpass.getuser()}')
        assert util.get_platform_home_dir() == expected
    else:
        with pytest.raises(NotImplementedError):
            util.get_platform_home_dir()


def test_get_platform_appdata_dir():
    plat = platform.system()
    if plat == 'Windows':
        expected = osp.abspath(f'C:\\Users\\{getpass.getuser()}\\AppData\\Roaming')
        assert util.get_platform_appdata_dir() == expected
        expected = osp.abspath(f'C:\\Users\\{getpass.getuser()}\\AppData\\Local')
        assert util.get_platform_appdata_dir(winroam=False) == expected
    elif plat == 'Darwin':
        expected = osp.abspath(f'/Users/{getpass.getuser()}/Library/Application Support')
        assert util.get_platform_appdata_dir() == expected
    else:
        with pytest.raises(NotImplementedError):
            util.get_platform_appdata_dir()


def test_get_platform_tmp_dir():
    plat = platform.system()
    if plat == 'Windows':
        expected = osp.abspath(f'C:\\Users\\{getpass.getuser()}\\AppData\\Local\\Temp')
        assert util.get_platform_tmp_dir() == expected
    elif plat == 'Darwin':
        expected = osp.abspath(f'/Users/{getpass.getuser()}/Library/Caches')
        assert util.get_platform_tmp_dir() == expected
    elif plat == 'Linux':
        expected = '/tmp'
        assert util.get_platform_tmp_dir() == expected
    else:
        with pytest.raises(NotImplementedError):
            util.get_platform_tmp_dir()


def test_format_error_message():
    got = util.format_error_message(
        situation='task result is wrong',
        expected=100,
        got=-100,
        advice='did you forget to take its absolute value?',
        reaction='aborted',
    )
    expected = """\
task result is wrong:
- Expected: 100
- Got: -100
- Advice: did you forget to take its absolute value?
- Reaction: aborted"""
    assert got == expected


def test_is_multiline_text():
    text = 'single line'
    assert not util.is_multiline_text(text)
    text = """line 1
line 2
line 3"""
    assert util.is_multiline_text(text)


def test_get_md5_checksum():
    missing_file = 'missing'
    assert util.get_md5_checksum(missing_file) is None
    valid_file = osp.abspath(f'{_script_dir}/../LICENSE')
    # line-ends count
    assert util.get_md5_checksum(valid_file) == '5d326be91ee12591b87f17b6f4000efe' if platform.system() == 'Windows' else '7a3beb0af03d4afff89f8a69c70a87c0'


def test_substitute_keywords():
    str_map = {
        'var': 'foo',
    }
    text = """
变量 : %(var)s
Escape : %%
Variable in text: %(var)siable
"""
    assert util.substitute_keywords(text, str_map) == """
变量 : foo
Escape : %
Variable in text: fooiable
"""
    str_map = {
        'var': 'foo',
        '%%': '$$'
    }
    text = """
变量 : %(var)s
Escape : %%
Variable in text: %(var)siable
"""
    assert util.substitute_keywords(text, str_map, useliteral=True) == """
变量 : %(foo)s
Escape : $$
Variable in text: %(foo)siable
"""


def test_is_uuid():
    valid = 'c9bf9e57-1685-4c89-bafb-ff5af830be8a'
    assert util.is_uuid(valid)
    invalid = 'c9bf9e58'
    assert not util.is_uuid(invalid)


def test_convert_to_wine_path():
    path = '/path/to/my/file'
    assert util.convert_to_wine_path(path) == 'Z:\\path\\to\\my\\file'
    drive = 'X:'
    assert util.convert_to_wine_path(path, drive) == 'X:\\path\\to\\my\\file'
    path = '~/my/file'
    assert util.convert_to_wine_path(path) == 'Y:\\my\\file'
    drive = 'H:'
    assert util.convert_to_wine_path(path, drive) == 'H:\\my\\file'


def test_convert_from_wine_path():
    path = ' Z:\\path\\to\\my\\file   '
    assert util.convert_from_wine_path(path) == '/path/to/my/file'
    path = 'Y:\\my\\file'
    assert util.convert_from_wine_path(path) == '~/my/file' if platform.system() == 'Windows' else f'{os.environ.get("HOME")}/my/file'
    path = 'X:\\my\\file'
    assert util.convert_from_wine_path(path) == path


def test_find_first_line_in_range():
    lines = """
keyword: other stuff
...... ...... ...... ...... ......
...... ...... ...... ...... ......
""".split('\n')
    assert util.find_first_line_in_range(lines, 'keyword') == 1
    lines = """
other stuff: keyword
...... ...... ...... ...... ......
...... ...... ...... ...... ......
""".split('\n')
    assert util.find_first_line_in_range(lines, 'keyword', algo='endswith') == 1
    lines = """
other stuff: keyword: other stuff
...... ...... ...... ...... ......
...... ...... ...... ...... ......
""".split('\n')
    assert util.find_first_line_in_range(lines, 'keyword', algo='contains') == 1
    lines = """
...... ...... ...... ...... ......
...... ...... ...... ...... ......
keyword: other stuff
...... ...... ...... ...... ......
...... ...... ...... ...... ......
""".split('\n')
    assert util.find_first_line_in_range(lines, 'keyword', linerange=(3,)) == 3
    lines = """0
1...... ...... ...... ...... ......
2...... ...... ...... ...... ......
keyword: other stuff
4...... ...... ...... ...... ......
5...... ...... ...... ...... ......
6...... ...... ...... ...... ......
keyword: other stuff
...... ...... ...... ...... ......
...... ...... ...... ...... ......
""".split('\n')
    assert util.find_first_line_in_range(lines, 'keyword', linerange=(4,)) == 7

    lines = """
...... ...... ...... ...... ......
...... ...... ...... ...... ......
""".split('\n')
    assert util.find_first_line_in_range(lines, 'keyword') is None
    lines = """0
1...... ...... ...... ...... ......
2...... ...... ...... ...... ......
keyword: other stuff
4...... ...... ...... ...... ......
5...... ...... ...... ...... ......
6...... ...... ...... ...... ......
keyword: other stuff
8...... ...... ...... ...... ......
9...... ...... ...... ...... ......
""".split('\n')
    assert util.find_first_line_in_range(lines, 'keyword', linerange=(8,)) is None

    lines = """0
keyword: other stuff
2...... ...... ...... ...... ......
3...... ...... ...... ...... ......
""".split('\n')
    with pytest.raises(AssertionError):
        util.find_first_line_in_range(lines, 'keyword', linerange=(2, 0))

    lines = """
keyword: other stuff
...... ...... ...... ...... ......
...... ...... ...... ...... ......
"""
    with pytest.raises(TypeError):
        util.find_first_line_in_range(lines, 'keyword')


def test_flatten_nested_lists():
    nested = [[1, 2], [3, 4], [5, 6, 7, 8], [9]]
    flat = util.flatten_nested_lists(nested)
    assert flat == [1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_show_results():
    # full input
    succeeded = True
    detail = """\
- detail 1
- detail 2
- detail 3"""
    advice = """\
- advice 1
- advice 2
- advice 3"""
    dryrun = False
    report = util.show_results(succeeded, detail, advice, dryrun)
    assert report == """
*** SUCCEEDED ***

Detail:
- detail 1
- detail 2
- detail 3

Next:
- advice 1
- advice 2
- advice 3"""

    # no detail
    detail = None
    report = util.show_results(succeeded, detail, advice, dryrun)
    assert report == """
*** SUCCEEDED ***

Detail:
- (N/A)

Next:
- advice 1
- advice 2
- advice 3"""

    # no advice
    advice = None
    report = util.show_results(succeeded, detail, advice, dryrun)
    assert report == """
*** SUCCEEDED ***

Detail:
- (N/A)

Next:
- (N/A)"""

    # full input: failed
    succeeded = False
    detail = """\
- detail 1
- detail 2
- detail 3"""
    advice = """\
- advice 1
- advice 2
- advice 3"""
    report = util.show_results(succeeded, detail, advice, dryrun)
    assert report == """
* FAILED *

Detail:
- detail 1
- detail 2
- detail 3

Advice:
- advice 1
- advice 2
- advice 3"""

    # no detail
    detail = ''
    report = util.show_results(succeeded, detail, advice, dryrun)
    assert report == """
* FAILED *

Detail:
- (N/A)

Advice:
- advice 1
- advice 2
- advice 3"""

    # no advice
    advice = ''
    report = util.show_results(succeeded, detail, advice, dryrun)
    assert report == """
* FAILED *

Detail:
- (N/A)

Advice:
- (N/A)"""

    # dryrun
    dryrun = True
    report = util.show_results(succeeded, detail, advice, dryrun)
    assert report == """
** DRYRUN **

Detail:
- (N/A)

Advice:
- (N/A)"""


def test_pack_obj():
    # namespace
    obj = types.SimpleNamespace(n=1, s='hello', f=9.99, l=[1, 2, 3])
    topic = 'pkg'
    packed = util.pack_obj(obj, topic)
    assert packed == '<KK-ENV>{"payload": {"n": 1, "s": "hello", "f": 9.99, "l": [1, 2, 3]}, "topic": "pkg"}</KK-ENV>'
    # custom tags
    envelope = ('<MyEnv>', '</MyEnv>')
    packed = util.pack_obj(obj, topic, envelope=envelope)
    assert packed == '<MyEnv>{"payload": {"n": 1, "s": "hello", "f": 9.99, "l": [1, 2, 3]}, "topic": "pkg"}</MyEnv>'
    # default topic
    packed = util.pack_obj(obj)
    assert packed == '<KK-ENV>{"payload": {"n": 1, "s": "hello", "f": 9.99, "l": [1, 2, 3]}, "topic": "SimpleNamespace"}</KK-ENV>'

    # custom class
    class MyClass:
        def __init__(self, *args, **kwargs):
            self.n: int = 1
            self.s: str = 'hello'
            self.f: float = 9.99
            self.l: list[int] = [1, 2, 3]

        def main(self):
            pass
    obj = MyClass()
    packed = util.pack_obj(obj, classes=(MyClass,))
    assert packed == '<KK-ENV>{"payload": {"n": 1, "s": "hello", "f": 9.99, "l": [1, 2, 3]}, "topic": "MyClass"}</KK-ENV>'


def test_remove_duplication():
    my_list = [1, 2, 3, 2, 5, 3]
    assert (util.remove_duplication(my_list)) == [1, 2, 3, 5]
    my_list = [1, 5.0, 'xyz', 5.0, 5, 'xyz']
    assert (util.remove_duplication(my_list)) == [1, 5.0, 'xyz']


def test_validate_platform():
    supported = ['os1', 'os2']
    with pytest.raises(NotImplementedError):
        util.validate_platform(supported)
    supported = platform.system()
    util.validate_platform(supported)


def test_raise_error():
    errcls = NotImplementedError
    detail = '- This is a test error'
    advice = '- Fix it'
    with pytest.raises(NotImplementedError) as diagnostics:
        util.raise_error(errcls, detail, advice)
    assert str(diagnostics.value) == """\
Detail:
- This is a test error

Advice:
- Fix it"""


def test_get_drivewise_commondirs():
    # single path
    if is_posix := platform.system() != 'Windows':
        abs_paths = ['/path/to/dir1/file1']
        assert util.get_drivewise_commondirs(abs_paths) == {'/': '/path/to/dir1'}
        rel_paths = ['path/to/dir1/file1']
        assert util.get_drivewise_commondirs(rel_paths) == {'': 'path/to/dir1'}
    else:
        abs_paths = ['C:\\path\\to\\dir1\\file1.ext']
        assert util.get_drivewise_commondirs(abs_paths) == {'c:': 'c:\\path\\to\\dir1'}
        rel_paths = ['path\\to\\dir1\\file1']
        assert util.get_drivewise_commondirs(rel_paths) == {'': 'path\\to\\dir1'}
    # many paths
    if is_posix := platform.system() != 'Windows':
        abs_paths = ['/path/to/dir1/file1', '/path/to/dir2/', '/path/to/dir3/dir4/file2']
        assert util.get_drivewise_commondirs(abs_paths) == {'/': '/path/to'}
        rel_paths = ['path/to/dir1/file1', 'path/to/dir2/', 'path/to/dir3/dir4/file2']
        assert util.get_drivewise_commondirs(rel_paths) == {'': 'path/to'}
        # case-sensitive
        rel_paths = ['path/TO/dir1/file1', 'path/to/dir2/', 'path/to/dir3/dir4/file2']
        assert util.get_drivewise_commondirs(rel_paths) == {'': 'path'}
    else:
        abs_paths = [
            'C:\\path\\to\\dir1\\file1.ext',
            'c:\\path\\to\\dir2\\',
            'd:\\path\\to\\dir3\\dir4\\file2.ext',
            'D:\\path\\to\\dir5\\dir6\\file3.ext',
            'e:\\path\\to\\file8.ext',
            '\\\\Network\\share\\path\\to\\dir7\\file4.ext',
            '\\\\network\\share\\path\\to\\dir7\\dir8\\file5.ext',
            'path\\to\\dir9\\file6.ext',
            'path\\to\\dir9\\file7.ext',
        ]
        assert util.get_drivewise_commondirs(abs_paths) == {
            'c:': 'c:\\path\\to',
            'd:': 'd:\\path\\to',
            'e:': 'e:\\path\\to',
            '\\\\network\\share': '\\\\network\\share\\path\\to\\dir7',
            '': 'path\\to\\dir9'
        }
        # case-insensitive
        rel_paths = [
            'path\\to\\dir1\\file1.ext',
            '\\Path\\to\\dir2\\',
            'path\\To\\dir1\\dir4\\file2.ext'
        ]
        assert util.get_drivewise_commondirs(rel_paths) == {'': 'path\\to'}


def test_split_platform_drive():
    if platform.system() == 'Windows':
        path = osp.normpath('C:/path/to/dir1/file1')
        assert util.split_platform_drive(path) == ('c:', osp.normpath('path/to/dir1/file1'))
        path = osp.normpath('path/to/dir1/file1')
        assert util.split_platform_drive(path) == ('', osp.normpath('path/to/dir1/file1'))
    else:
        path = '/path/to/dir1/file1'
        assert util.split_platform_drive(path) == ('/', 'path/to/dir1/file1')
        path = 'path/to/dir1/file1'
        assert util.split_platform_drive(path) == ('', 'path/to/dir1/file1')
