from r3tagger import library

path_file = '/path/to/folder/file.ext'

path_folder_1 = '/path/to/folder'
path_folder_2 = '/path/to/folder/'


def test_extension():
    assert library.extension(path_file) == '.ext'


def test_parent():
    result = '/path/to'
    assert library.parent(path_folder_1) == result
    assert library.parent(path_folder_2) == result


def test_parent_arg():
    assert library.parent(path_folder_1, 2) == '/path'


def test_filename():
    assert library.filename(path_file) == 'file.ext'
