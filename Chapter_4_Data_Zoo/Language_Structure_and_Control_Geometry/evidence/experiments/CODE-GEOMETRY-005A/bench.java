class Bench {
  static int clamp(int x, int lo, int hi) {
    if (x < lo) return lo;
    if (x > hi) return hi;
    return x;
  }
  static int gcd(int a, int b) {
    while (b != 0) { int t = a % b; a = b; b = t; }
    return a;
  }
  static long fib(int n) {
    long a = 0, b = 1;
    for (int i = 0; i < n; i++) { long t = a + b; a = b; b = t; }
    return a;
  }
  static boolean isPrime(int n) {
    if (n < 2) return false;
    int d = 2;
    while (d * d <= n) { if (n % d == 0) return false; d += 1; }
    return true;
  }
  static int binarySearch(int[] xs, int target) {
    int lo = 0, hi = xs.length - 1;
    while (lo <= hi) {
      int mid = (lo + hi) / 2;
      if (xs[mid] == target) return mid;
      if (xs[mid] < target) lo = mid + 1; else hi = mid - 1;
    }
    return -1;
  }
  static int[] prefixSums(int[] xs) {
    int[] out = new int[xs.length]; int total = 0;
    for (int i = 0; i < xs.length; i++) { total += xs[i]; out[i] = total; }
    return out;
  }
  static int countVowels(String s) {
    int count = 0;
    for (int i=0;i<s.length();i++) {
      char c = Character.toLowerCase(s.charAt(i));
      if (c=='a'||c=='e'||c=='i'||c=='o'||c=='u') count += 1;
    }
    return count;
  }
  static int[] mergeSorted(int[] a, int[] b) {
    int[] out = new int[a.length+b.length]; int i=0,j=0,k=0;
    while (i<a.length && j<b.length) { if (a[i] <= b[j]) out[k++]=a[i++]; else out[k++]=b[j++]; }
    while (i<a.length) out[k++]=a[i++];
    while (j<b.length) out[k++]=b[j++];
    return out;
  }
  static int runCount(String s) {
    if (s.length()==0) return 0;
    int count=1;
    for (int i=1;i<s.length();i++) if (s.charAt(i)!=s.charAt(i-1)) count += 1;
    return count;
  }
  static int sumPositive(int[] xs) {
    int total=0;
    for (int x: xs) if (x>0) total += x;
    return total;
  }
}
