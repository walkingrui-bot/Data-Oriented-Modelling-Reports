# Publishing the English Edition

The package contains both phases of the research, 39 experiment folders, 35 hypothesis records, and 512 original source artifacts.

| Publication item | Prepared text |
| --- | --- |
| Repository name | `biosphere-3-public-reports` |
| Title | Biosphere 3 — Public Reports |
| Description | Independent personal-interest research on generative-function formation, observation, and control. |
| First release | `v0.1.0` — both research phases |
| Language | English |
| Project | Independent, self-directed personal research; conducted without academic supervision |
| Contact | walkingrui@gmail.com |

## Put the work online

1. Create the GitHub repository and add the extracted package contents, with `README.md` at the repository root.
2. Add the preferred author name and actual repository URL to `CITATION.md` and `PROJECT_INFORMATION.md`.
3. Commit the snapshot and create tag `v0.1.0`. Use `RELEASE_NOTES.md` as the release description.
4. Attach the two English DOCX files and the complete package ZIP to the release. Share the release URL.

The repository presents the findings as readable Markdown. DOCX files provide downloadable editions. Each experiment folder contains its method, results, interpretation, and direct evidence links. Keep the compressed evidence in its archived form.

## Files included for publication

| File or folder | Purpose |
| --- | --- |
| `README.md` | Main conclusion, hypothesis overview, all 39 experiment entries, and reading links |
| `PROJECT_INFORMATION.md` | Independent personal-interest project description |
| `report_text/`, `reports/` | Two English findings documents |
| `experiments/` | 39 experiment dossiers |
| `evidence/`, `source/` | Original experimental materials |
| `CITATION.md` | Citation title, version, and experiment IDs |
| `CHANGELOG.md`, `RELEASE_NOTES.md` | Release history and ready-to-publish description |
| `CONTRIBUTING.md` | Discussion and replication entry point |

## Future releases

Record new findings in `CHANGELOG.md` and keep experiment IDs stable. For an edited snapshot, refresh the file index and check the evidence links:

```bash
python audit/recalculate.py
python audit/recalculate_phase2.py
python scripts/refresh_manifest.py
python scripts/verify_release.py
```

A preferred reuse license can be added when chosen. CC BY 4.0 is one option for author-created text and figures; code and source materials keep their applicable terms. A structured `CITATION.cff` and a Zenodo DOI can be added after the author name and public URL are set.

Useful references: [GitHub releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository), [citation files](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), [Zenodo and GitHub](https://help.zenodo.org/docs/github/).
