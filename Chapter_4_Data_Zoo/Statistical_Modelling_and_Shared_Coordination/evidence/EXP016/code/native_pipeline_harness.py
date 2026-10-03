#!/usr/bin/env python3
"""
INTERNAL_COORDINATION_016 — native-pipeline training harness.

Purpose
-------
Build the 18-pipeline Evidence Data Passport data plane pinned to Open Targets 26.06.
Within each native pipeline, fit/risk-route statistical experts first (Stat-MoE),
then export one calibrated channel state into a shared ganglion. Human clinical
outcome remains terminal and is joined only after the evidence snapshot is frozen.

This file is intentionally a training harness rather than a reported 18-pipeline
fit: the current chat runtime does not contain the 26.06 source-level parquet.
It is executable once `data_root` points to an Open Targets 26.06 output tree.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

RELEASE = "26.06"

PASSPORTS = [
    ("DP-GEN-01", "GWAS associations", "gwas_credible_sets", "evidence_gwas_credible_sets"),
    ("DP-GEN-02", "Gene Burden", "gene_burden", "evidence_gene_burden"),
    ("DP-GEN-03", "ClinVar", "eva", "evidence_eva"),
    ("DP-GEN-04", "Genomics England PanelApp", "genomics_england", "evidence_genomics_england"),
    ("DP-GEN-05", "Gene2Phenotype", "gene2phenotype", "evidence_gene2phenotype"),
    ("DP-GEN-06", "UniProt literature", "uniprot_literature", "evidence_uniprot_literature"),
    ("DP-GEN-07", "UniProt curated variants", "uniprot_variants", "evidence_uniprot_variants"),
    ("DP-GEN-08", "Orphanet", "orphanet", "evidence_orphanet"),
    ("DP-GEN-09", "ClinGen", "clingen", "evidence_clingen"),
    ("DP-SOM-01", "Cancer Gene Census", "cancer_gene_census", "evidence_cancer_gene_census"),
    ("DP-SOM-02", "IntOGen", "intogen", "evidence_intogen"),
    ("DP-PWY-01", "Cancer Biomarkers", "cancer_biomarkers", "evidence_cancer_biomarkers"),
    ("DP-PWY-02", "Systematic CRISPR screens", "crispr_screen", "evidence_crispr_screen"),
    ("DP-PWY-03", "Project Score / unified cancer CRISPR", "crispr", "evidence_crispr"),
    ("DP-PWY-04", "Reactome", "reactome", "evidence_reactome"),
    ("DP-LIT-01", "Europe PMC", "europepmc", "evidence_europepmc"),
    ("DP-RNA-01", "Expression Atlas", "expression_atlas", "evidence_expression_atlas"),
    ("DP-ANM-01", "IMPC / PhenoDigm", "impc", "evidence_impc"),
]

# Fields whose presence is useful for current-state / point-in-time construction.
PIPELINE_FIELDS: Dict[str, Sequence[str]] = {
    "gwas_credible_sets": ["targetId", "diseaseId", "score", "resourceScore", "studyLocusId", "curationDate", "publicationDate", "evidenceDate", "qualityControls"],
    "gene_burden": ["targetId", "diseaseId", "score", "resourceScore", "studyId", "publicationDate", "evidenceDate", "directionOnTrait", "directionOnTarget"],
    "eva": ["targetId", "diseaseId", "score", "confidence", "clinicalSignificances", "studyId", "releaseDate", "publicationDate", "evidenceDate", "directionOnTrait", "directionOnTarget"],
    "genomics_england": ["targetId", "diseaseId", "score", "confidence", "studyId", "cohortPhenotypes", "allelicRequirements", "publicationDate", "evidenceDate"],
    "gene2phenotype": ["targetId", "diseaseId", "score", "confidence", "studyId", "allelicRequirements", "variantFunctionalConsequenceId", "publicationDate", "evidenceDate", "directionOnTrait", "directionOnTarget"],
    "uniprot_literature": ["targetId", "diseaseId", "score", "confidence", "literature", "targetModulation", "publicationDate", "evidenceDate"],
    "uniprot_variants": ["targetId", "diseaseId", "score", "confidence", "variantId", "variantRsId", "targetModulation", "publicationDate", "evidenceDate"],
    "orphanet": ["targetId", "diseaseId", "score", "confidence", "publicationDate", "evidenceDate", "directionOnTrait", "directionOnTarget"],
    "clingen": ["targetId", "diseaseId", "score", "confidence", "publicationDate", "evidenceDate"],
    "cancer_gene_census": ["targetId", "diseaseId", "score", "resourceScore", "publicationDate", "evidenceDate", "directionOnTrait", "directionOnTarget"],
    "intogen": ["targetId", "diseaseId", "score", "resourceScore", "cohortId", "significantDriverMethods", "mutatedSamples", "publicationDate", "evidenceDate", "directionOnTrait", "directionOnTarget"],
    "cancer_biomarkers": ["targetId", "diseaseId", "score", "confidence", "drugResponse", "drugId", "biomarkerName", "biomarkers", "publicationDate", "evidenceDate"],
    "crispr_screen": ["targetId", "diseaseId", "score", "resourceScore", "studyId", "projectId", "cellType", "geneticBackground", "contrast", "log2FoldChangeValue", "publicationDate", "evidenceDate"],
    "crispr": ["targetId", "diseaseId", "score", "resourceScore", "diseaseCellLines", "publicationDate", "evidenceDate"],
    "reactome": ["targetId", "diseaseId", "score", "reactionId", "reactionName", "pathways", "targetModulation", "publicationDate", "evidenceDate"],
    "europepmc": ["targetId", "diseaseId", "score", "resourceScore", "publicationYear", "textMiningSentences", "literature", "publicationDate", "evidenceDate"],
    "expression_atlas": ["targetId", "diseaseId", "score", "resourceScore", "studyId", "biosamplesFromSource", "contrast", "log2FoldChangeValue", "log2FoldChangePercentileRank", "publicationDate", "evidenceDate"],
    "impc": ["targetId", "diseaseId", "score", "targetInModelMgiId", "publicationDate", "evidenceDate", "directionOnTrait", "directionOnTarget"],
}

STAT_EXPERTS = {
    "default": ["additive_calibration", "interaction_calibration", "empirical_bayes"],
    "gwas_credible_sets": ["locus_hierarchical", "study_replication", "empirical_bayes"],
    "gene_burden": ["burden_meta", "cohort_hierarchical", "empirical_bayes"],
    "eva": ["clinical_significance_ordinal", "review_conflict", "empirical_bayes"],
    "expression_atlas": ["effect_meta", "tissue_hierarchical", "empirical_bayes"],
    "crispr_screen": ["effect_meta", "celltype_hierarchical", "empirical_bayes"],
    "crispr": ["dependency_distribution", "tumour_hierarchical", "empirical_bayes"],
    "intogen": ["method_consensus", "cohort_hierarchical", "empirical_bayes"],
    "impc": ["phenotype_concordance", "transport_calibration", "empirical_bayes"],
    "europepmc": ["publication_count", "source_dependence", "time_locked_calibration"],
}

@dataclass(frozen=True)
class Passport:
    passport_id: str
    name: str
    datasource_id: str
    native_table: str


def registry() -> List[Passport]:
    return [Passport(*x) for x in PASSPORTS]


def validate_registry() -> None:
    rows = registry()
    assert len(rows) == 18, len(rows)
    assert len({x.passport_id for x in rows}) == 18
    assert len({x.datasource_id for x in rows}) == 18
    assert set(x.datasource_id for x in rows).issubset(PIPELINE_FIELDS)


def read_parquet_dir(path: Path, columns: Optional[Sequence[str]] = None):
    import pandas as pd
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_parquet(path, columns=list(columns) if columns else None)


def build_old_to_current_disease_map(disease_df):
    """Bridge older EFO IDs to 26.06 current IDs using disease.obsoleteTerms/XRefs.

    Existing 011-015 terminal cohort contains pre-26.06 EFO IDs. 26.06 replaced
    many disease IDs with Mondo IDs, so this bridge is mandatory before joining.
    """
    bridge: Dict[str, str] = {}
    for row in disease_df.itertuples(index=False):
        current = str(row.id)
        bridge[current] = current
        for field in ("obsoleteTerms", "obsoleteXRefs", "dbXRefs"):
            vals = getattr(row, field, None)
            if vals is None:
                continue
            if not isinstance(vals, (list, tuple, np.ndarray)):
                vals = [vals]
            for v in vals:
                if v is not None:
                    bridge[str(v)] = current
    return bridge


def load_datasource_associations(data_root: Path):
    cols = ["targetId", "diseaseId", "aggregationValue", "associationScore",
            "evidenceCount", "timeseries", "currentNovelty", "release"]
    df = read_parquet_dir(data_root / "association_by_datasource_direct", cols)
    return df[df["release"].astype(str).eq(RELEASE)].copy()


def build_18_score_matrix(data_root: Path, terminal_pairs):
    """Fast source-level first pass using 26.06 datasource association scores.

    This does NOT pretend associationScore is native raw evidence. It is only the
    source-level integration smoke test. Full precision work should switch each
    pipeline to its source-specific native evidence table.
    """
    import pandas as pd
    assoc = load_datasource_associations(data_root)
    wanted = {p.datasource_id: p.passport_id for p in registry()}
    assoc = assoc[assoc["aggregationValue"].isin(wanted)].copy()
    assoc["passport_id"] = assoc["aggregationValue"].map(wanted)
    score = assoc.pivot_table(index=["targetId", "diseaseId"], columns="passport_id",
                              values="associationScore", aggfunc="max")
    count = assoc.pivot_table(index=["targetId", "diseaseId"], columns="passport_id",
                              values="evidenceCount", aggfunc="sum")
    score.columns = [f"{c}__score" for c in score.columns]
    count.columns = [f"{c}__count" for c in count.columns]
    X = score.join(count, how="outer").reset_index()
    return terminal_pairs.merge(X, on=["targetId", "diseaseId"], how="left")


def time_lock_native_evidence(df, freeze_date, date_candidates=("evidenceDate", "publicationDate", "releaseDate", "curationDate")):
    import pandas as pd
    if freeze_date is None:
        return df
    freeze = pd.to_datetime(freeze_date)
    out = df.copy()
    found = False
    for c in date_candidates:
        if c in out.columns:
            dt = pd.to_datetime(out[c], errors="coerce")
            keep = dt.isna() | (dt <= freeze)
            out = out.loc[keep]
            found = True
    if not found:
        raise ValueError("No time field available for point-in-time lock")
    return out


def load_native_pipeline(data_root: Path, p: Passport, freeze_date=None):
    table_path = data_root / p.native_table
    df = read_parquet_dir(table_path)
    if "release" in df.columns:
        df = df[df["release"].astype(str).eq(RELEASE)].copy()
    df = time_lock_native_evidence(df, freeze_date)
    return df


def fnv1a32(text: str, salt: int = 0) -> int:
    h = (2166136261 ^ salt) & 0xFFFFFFFF
    for ch in str(text):
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return h


def target_split(target_id: str) -> str:
    z = fnv1a32(target_id) % 100
    return "train" if z < 70 else ("validation" if z < 85 else "test")


def candidate_experts(p: Passport) -> Sequence[str]:
    return STAT_EXPERTS.get(p.datasource_id, STAT_EXPERTS["default"])


def stat_moe_route(oof_predictions: np.ndarray, y: np.ndarray, sample_weight: np.ndarray, step: float = 0.02):
    """OOF probability-mixture routing for three experts.

    Returns simplex weights that minimise weighted Bernoulli log loss. This is the
    Experiment 015 rule: routing remains in statistics, below the shared ganglion.
    """
    if oof_predictions.shape[1] != 3:
        raise ValueError("This reference router expects exactly 3 expert predictions")
    best_w = np.array([0.0, 1.0, 0.0])
    best_loss = np.inf
    grid = np.arange(0.0, 1.0 + 1e-12, step)
    for w0 in grid:
        for w1 in grid:
            if w0 + w1 > 1.0 + 1e-12:
                continue
            w = np.array([w0, w1, 1.0 - w0 - w1])
            p = np.clip(oof_predictions @ w, 1e-7, 1 - 1e-7)
            loss = np.average(-(y*np.log(p) + (1-y)*np.log(1-p)), weights=sample_weight)
            if loss < best_loss:
                best_loss, best_w = float(loss), w.copy()
    return best_w, best_loss


def export_channel_state(passport_id: str, prediction: np.ndarray, uncertainty: np.ndarray,
                         availability: np.ndarray, novelty: Optional[np.ndarray] = None):
    state = {
        "passport_id": passport_id,
        "prediction": np.asarray(prediction, dtype=np.float32),
        "uncertainty": np.asarray(uncertainty, dtype=np.float32),
        "availability": np.asarray(availability, dtype=np.float32),
    }
    if novelty is not None:
        state["novelty"] = np.asarray(novelty, dtype=np.float32)
    return state


def ganglion_spec(n_pipelines: int = 18, state_dim: int = 16, ganglion_dim: int = 24):
    return {
        "n_pipelines": n_pipelines,
        "pipeline_state_dim": state_dim,
        "ganglion_dim": ganglion_dim,
        "aggregation": "availability-aware set aggregation within aligned evidence slice",
        "shared_update": "single shared matrix/operator; no expert routing inside ganglion",
        "onboarding": "freeze shared ganglion; train new pipeline Stat-MoE + channel interface first",
    }


def validate_data_root(data_root: Path) -> Dict[str, object]:
    missing = []
    present = []
    for p in registry():
        path = data_root / p.native_table
        (present if path.exists() else missing).append(p.native_table)
    for required in ("association_by_datasource_direct", "disease"):
        if not (data_root / required).exists():
            missing.append(required)
    return {"release": RELEASE, "present": present, "missing": missing,
            "ready_native": len(present), "required_native": 18}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, help="Open Targets 26.06 output root")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--print-registry", action="store_true")
    args = parser.parse_args()

    validate_registry()
    if args.print_registry or args.data_root is None:
        print(json.dumps([p.__dict__ | {"experts": list(candidate_experts(p)),
                                      "fields": list(PIPELINE_FIELDS[p.datasource_id])}
                          for p in registry()], indent=2))
    if args.data_root is not None:
        status = validate_data_root(args.data_root)
        print(json.dumps(status, indent=2))
        if args.validate_only and status["missing"]:
            raise SystemExit(2)
    print(json.dumps(ganglion_spec(), indent=2))


if __name__ == "__main__":
    main()

# -----------------------------------------------------------------------------
# Shared ganglion implementation used after the 18 within-pipeline Stat-MoEs.
# -----------------------------------------------------------------------------

def _torch():
    import torch
    from torch import nn
    return torch, nn


def make_ganglion_model(n_pipelines: int = 18, state_features: int = 4,
                        interface_dim: int = 24, ganglion_dim: int = 24):
    torch, nn = _torch()

    class NativePipelineGanglion(nn.Module):
        def __init__(self):
            super().__init__()
            self.interfaces = nn.ModuleList([
                nn.Sequential(nn.Linear(state_features, interface_dim), nn.Tanh())
                for _ in range(n_pipelines)
            ])
            self.ganglion = nn.Sequential(
                nn.Linear(interface_dim, ganglion_dim),
                nn.Tanh(),
            )
            self.outcome_head = nn.Linear(ganglion_dim, 1)

        def forward(self, pipeline_state, availability):
            # pipeline_state: [B, P, F]; availability: [B, P]
            parts = []
            for i, interface in enumerate(self.interfaces):
                parts.append(interface(pipeline_state[:, i, :]))
            h = torch.stack(parts, dim=1)  # [B,P,D]
            mask = availability.unsqueeze(-1).to(h.dtype)
            denom = mask.sum(dim=1).clamp_min(1.0)
            evidence_set = (h * mask).sum(dim=1) / denom
            reality_state = self.ganglion(evidence_set)
            logit = self.outcome_head(reality_state).squeeze(-1)
            return logit, reality_state

        def freeze_ganglion(self):
            for p in self.ganglion.parameters():
                p.requires_grad = False
            for p in self.outcome_head.parameters():
                p.requires_grad = False

        def freeze_existing_interfaces(self, except_index: int):
            for i, module in enumerate(self.interfaces):
                if i != except_index:
                    for p in module.parameters():
                        p.requires_grad = False

    return NativePipelineGanglion()


def build_state_tensor(channel_states: Sequence[dict], passport_order: Sequence[str]):
    """Assemble [N,18,4] = prediction, uncertainty, novelty, availability."""
    by_id = {s["passport_id"]: s for s in channel_states}
    n = len(next(iter(by_id.values()))["prediction"])
    X = np.zeros((n, len(passport_order), 4), dtype=np.float32)
    A = np.zeros((n, len(passport_order)), dtype=np.float32)
    for j, pid in enumerate(passport_order):
        s = by_id[pid]
        X[:, j, 0] = s["prediction"]
        X[:, j, 1] = s["uncertainty"]
        X[:, j, 2] = s.get("novelty", np.zeros(n, dtype=np.float32))
        X[:, j, 3] = s["availability"]
        A[:, j] = s["availability"]
    return X, A


def fit_ganglion(model, X, A, y, sample_weight=None, epochs: int = 250,
                  lr: float = 2e-3, seed: int = 20261002):
    torch, _ = _torch()
    torch.manual_seed(seed)
    X = torch.as_tensor(X, dtype=torch.float32)
    A = torch.as_tensor(A, dtype=torch.float32)
    y = torch.as_tensor(y, dtype=torch.float32)
    w = torch.ones_like(y) if sample_weight is None else torch.as_tensor(sample_weight, dtype=torch.float32)
    opt = torch.optim.Adam([p for p in model.parameters() if p.requires_grad], lr=lr)
    for _ in range(epochs):
        opt.zero_grad()
        logit, _ = model(X, A)
        per = torch.nn.functional.binary_cross_entropy_with_logits(logit, y, reduction="none")
        loss = (per * w).sum() / w.sum().clamp_min(1.0)
        loss.backward()
        opt.step()
    return model


def frozen_ganglion_onboarding(model, new_pipeline_index: int, X, A, y,
                                sample_weight=None, epochs: int = 150, lr: float = 2e-3):
    """Experiment interface: add one native pipeline without rewriting shared reality."""
    model.freeze_ganglion()
    model.freeze_existing_interfaces(except_index=new_pipeline_index)
    return fit_ganglion(model, X, A, y, sample_weight=sample_weight, epochs=epochs, lr=lr)
