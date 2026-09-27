function clamp(x, lo, hi) {
  if (x < lo) return lo;
  if (x > hi) return hi;
  return x;
}
function gcd(a, b) {
  while (b !== 0) { const t = a % b; a = b; b = t; }
  return a;
}
function fib(n) {
  let a = 0, b = 1;
  for (let i = 0; i < n; i++) { const t = a + b; a = b; b = t; }
  return a;
}
function isPrime(n) {
  if (n < 2) return false;
  let d = 2;
  while (d * d <= n) {
    if (n % d === 0) return false;
    d += 1;
  }
  return true;
}
function binarySearch(xs, target) {
  let lo = 0, hi = xs.length - 1;
  while (lo <= hi) {
    const mid = Math.floor((lo + hi) / 2);
    if (xs[mid] === target) return mid;
    if (xs[mid] < target) lo = mid + 1; else hi = mid - 1;
  }
  return -1;
}
function prefixSums(xs) {
  const out = []; let total = 0;
  for (const x of xs) { total += x; out.push(total); }
  return out;
}
function countVowels(s) {
  let count = 0;
  for (const ch of s.toLowerCase()) if ("aeiou".includes(ch)) count += 1;
  return count;
}
function mergeSorted(a, b) {
  let i = 0, j = 0; const out = [];
  while (i < a.length && j < b.length) {
    if (a[i] <= b[j]) out.push(a[i++]); else out.push(b[j++]);
  }
  while (i < a.length) out.push(a[i++]);
  while (j < b.length) out.push(b[j++]);
  return out;
}
function runCount(s) {
  if (s.length === 0) return 0;
  let count = 1;
  for (let i = 1; i < s.length; i++) if (s[i] !== s[i - 1]) count += 1;
  return count;
}
function sumPositive(xs) {
  let total = 0;
  for (const x of xs) if (x > 0) total += x;
  return total;
}
