import threading
from datetime import datetime

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


def test_easy_TimedSemaphore():
    """Five requests at one request per second"""
    def dummy_request(record):
        record.append(datetime.now())

    requests_completed = []
    threads = []
    lock = library.TimedSemaphore()
    for _ in range(5):
        with lock:
            thread = threading.Thread(target=dummy_request,
                                    args=(requests_completed,))
            threads.append(thread)
            thread.start()

    for index, time in enumerate(requests_completed[1:]):
        time_diff = time - requests_completed[index - 1]
        assert time_diff.seconds >= 1

    assert len(requests_completed) == 5


def test_stress_TimedSemaphore():
    """One thousand reqeuests at one hundred per second"""
    def dummy_request(record):
        record.append(datetime.now())

    number_of_queries = 1000
    queries_per_limit = 100
    delay = 1

    requests_completed = []
    threads = []
    lock = library.TimedSemaphore(delay=delay, value=queries_per_limit)
    start_time = datetime.now()
    for _ in range(number_of_queries):
        with lock:
            thread = threading.Thread(target=dummy_request,
                                    args=(requests_completed,))
            threads.append(thread)
            thread.start()

    seconds_total = int(delay * (number_of_queries / queries_per_limit))
    query_record = {second: 0 for second in range(seconds_total)}
    for query in requests_completed:
        seconds_since_start = (query - start_time).seconds
        query_record[seconds_since_start] += 1

    for number_of_queries in query_record.values():
        assert number_of_queries <= queries_per_limit

    assert len(requests_completed) == 1000
