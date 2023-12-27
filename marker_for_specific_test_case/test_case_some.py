# content of test_someenv.py

import pytest


@pytest.mark.testcase("1111")
def test_basic_db_operation_1():
    pass



@pytest.mark.testcase("2222")
def test_basic_db_operation_2():
    pass



# execution command : pytest --TC 1111