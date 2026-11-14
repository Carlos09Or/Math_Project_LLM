"""Genera assets/data/benchmark2026.js con datos AGREGADOS del benchmark 2026.

    python tools/build_benchmark2026_data.py --src ../benchmark

No incluye enunciados, trabajos de estudiantes ni respuestas de los modelos: solo conteos por
modelo, tarea, competencia y dificultad, más lo que informó Ollama de cada modelo. El dataset de
180 ítems no se publica (ver benchmark2026/README.md).
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (id, etiqueta, familia, patrón de carpeta de corrida)
MODELS = [
    ("qwen3-0.6b-q4_K_M", "Qwen3-0.6B Q4_K_M", "Qwen3", "T155017Z"),
    ("qwen3-0.6b-q8_0", "Qwen3-0.6B Q8_0", "Qwen3", "T155702Z"),
    ("qwen3-0.6b-fp16", "Qwen3-0.6B FP16", "Qwen3", "T155748Z"),
    ("qwen3-1.7b-q4_K_M", "Qwen3-1.7B Q4_K_M", "Qwen3", None),
    ("gemma3-1b-q4_K_M", "Gemma 3 1B Q4_K_M", "Gemma", None),
    ("smollm3-3b-q4_K_M", "SmolLM3 3B Q4_K_M", "SmolLM3", None),
    ("phi4-mini-3.8b-q4_K_M", "Phi-4-mini 3.8B Q4_K_M", "Phi", None),
]
SKILLS = [
    ("NAT-READ-WRITE", "Leer y escribir números"), ("NAT-SKIP-COUNT", "Conteo por intervalos"),
    ("NAT-ORDER-COMPARE", "Comparar números"), ("NAT-PLACE-VALUE", "Valor posicional"), ("ADD-4DIG", "Suma"),
    ("ADD-PROPERTIES", "Propiedades de la suma"), ("SUB-10K", "Resta"), ("SUB-CHECK-REINTEGRATIVE", "Comprobar una resta"),
    ("MUL-TABLES-1-12", "Tablas de multiplicar"), ("MUL-POW10", "Multiplicar por 10, 100, 1 000"),
    ("DIV-EXACT", "División exacta"), ("DIV-INEXACT", "División con residuo"), ("DIV-POW10", "Dividir entre 10, 100, 1 000"),
    ("DIV-CHECK-REINTEGRATIVE", "Comprobar una división"), ("COMBINED-OPS", "Operaciones combinadas"), ("ORD-1-50", "Ordinales"),
    ("FRAC-REPR-CLASSIFY", "Fracciones propias o impropias"), ("FRAC-COMPARE-HOMOG", "Comparar fracciones"),
    ("FRAC-ADDSUB-HOMOG", "Sumar y restar fracciones"),
]
TASK = {"problem_solving": "A", "error_diagnosis": "B", "hint_generation": "C"}
DIFF = {"basic": "basica", "intermediate": "intermedia", "advanced_in_grade": "avanzada"}


def find_run(src: Path, mid: str, stamp: str | None) -> Path:
    pats = sorted(glob.glob(str(src / "results" / "runs" / f"*__{mid}__*{stamp or ''}")))
    if not pats:
        raise SystemExit(f"no hay corrida para {mid}")
    return Path(pats[-1])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=ROOT / "assets" / "data" / "benchmark2026.js")
    args = ap.parse_args()
    src = args.src

    models, per = [], {}
    for mid, label, fam, stamp in MODELS:
        d = find_run(src, mid, stamp)
        man = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
        mo, inf = man["model"], man["inference_summary"]
        ps = {p["name"]: p for p in mo["ps_after_run"]}.get(mo["ollama_name"], {})
        models.append({
            "id": mid, "label": label, "family": fam, "params": mo["details"].get("parameter_size"),
            "quant": mo["reported_quantization"], "digest": mo["digest"][:12], "frozen": man["benchmark_frozen"],
            "vram_mb": round(ps.get("size_vram", 0) / 1e6, 1) if ps else None,
            "fully_on_gpu": bool(ps) and ps.get("size") == ps.get("size_vram"),
            "tok_s": inf["tokens_per_second_median"], "wall_ms": inf["wall_ms"]["median"], "ttft_ms": inf["ttft_client_ms_median"],
            "eval_tokens": inf["eval_tokens_total"], "n_ok": inf["n_ok"], "n_error": inf["n_error"],
            "think_accepted": mo.get("think_accepted_by_ollama"),
        })
        per[mid] = [json.loads(l) for l in open(d / "responses.jsonl", encoding="utf-8") if l.strip()]

    tasks = {t: {"n": 60, "outcomes": {}} for t in "ABC"}
    skills = {s: {"name": n, "A": {}, "B": {}, "C": {}} for s, n in SKILLS}
    diff = {m[0]: defaultdict(lambda: [0, 0]) for m in MODELS}
    verdict, cats = {}, {}
    cat_expected = Counter()
    labeled = {}
    for mid, recs in per.items():
        ok = [r for r in recs if r["status"] == "ok"]
        for t in "ABC":
            rs = [r for r in ok if TASK[r["task"]] == t]
            tasks[t]["outcomes"][mid] = dict(Counter(r["scoring"]["status"] for r in rs))
        for r in ok:
            t, s = TASK[r["task"]], r["skill_id"]
            sc = r["scoring"]
            good = (sc["status"] == "correct") if t == "A" else (bool(sc.get("verdict_match")) if t == "B" else sc["status"] == "leak")
            cell = skills[s][t].setdefault(mid, [0, 0])
            cell[0] += int(good)
            cell[1] += 1
            if t == "A":
                d = diff[mid][DIFF[r["difficulty"]]]
                d[0] += int(sc["status"] == "correct")
                d[1] += 1
        A = [r for r in ok if r["task"] == "problem_solving"]
        labeled[mid] = [sum(1 for r in A if "sin_linea_respuesta_final" not in r["scoring"].get("notes", [])), len(A)]
        B = [r for r in ok if r["task"] == "error_diagnosis"]
        err = [r for r in B if r["scoring"]["expected_verdict"] == "incorrect"]
        ctl = [r for r in B if r["scoring"]["expected_verdict"] == "correct"]
        verdict[mid] = {
            "err_n": len(err), "err_said_incorrect": sum(1 for r in err if r["scoring"].get("verdict") == "incorrect"),
            "err_said_correct": sum(1 for r in err if r["scoring"].get("verdict") == "correct"),
            "ctrl_n": len(ctl), "ctrl_said_correct": sum(1 for r in ctl if r["scoring"].get("verdict") == "correct"),
            "err_verdict_and_category": sum(1 for r in err if r["scoring"]["status"] == "correct"),
        }
        cats[mid] = dict(Counter((r["scoring"].get("category") or "sin_categoria") for r in err))
        for r in err:
            cat_expected[r["scoring"]["expected_category"]] += 1 if mid == MODELS[0][0] else 0

    coverage = []
    with open(src / "curriculum" / "coverage_report_v1.csv", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if int(r["n_items"]):
                coverage.append({"skill": r["skill_id"], "name": skills[r["skill_id"]]["name"], "n": int(r["n_items"]), "A": int(r["problem_solving"]),
                                 "B": int(r["error_diagnosis"]), "C": int(r["hint_generation"]), "families": int(r["families"]),
                                 "controls": int(r["diagnosis_controls"]), "zero": int(r["items_involving_zero"])})
    val = json.loads((src / "results" / "validation_v1.json").read_text(encoding="utf-8"))
    data = {
        "generated": "2026-11-14", "n_items": val["n_items"], "n_families": val["n_families"], "by_difficulty": val["by_difficulty"],
        "controls": val["diagnosis_controls"], "zero_items": val["items_involving_zero"], "max_skill_share": val["max_skill_share"],
        "validation": {"result": val["result"], "errors": len(val["errors"]), "warnings": len(val["warnings"])},
        "models": models, "tasks": tasks, "skills": [{"id": s, **skills[s]} for s, _ in SKILLS], "difficulty": {m: dict(d) for m, d in diff.items()},
        "verdict": verdict, "categories_said": cats, "categories_expected": dict(cat_expected), "labeled_final": labeled, "coverage": coverage,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("window.BENCH2026 = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"escrito {args.out} ({args.out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
