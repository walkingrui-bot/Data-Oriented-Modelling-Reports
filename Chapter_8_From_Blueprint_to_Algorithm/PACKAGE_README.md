# Using the publication package

Start with `From_Blueprint_to_Algorithm_EN_v1.0_20261006.docx` for the illustrated English report, or `REPORT_EN.md` for the same report in Markdown. Both contain nine figures and ten numbered tables. The report is the synthesis and conclusion of the current explanatory sequence; future evidence will be maintained in the corresponding topical chapters.

`EVIDENCE_INDEX.md` maps the experiments to their records. The `evidence` directory preserves the recovered reports, numeric records, code, synthetic-task checkpoints, original figures and table data. `Evidence_Manifest.csv` records source and published hashes; `SOURCE_AVAILABILITY.md` explains the available records and the limits of verification. These materials do not include an external raw dataset.

The complete publication archive contains a snapshot of this chapter, excluding the downloadable ZIP files themselves. Links to other chapters and downloads require the [online chapter](https://github.com/walkingrui-bot/Data-Oriented-Modelling-Reports/tree/main/Chapter_8_From_Blueprint_to_Algorithm). The separate evidence archive contains the evidence directory, its indexes, source-availability note and its own `SHA256SUMS.txt`.

To verify the complete publication snapshot, run `sha256sum -c SHA256SUMS.txt` from the extracted chapter directory. For the separate evidence archive, run the same command from its extracted directory. ZIP-file hashes are published in `releases/SHA256SUMS.txt` in the repository.
