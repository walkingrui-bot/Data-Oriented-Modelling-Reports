int clamp(int x, int lo, int hi) {
  if (x < lo) return lo;
  if (x > hi) return hi;
  return x;
}
int gcd(int a, int b) {
  while (b != 0) { int t = a % b; a = b; b = t; }
  return a;
}
int fib(int n) {
  int a = 0, b = 1;
  for (int i = 0; i < n; i++) { int t = a + b; a = b; b = t; }
  return a;
}
int is_prime(int n) {
  if (n < 2) return 0;
  int d = 2;
  while (d * d <= n) { if (n % d == 0) return 0; d += 1; }
  return 1;
}
int binary_search(const int *xs, int n, int target) {
  int lo = 0, hi = n - 1;
  while (lo <= hi) {
    int mid = (lo + hi) / 2;
    if (xs[mid] == target) return mid;
    if (xs[mid] < target) lo = mid + 1; else hi = mid - 1;
  }
  return -1;
}
void prefix_sums(const int *xs, int n, int *out) {
  int total = 0;
  for (int i = 0; i < n; i++) { total += xs[i]; out[i] = total; }
}
int count_vowels(const char *s) {
  int count = 0;
  for (int i = 0; s[i] != '\0'; i++) {
    char c = s[i];
    if (c=='a'||c=='e'||c=='i'||c=='o'||c=='u'||c=='A'||c=='E'||c=='I'||c=='O'||c=='U') count += 1;
  }
  return count;
}
int merge_sorted(const int *a, int na, const int *b, int nb, int *out) {
  int i=0,j=0,k=0;
  while (i<na && j<nb) { if (a[i] <= b[j]) out[k++]=a[i++]; else out[k++]=b[j++]; }
  while (i<na) out[k++]=a[i++];
  while (j<nb) out[k++]=b[j++];
  return k;
}
int run_count(const char *s) {
  if (s[0]=='\0') return 0;
  int count=1;
  for (int i=1; s[i]!='\0'; i++) if (s[i]!=s[i-1]) count += 1;
  return count;
}
int sum_positive(const int *xs, int n) {
  int total=0;
  for (int i=0;i<n;i++) if (xs[i]>0) total += xs[i];
  return total;
}
