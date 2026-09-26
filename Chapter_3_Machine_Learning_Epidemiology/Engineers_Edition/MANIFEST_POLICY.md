# Integrity records

`FILE_MANIFEST.csv` records each payload file, its byte length, SHA-256 digest,
and source category. It excludes itself and `CHECKSUMS.sha256` to avoid a
self-referential digest. `CHECKSUMS.sha256` covers the payload and the manifest;
it excludes only itself. Paths are relative to the release root.

The original six supplied files and all 229 expanded cloud-archive members are
preserved byte for byte. Source-order table CSVs are transcriptions; the English
report, navigation, editorial checks, and attributed presentation figures are
derived artifacts. Referenced local companion records are listed in
`LOCAL_SOURCE_MAP.csv`; they are not payload files.

From the unpacked release root, use `sha256sum -c CHECKSUMS.sha256` on systems
providing that command. Numerical recalculation is documented in `README.md`.
