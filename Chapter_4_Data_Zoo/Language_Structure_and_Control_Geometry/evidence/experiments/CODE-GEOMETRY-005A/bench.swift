func clamp(_ x: Int, _ lo: Int, _ hi: Int) -> Int {
  if x < lo { return lo }
  if x > hi { return hi }
  return x
}
func gcd(_ aa: Int, _ bb: Int) -> Int {
  var a = aa; var b = bb
  while b != 0 { let t = a % b; a = b; b = t }
  return a
}
func fib(_ n: Int) -> Int {
  var a = 0; var b = 1
  for _ in 0..<n { let t = a + b; a = b; b = t }
  return a
}
func isPrime(_ n: Int) -> Bool {
  if n < 2 { return false }
  var d = 2
  while d*d <= n { if n % d == 0 { return false }; d += 1 }
  return true
}
func binarySearch(_ xs: [Int], _ target: Int) -> Int {
  var lo = 0; var hi = xs.count - 1
  while lo <= hi {
    let mid = (lo + hi) / 2
    if xs[mid] == target { return mid }
    if xs[mid] < target { lo = mid + 1 } else { hi = mid - 1 }
  }
  return -1
}
func prefixSums(_ xs: [Int]) -> [Int] {
  var out: [Int] = []; var total = 0
  for x in xs { total += x; out.append(total) }
  return out
}
func countVowels(_ s: String) -> Int {
  var count = 0
  for ch in s.lowercased() { if "aeiou".contains(ch) { count += 1 } }
  return count
}
func mergeSorted(_ a: [Int], _ b: [Int]) -> [Int] {
  var i=0; var j=0; var out:[Int]=[]
  while i<a.count && j<b.count { if a[i] <= b[j] { out.append(a[i]); i += 1 } else { out.append(b[j]); j += 1 } }
  while i<a.count { out.append(a[i]); i += 1 }
  while j<b.count { out.append(b[j]); j += 1 }
  return out
}
func runCount(_ s: String) -> Int {
  let chars = Array(s)
  if chars.isEmpty { return 0 }
  var count = 1
  for i in 1..<chars.count { if chars[i] != chars[i-1] { count += 1 } }
  return count
}
func sumPositive(_ xs: [Int]) -> Int {
  var total = 0
  for x in xs { if x > 0 { total += x } }
  return total
}
