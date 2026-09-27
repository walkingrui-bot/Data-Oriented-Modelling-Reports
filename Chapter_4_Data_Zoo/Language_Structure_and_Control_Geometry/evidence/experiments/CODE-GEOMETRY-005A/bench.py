def clamp(x: int, lo: int, hi: int) -> int:
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x

def gcd(a: int, b: int) -> int:
    while b != 0:
        a, b = b, a % b
    return a

def fib(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True

def binary_search(xs: list[int], target: int) -> int:
    lo, hi = 0, len(xs) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if xs[mid] == target:
            return mid
        if xs[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

def prefix_sums(xs: list[int]) -> list[int]:
    out: list[int] = []
    total = 0
    for x in xs:
        total += x
        out.append(total)
    return out

def count_vowels(s: str) -> int:
    count = 0
    for ch in s.lower():
        if ch in "aeiou":
            count += 1
    return count

def merge_sorted(a: list[int], b: list[int]) -> list[int]:
    i, j = 0, 0
    out: list[int] = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    while i < len(a):
        out.append(a[i]); i += 1
    while j < len(b):
        out.append(b[j]); j += 1
    return out

def run_count(s: str) -> int:
    if not s:
        return 0
    count = 1
    for i in range(1, len(s)):
        if s[i] != s[i - 1]:
            count += 1
    return count

def sum_positive(xs: list[int]) -> int:
    total = 0
    for x in xs:
        if x > 0:
            total += x
    return total
