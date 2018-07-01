from infrabin.helpers import fib


def test_fib():
    # First 5 Fibonacci numbers
    # 1 1 2 3 5
    result = fib(4)
    assert result == 3
