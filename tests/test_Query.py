import pytest

from r3tagger.query import Retry, QueryError

# I know. Sorry.
count = 0


def test_Retry():

    @Retry(Exception, 4)
    def invoke_this():
        global count
        count += 1
        raise Exception("dummy error")

    with pytest.raises(QueryError):
        invoke_this()

    assert count == 4
