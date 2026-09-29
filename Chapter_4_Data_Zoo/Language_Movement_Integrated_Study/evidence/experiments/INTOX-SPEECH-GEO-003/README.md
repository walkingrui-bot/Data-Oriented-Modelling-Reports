# INTOX-SPEECH-GEO-003 — Acoustic temporal geometry

The analyzed object comprises 103 KAISD mel-spectrogram segments (52 sober, 51 intoxicated) from two source recordings, each 128 × 345. The directory preserves pooled and segment-level geometry, resampling summaries, timing-control results and the preprocessing specification. Figures 2–5 are in `../../../figures/`.

`recompute_speech_geometry_template.py` implements core pooled and segment-level geometry from source tensors supplied locally. The full executable scope, input format and recorded control settings are in the publication reproduction guide. The original tensors remain at their source distribution channel.

The segment-table label “Movement-band breadth /128” denotes an effective band count out of 128. Its values, 121.74 and 116.98, are counts rather than already normalized fractions.
