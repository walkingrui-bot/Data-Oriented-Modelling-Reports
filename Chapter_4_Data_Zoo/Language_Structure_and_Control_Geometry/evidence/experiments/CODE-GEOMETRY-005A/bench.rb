def clamp(x, lo, hi)
  return lo if x < lo
  return hi if x > hi
  x
end

def gcd(a, b)
  while b != 0
    a, b = b, a % b
  end
  a
end

def fib(n)
  a = 0; b = 1
  n.times do
    a, b = b, a + b
  end
  a
end

def is_prime(n)
  return false if n < 2
  d = 2
  while d * d <= n
    return false if n % d == 0
    d += 1
  end
  true
end

def binary_search(xs, target)
  lo = 0; hi = xs.length - 1
  while lo <= hi
    mid = (lo + hi) / 2
    return mid if xs[mid] == target
    if xs[mid] < target then lo = mid + 1 else hi = mid - 1 end
  end
  -1
end

def prefix_sums(xs)
  out = []; total = 0
  xs.each do |x|
    total += x
    out << total
  end
  out
end

def count_vowels(s)
  count = 0
  s.downcase.each_char { |ch| count += 1 if "aeiou".include?(ch) }
  count
end

def merge_sorted(a, b)
  i = 0; j = 0; out = []
  while i < a.length && j < b.length
    if a[i] <= b[j] then out << a[i]; i += 1 else out << b[j]; j += 1 end
  end
  while i < a.length; out << a[i]; i += 1 end
  while j < b.length; out << b[j]; j += 1 end
  out
end

def run_count(s)
  return 0 if s.empty?
  count = 1
  (1...s.length).each { |i| count += 1 if s[i] != s[i-1] }
  count
end

def sum_positive(xs)
  total = 0
  xs.each { |x| total += x if x > 0 }
  total
end
