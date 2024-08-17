
from exercises import sum_two_numbers, filter_even_numbers, sort_numbers

assert sum_two_numbers(1, 2) == 3, 'Test Failed: sum_two_numbers'
assert filter_even_numbers([1, 2, 3, 4]) == [2, 4], 'Test Failed: filter_even_numbers'
assert sort_numbers([3, 2, 1]) == [1, 2, 3], 'Test Failed: sort_numbers'

print('All tests passed.')

