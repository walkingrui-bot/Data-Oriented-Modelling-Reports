from pathlib import Path
import re, json, ast, math, subprocess, tempfile, os, statistics
from collections import Counter, defaultdict
import numpy as np

ROOT=Path('/mnt/data/code_geometry_005a')
ROOT.mkdir(exist_ok=True)

corpora={}

corpora['Python'] = r'''
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
'''.strip()+"\n"

corpora['JavaScript'] = r'''
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
'''.strip()+"\n"

corpora['TypeScript'] = r'''
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
'''.strip()+"\n"

# C and C++ use raw arrays to avoid standard-library AST pollution.
corpora['C'] = r'''
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
'''.strip()+"\n"

corpora['C++'] = r'''
int clamp(int x, int lo, int hi) {
  if (x < lo) return lo;
  if (x > hi) return hi;
  return x;
}
int gcd(int a, int b) {
  while (b != 0) { int t = a % b; a = b; b = t; }
  return a;
}
long long fib(int n) {
  long long a = 0, b = 1;
  for (int i = 0; i < n; ++i) { auto t = a + b; a = b; b = t; }
  return a;
}
bool is_prime(int n) {
  if (n < 2) return false;
  for (int d = 2; d * d <= n; ++d) if (n % d == 0) return false;
  return true;
}
int binary_search(const int *xs, int n, int target) {
  int lo = 0, hi = n - 1;
  while (lo <= hi) {
    const int mid = (lo + hi) / 2;
    if (xs[mid] == target) return mid;
    if (xs[mid] < target) lo = mid + 1; else hi = mid - 1;
  }
  return -1;
}
void prefix_sums(const int *xs, int n, int *out) {
  int total = 0;
  for (int i = 0; i < n; ++i) { total += xs[i]; out[i] = total; }
}
int count_vowels(const char *s) {
  int count = 0;
  for (int i = 0; s[i] != '\0'; ++i) {
    const char c = s[i];
    if (c=='a'||c=='e'||c=='i'||c=='o'||c=='u'||c=='A'||c=='E'||c=='I'||c=='O'||c=='U') ++count;
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
  for (int i=1; s[i]!='\0'; ++i) if (s[i]!=s[i-1]) ++count;
  return count;
}
int sum_positive(const int *xs, int n) {
  int total=0;
  for (int i=0;i<n;++i) if (xs[i]>0) total += xs[i];
  return total;
}
'''.strip()+"\n"

corpora['Java'] = r'''
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
'''.strip()+"\n"

corpora['Go'] = r'''
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
'''.strip()+"\n"

corpora['Swift'] = r'''
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
'''.strip()+"\n"

corpora['Ruby'] = r'''
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
'''.strip()+"\n"

exts={'Python':'py','JavaScript':'js','TypeScript':'ts','C':'c','C++':'cpp','Java':'java','Go':'go','Swift':'swift','Ruby':'rb'}
for lang,code in corpora.items():
    (ROOT/f"bench.{exts[lang]}").write_text(code)

# ---------- universal lexical tokenizer ----------
keywords={
'Python': set('def return if else for while in not and or True False None class import from as break continue pass lambda with yield'.split()),
'JavaScript': set('function return if else for while const let var of in true false null new class break continue'.split()),
'TypeScript': set('function return if else for while const let var of in true false null new class interface type number string boolean break continue'.split()),
'C': set('int char void return if else for while const struct static break continue'.split()),
'C++': set('int char void bool long auto return if else for while const true false class struct static break continue'.split()),
'Java': set('class static int long char boolean void return if else for while new true false break continue'.split()),
'Go': set('package func return if else for range var const true false make append break continue'.split()),
'Swift': set('func return if else for while in var let true false Int Bool String break continue'.split()),
'Ruby': set('def end return if else elsif unless while do true false nil class then'.split()),
}
# ordered regex groups
TOKEN_RE=re.compile(r'''(?P<COMMENT>//[^\n]*|/\*.*?\*/|\#[^\n]*)|(?P<STRING>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|(?P<NUMBER>\b(?:\d+(?:\.\d+)?)\b)|(?P<ID>[A-Za-z_][A-Za-z_0-9]*|[\u0080-\uffff]+)|(?P<OP>===|!==|==|!=|<=|>=|<<|>>|\+=|-=|\*=|/=|%=|\+\+|--|&&|\|\||->|=>|:=|\.\.<|\.\.\.|::|\*\*|//|[{}()\[\];,.:?~+\-*/%<>=!&|^])''',re.S)

def lexical_tokens(lang, code):
    out=[]
    for m in TOKEN_RE.finditer(code):
        k=m.lastgroup; v=m.group()
        if k=='COMMENT': continue
        if k=='ID':
            out.append(v if v in keywords[lang] else '<ID>')
        elif k=='NUMBER': out.append('<NUM>')
        elif k=='STRING': out.append('<STR>')
        else: out.append(v)
    return out

def transition_spectrum(seq):
    vocab=sorted(set(seq))
    idx={x:i for i,x in enumerate(vocab)}
    V=len(vocab)
    counts=np.zeros((V,V),float); row=np.zeros(V,float); nxt=np.zeros(V,float)
    for a,b in zip(seq[:-1],seq[1:]):
        i,j=idx[a],idx[b]; counts[i,j]+=1; row[i]+=1; nxt[j]+=1
    total=nxt.sum()
    if total==0:return dict(stable_rank=0,top3=0,participation=0,V=V)
    pglobal=nxt/total
    C=np.zeros_like(counts)
    for i in range(V):
        if row[i]>0: C[i]=counts[i]/row[i]-pglobal
    w=row/row.sum()
    A=(C.T*w)@C  # weighted covariance in next-token space
    vals=np.linalg.eigvalsh(A)
    vals=np.clip(vals,0,None)[::-1]
    if vals.sum()==0:return dict(stable_rank=0,top3=0,participation=0,V=V)
    sr=vals.sum()/vals[0]
    pr=(vals.sum()**2)/(np.square(vals).sum())
    top3=vals[:3].sum()/vals.sum()
    return dict(stable_rank=float(sr), top3=float(top3), participation=float(pr), V=V, eig=vals.tolist())

# ---------- tree metrics helpers ----------
def tree_metrics(nodes, edges):
    # nodes list of type labels indexed 0..n-1; edges parent-child index tuples
    n=len(nodes)
    children=defaultdict(list); indeg=[0]*n
    for a,b in edges:
        children[a].append(b); indeg[b]+=1
    roots=[i for i,d in enumerate(indeg) if d==0]
    if not roots and n: roots=[0]
    depths=[]; stack=[(r,0) for r in roots]
    seen=set()
    while stack:
        i,d=stack.pop()
        if i in seen: continue
        seen.add(i); depths.append(d)
        for c in children[i]: stack.append((c,d+1))
    branch=[len(children[i]) for i in range(n) if len(children[i])>0]
    leaf=sum(1 for i in range(n) if len(children[i])==0)
    cnt=Counter(nodes)
    probs=np.array(list(cnt.values()),float)/max(1,n)
    H=float(-(probs*np.log2(probs)).sum()) if len(probs) else 0.0
    # parent->child type transition spectrum
    trans=[]
    for a,b in edges: trans.append((nodes[a],nodes[b]))
    # Represent each edge path as flattened alternating types for simple spectrum? Better construct conditional code directly.
    types=sorted(set(nodes)); ti={t:i for i,t in enumerate(types)}; V=len(types)
    counts=np.zeros((V,V),float); row=np.zeros(V,float); nxt=np.zeros(V,float)
    for a,b in edges:
        i,j=ti[nodes[a]],ti[nodes[b]]; counts[i,j]+=1; row[i]+=1; nxt[j]+=1
    if nxt.sum()>0:
        p=nxt/nxt.sum(); C=np.zeros_like(counts)
        for i in range(V):
            if row[i]>0: C[i]=counts[i]/row[i]-p
        w=row/row.sum(); A=(C.T*w)@C
        vals=np.clip(np.linalg.eigvalsh(A),0,None)[::-1]
        if vals.sum()>0:
            sr=float(vals.sum()/vals[0]); top3=float(vals[:3].sum()/vals.sum()); pr=float(vals.sum()**2/np.square(vals).sum())
        else: sr=top3=pr=0.0
    else: sr=top3=pr=0.0
    return dict(node_count=n, max_depth=max(depths) if depths else 0, mean_depth=float(np.mean(depths)) if depths else 0,
                mean_branch=float(np.mean(branch)) if branch else 0, leaf_fraction=leaf/max(1,n), type_entropy=H,
                type_count=len(cnt), ast_stable_rank=sr, ast_top3=top3, ast_participation=pr)

# Python AST
def py_tree(path):
    root=ast.parse(path.read_text())
    nodes=[]; edges=[]
    def rec(x):
        i=len(nodes); nodes.append(type(x).__name__)
        for c in ast.iter_child_nodes(x):
            j=rec(c); edges.append((i,j))
        return i
    rec(root); return nodes,edges

# JS/TS via TypeScript compiler API
JS_HELPER=ROOT/'ts_ast.js'
JS_HELPER.write_text(r'''
const fs=require('fs'); const ts=require('typescript');
const file=process.argv[2], mode=process.argv[3];
const code=fs.readFileSync(file,'utf8');
const kind=mode==='ts'?ts.ScriptKind.TS:ts.ScriptKind.JS;
const root=ts.createSourceFile(file,code,ts.ScriptTarget.Latest,true,kind);
const nodes=[], edges=[];
function rec(n){ const i=nodes.length; nodes.push(ts.SyntaxKind[n.kind]); n.forEachChild(c=>{const j=rec(c); edges.push([i,j]);}); return i; }
rec(root); console.log(JSON.stringify({nodes,edges,diagnostics:root.parseDiagnostics.map(d=>d.messageText)}));
''')
def ts_tree(path, mode):
    r=subprocess.run(['node',str(JS_HELPER),str(path),mode],capture_output=True,text=True,check=True)
    obj=json.loads(r.stdout); return obj['nodes'], [tuple(x) for x in obj['edges']], obj['diagnostics']

# C/C++ clang JSON AST with source-file filtering

def clang_tree(path, cpp=False):
    cmd=['clang++' if cpp else 'clang','-std=c++17' if cpp else '-std=c11','-Xclang','-ast-dump=json','-fsyntax-only',str(path)]
    r=subprocess.run(cmd,capture_output=True,text=True,check=True)
    root=json.loads(r.stdout)
    nodes=[];edges=[]
    def rec(n,parent=None):
        cur=len(nodes); nodes.append(n.get('kind','?'))
        if parent is not None: edges.append((parent,cur))
        for c in n.get('inner',[]) or []: rec(c,cur)
        return cur
    # With no headers in these controlled snippets, source declarations have concrete line/offset locations; compiler builtins do not.
    for n in root.get('inner',[]) or []:
        loc=n.get('loc',{}) or {}
        if n.get('kind')=='FunctionDecl' and ('line' in loc or 'offset' in loc):
            rec(n,None)
    return nodes,edges

# Java AST helper using javac tree API
JAVA_HELPER=ROOT/'AstDump.java'
JAVA_HELPER.write_text(r'''
import java.io.*; import java.util.*; import javax.tools.*; import com.sun.source.tree.*; import com.sun.source.util.*;
public class AstDump {
  static ArrayList<String> nodes=new ArrayList<>(); static ArrayList<int[]> edges=new ArrayList<>();
  static class V extends TreeScanner<Integer,Integer> {
    @Override public Integer scan(Tree t, Integer p){ if(t==null)return -1; int me=nodes.size(); nodes.add(t.getKind().name()); if(p!=null&&p>=0)edges.add(new int[]{p,me}); return super.scan(t,me); }
  }
  public static void main(String[] a) throws Exception {
    JavaCompiler c=ToolProvider.getSystemJavaCompiler(); StandardJavaFileManager fm=c.getStandardFileManager(null,null,null);
    Iterable<? extends JavaFileObject> fs=fm.getJavaFileObjects(a[0]); JavacTask task=(JavacTask)c.getTask(null,fm,null,Arrays.asList("-proc:none"),null,fs);
    for(CompilationUnitTree cu:task.parse()) new V().scan(cu,-1);
    StringBuilder sb=new StringBuilder(); sb.append("{\"nodes\":[");
    for(int i=0;i<nodes.size();i++){if(i>0)sb.append(',');sb.append('"').append(nodes.get(i)).append('"');}
    sb.append("],\"edges\":["); for(int i=0;i<edges.size();i++){if(i>0)sb.append(',');sb.append('[').append(edges.get(i)[0]).append(',').append(edges.get(i)[1]).append(']');}
    sb.append("]}"); System.out.println(sb.toString());
  }
}
''')
subprocess.run(['javac',str(JAVA_HELPER)],check=True,cwd=ROOT)
def java_tree(path):
    r=subprocess.run(['java','-cp',str(ROOT),'AstDump',str(path)],capture_output=True,text=True,check=True)
    obj=json.loads(r.stdout); return obj['nodes'],[tuple(x) for x in obj['edges']]

# Go AST helper
GO_HELPER=ROOT/'astdump.go'
GO_HELPER.write_text(r'''
package main
import("encoding/json";"fmt";"go/ast";"go/parser";"go/token";"os";"reflect")
type Out struct{Nodes []string `json:"nodes"`; Edges [][2]int `json:"edges"`}
func main(){fset:=token.NewFileSet(); f,err:=parser.ParseFile(fset,os.Args[1],nil,0); if err!=nil{panic(err)}; o:=Out{}; var stack []int; ast.Inspect(f,func(n ast.Node) bool{if n==nil{ if len(stack)>0{stack=stack[:len(stack)-1]}; return false}; typ:=reflect.TypeOf(n).Elem().Name(); me:=len(o.Nodes); o.Nodes=append(o.Nodes,typ); if len(stack)>0{o.Edges=append(o.Edges,[2]int{stack[len(stack)-1],me})}; stack=append(stack,me); return true}); b,_:=json.Marshal(o); fmt.Println(string(b))}
''')
# note ast.Inspect nil callbacks make stack approach incorrect for sibling boundaries? It does call nil after each subtree. okay.
GO_BIN=ROOT/'astdump_go_bin'
subprocess.run(['go','build','-o',str(GO_BIN),str(GO_HELPER)],check=True,cwd=ROOT)
def go_tree(path):
    r=subprocess.run([str(GO_BIN),str(path)],capture_output=True,text=True,check=True,cwd=ROOT)
    obj=json.loads(r.stdout); return obj['nodes'],[tuple(x) for x in obj['edges']]

# Swift dump AST indentation parser
def swift_tree(path):
    r=subprocess.run(['swiftc','-dump-ast',str(path)],capture_output=True,text=True,check=True)
    text=r.stdout+r.stderr
    nodes=[];edges=[]; stack=[]
    for line in text.splitlines():
        if not line.strip().startswith('('): continue
        indent=len(line)-len(line.lstrip(' '))
        m=re.match(r'\s*\(([^\s()]+)',line)
        if not m: continue
        typ=m.group(1)
        me=len(nodes); nodes.append(typ)
        while stack and stack[-1][0]>=indent: stack.pop()
        if stack: edges.append((stack[-1][1],me))
        stack.append((indent,me))
    return nodes,edges

# Ruby Ripper S-expression to tree
RUBY_HELPER=ROOT/'astdump.rb'
RUBY_HELPER.write_text(r'''
require 'ripper'; require 'json'; sexp=Ripper.sexp(File.read(ARGV[0])); nodes=[]; edges=[]
def rec(x,nodes,edges,parent=nil)
  return if x.nil?
  if x.is_a?(Array)
    label = x[0].is_a?(Symbol) ? x[0].to_s : 'array'
    me=nodes.length; nodes << label; edges << [parent,me] unless parent.nil?
    start=(x[0].is_a?(Symbol) ? 1 : 0)
    x[start..-1].each{|c| rec(c,nodes,edges,me) if c.is_a?(Array)}
  end
end
rec(sexp,nodes,edges,nil); puts JSON.generate({nodes:nodes,edges:edges})
''')
def ruby_tree(path):
    r=subprocess.run(['ruby',str(RUBY_HELPER),str(path)],capture_output=True,text=True,check=True)
    obj=json.loads(r.stdout); return obj['nodes'],[tuple(x) for x in obj['edges']]

# Validation and metrics
validators={
'Python': lambda p: ast.parse(p.read_text()),
'JavaScript': lambda p: ts_tree(p,'js'),
'TypeScript': lambda p: subprocess.run(['tsc','--pretty','false','--noEmit','--target','ES2020',str(p)],capture_output=True,text=True,check=True),
'C': lambda p: subprocess.run(['clang','-std=c11','-fsyntax-only',str(p)],capture_output=True,text=True,check=True),
'C++': lambda p: subprocess.run(['clang++','-std=c++17','-fsyntax-only',str(p)],capture_output=True,text=True,check=True),
'Java': lambda p: subprocess.run(['javac','-d',str(ROOT/'javac_out'),str(p)],capture_output=True,text=True,check=True),
'Go': lambda p: subprocess.run(['gofmt','-d',str(p)],capture_output=True,text=True,check=True),
'Swift': lambda p: subprocess.run(['swiftc','-typecheck',str(p)],capture_output=True,text=True,check=True),
'Ruby': lambda p: subprocess.run(['ruby','-c',str(p)],capture_output=True,text=True,check=True),
}
(ROOT/'javac_out').mkdir(exist_ok=True)
parsers={
'Python':lambda p:py_tree(p),
'JavaScript':lambda p:ts_tree(p,'js')[:2],
'TypeScript':lambda p:ts_tree(p,'ts')[:2],
'C':lambda p:clang_tree(p,False),
'C++':lambda p:clang_tree(p,True),
'Java':java_tree,
'Go':go_tree,
'Swift':swift_tree,
'Ruby':ruby_tree,
}

# lightweight lexical semantic counts
patterns={
'branch': re.compile(r'\b(if|else|switch|case|match|when|unless|elsif)\b'),
'loop': re.compile(r'\b(for|while|range|each|times)\b'),
'return': re.compile(r'\breturn\b'),
'decl': re.compile(r'\b(let|const|var|int|long|char|bool|boolean|String|func|def|function|static|auto)\b|:='),
'mutation': re.compile(r'(\+=|-=|\+\+|--|(?<![=!<>:])=(?!=))'),
'call': re.compile(r'\b[A-Za-z_][A-Za-z_0-9]*\s*\('),
}
# explicit type tokens/markers, intentionally syntax-surface not semantic type inference
type_patterns={
'Python':re.compile(r'(:\s*(int|bool|str|list\b)|->)'),
'JavaScript':re.compile(r'a^'),
'TypeScript':re.compile(r':\s*(number|string|boolean)|:\s*number\[\]|\)\s*:\s*'),
'C':re.compile(r'\b(int|char|void|const)\b'),
'C++':re.compile(r'\b(int|char|void|bool|long|auto|const)\b'),
'Java':re.compile(r'\b(int|long|char|boolean|String|void)\b|int\[\]'),
'Go':re.compile(r'\b(int|string|bool)\b|\[\]int'),
'Swift':re.compile(r'\b(Int|String|Bool)\b|\[Int\]|->'),
'Ruby':re.compile(r'a^'),
}

results=[]
for lang,code in corpora.items():
    path=ROOT/f"bench.{exts[lang]}"
    try:
        validators[lang](path); valid=True; verror=''
    except Exception as e:
        valid=False; verror=str(e)
    toks=lexical_tokens(lang,code); lex=transition_spectrum(toks)
    nodes,edges=parsers[lang](path); tm=tree_metrics(nodes,edges)
    tokenN=len(toks)
    row=dict(language=lang,valid=valid,token_count=tokenN,lex_vocab=lex['V'],lex_stable_rank=lex['stable_rank'],lex_participation=lex['participation'],lex_top3=lex['top3'])
    row.update(tm)
    for name,pat in patterns.items(): row[name+'_per100']=100*len(pat.findall(code))/tokenN
    row['type_surface_per100']=100*len(type_patterns[lang].findall(code))/tokenN
    row['ast_nodes_per_token']=tm['node_count']/tokenN
    row['validation_error']=verror
    results.append(row)

# normalize selected feature vector and compute pairwise distances
feat_names=['lex_stable_rank','lex_top3','ast_stable_rank','ast_top3','ast_nodes_per_token','max_depth','mean_branch','type_entropy','branch_per100','loop_per100','mutation_per100','type_surface_per100']
X=np.array([[r[f] for f in feat_names] for r in results],float)
mu=X.mean(0); sd=X.std(0); sd[sd==0]=1
Z=(X-mu)/sd
D=np.sqrt(((Z[:,None,:]-Z[None,:,:])**2).mean(axis=2))
langs=[r['language'] for r in results]
for i,r in enumerate(results):
    order=np.argsort(D[i])
    r['nearest']=[(langs[j],float(D[i,j])) for j in order if j!=i][:3]

out={'design':{'tasks':10,'languages':langs,'features':feat_names},'results':results,'distance_matrix':{'languages':langs,'values':D.tolist()}}
(ROOT/'results.json').write_text(json.dumps(out,indent=2))

# Print compact table
cols=['language','token_count','lex_stable_rank','lex_top3','ast_stable_rank','ast_top3','ast_nodes_per_token','max_depth','mean_branch','branch_per100','loop_per100','mutation_per100','type_surface_per100']
print('\t'.join(cols))
for r in results:
    vals=[]
    for c in cols:
        v=r[c]
        vals.append(f"{v:.3f}" if isinstance(v,float) else str(v))
    print('\t'.join(vals))
print('\nNearest neighbors in standardized structural feature space:')
for r in results: print(r['language'],r['nearest'])
print('\nValidation:',[(r['language'],r['valid']) for r in results])
