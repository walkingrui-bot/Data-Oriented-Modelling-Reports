function clamp(x: number, lo: number, hi: number): number {
  if (x < lo) return lo;
  if (x > hi) return hi;
  return x;
}
function gcd(a: number, b: number): number {
  while (b !== 0) { const t: number = a % b; a = b; b = t; }
  return a;
}
function fib(n: number): number {
  let a: number = 0, b: number = 1;
  for (let i: number = 0; i < n; i++) { const t: number = a + b; a = b; b = t; }
  return a;
}
function isPrime(n: number): boolean {
  if (n < 2) return false;
  let d: number = 2;
  while (d * d <= n) {
    if (n % d === 0) return false;
    d += 1;
  }
  return true;
}
function binarySearch(xs: number[], target: number): number {
  let lo: number = 0, hi: number = xs.length - 1;
  while (lo <= hi) {
    const mid: number = Math.floor((lo + hi) / 2);
    if (xs[mid] === target) return mid;
    if (xs[mid] < target) lo = mid + 1; else hi = mid - 1;
  }
  return -1;
}
function prefixSums(xs: number[]): number[] {
  const out: number[] = []; let total: number = 0;
  for (const x of xs) { total += x; out.push(total); }
  return out;
}
function countVowels(s: string): number {
  let count: number = 0;
  for (const ch of s.toLowerCase()) if ("aeiou".includes(ch)) count += 1;
  return count;
}
function mergeSorted(a: number[], b: number[]): number[] {
  let i: number = 0, j: number = 0; const out: number[] = [];
  while (i < a.length && j < b.length) {
    if (a[i] <= b[j]) out.push(a[i++]); else out.push(b[j++]);
  }
  while (i < a.length) out.push(a[i++]);
  while (j < b.length) out.push(b[j++]);
  return out;
}
function runCount(s: string): number {
  if (s.length === 0) return 0;
  let count: number = 1;
  for (let i: number = 1; i < s.length; i++) if (s[i] !== s[i - 1]) count += 1;
  return count;
}
function sumPositive(xs: number[]): number {
  let total: number = 0;
  for (const x of xs) if (x > 0) total += x;
  return total;
}
