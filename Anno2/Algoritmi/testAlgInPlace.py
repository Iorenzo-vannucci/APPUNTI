#REVERSE 
def reverse_in_place(arr):
    left, right = 0, len(arr) - 1
    while left < right:
        arr[left], arr[right] = arr[right], arr[left]  # Scambio in-place
        arr[right] = arr[left]
        left += 1
        right -= 1

arr = [1, 2, 3, 4, 5]
reverse_in_place(arr)
print(arr)  # Output: [5, 4, 3, 2, 1]

print(arr.reverse)