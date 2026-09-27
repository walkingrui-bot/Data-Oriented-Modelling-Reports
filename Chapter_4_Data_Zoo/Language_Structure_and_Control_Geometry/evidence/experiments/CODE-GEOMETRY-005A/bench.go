package bench

func clamp(x int, lo int, hi int) int {
  if x < lo { return lo }
  if x > hi { return hi }
  return x
}
func gcd(a int, b int) int {
  for b != 0 { a, b = b, a%b }
  return a
}
func fib(n int) int {
  a, b := 0, 1
  for i := 0; i < n; i++ { a, b = b, a+b }
  return a
}
func isPrime(n int) bool {
  if n < 2 { return false }
  for d := 2; d*d <= n; d++ { if n%d == 0 { return false } }
  return true
}
func binarySearch(xs []int, target int) int {
  lo, hi := 0, len(xs)-1
  for lo <= hi {
    mid := (lo+hi)/2
    if xs[mid] == target { return mid }
    if xs[mid] < target { lo = mid+1 } else { hi = mid-1 }
  }
  return -1
}
func prefixSums(xs []int) []int {
  out := make([]int, len(xs)); total := 0
  for i, x := range xs { total += x; out[i] = total }
  return out
}
func countVowels(s string) int {
  count := 0
  for i := 0; i < len(s); i++ {
    c := s[i]
    if c=='a'||c=='e'||c=='i'||c=='o'||c=='u'||c=='A'||c=='E'||c=='I'||c=='O'||c=='U' { count++ }
  }
  return count
}
func mergeSorted(a []int, b []int) []int {
  out := make([]int, 0, len(a)+len(b)); i, j := 0, 0
  for i<len(a) && j<len(b) { if a[i] <= b[j] { out=append(out,a[i]); i++ } else { out=append(out,b[j]); j++ } }
  for i<len(a) { out=append(out,a[i]); i++ }
  for j<len(b) { out=append(out,b[j]); j++ }
  return out
}
func runCount(s string) int {
  if len(s)==0 { return 0 }
  count := 1
  for i:=1;i<len(s);i++ { if s[i]!=s[i-1] { count++ } }
  return count
}
func sumPositive(xs []int) int {
  total := 0
  for _, x := range xs { if x>0 { total += x } }
  return total
}
