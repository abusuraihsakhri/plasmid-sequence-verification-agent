"""Deterministic ungapped comparison of a reference plasmid and observed consensus DNA.

This is not a read assembler, indel aligner, or clinical validation pipeline.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

MAX_BASES = 200_000
MAX_REPORTED_MISMATCHES = 500
COMPLEMENT = str.maketrans("ACGTN", "TGCAN")


def parse_sequence(text: str) -> str:
    """Accept raw DNA or exactly one FASTA record; N is literal, not a wildcard."""
    if not isinstance(text, str):
        raise ValueError("Sequence input must be text")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("Sequence is empty")
    if lines[0].startswith(">"):
        if len(lines[0]) == 1:
            raise ValueError("FASTA header must contain an identifier")
        if any(line.startswith(">") for line in lines[1:]):
            raise ValueError("Only one FASTA record is supported")
        lines = lines[1:]
    elif any(line.startswith(">") for line in lines):
        raise ValueError("FASTA header must be the first line")
    seq = "".join("".join(line.split()) for line in lines).upper()
    if not seq:
        raise ValueError("Sequence is empty")
    if len(seq) > MAX_BASES:
        raise ValueError(f"Sequence exceeds {MAX_BASES} bases")
    invalid = set(seq) - set("ACGTN")
    if invalid:
        raise ValueError(f"Unsupported DNA symbols: {''.join(sorted(invalid))}. Allowed: A, C, G, T, N")
    return seq


def reverse_complement(seq: str) -> str:
    return seq.translate(COMPLEMENT)[::-1]


def verify_sequences(reference_text: str, observed_text: str, *, circular: bool = False) -> dict:
    reference, observed = parse_sequence(reference_text), parse_sequence(observed_text)
    result = {
        "reference_length": len(reference), "observed_length": len(observed),
        "status": "LENGTH_MISMATCH", "orientation": None, "rotation_offset": None,
        "mismatch_count": None, "identity_percent": None,
        "mismatches": [], "mismatches_truncated": False,
        "method": "Ungapped exact-base comparison (N is not a wildcard)",
        "note": "Different lengths: insertions/deletions cannot be classified without gapped alignment.",
    }
    if len(reference) != len(observed):
        return result
    reverse = reverse_complement(observed)
    if reference == observed or reference == reverse:
        result.update(status="MATCH",
                      orientation="forward" if reference == observed else "reverse_complement",
                      rotation_offset=0, mismatch_count=0, identity_percent=100.0,
                      note="Exact match.")
        return result
    if circular:
        doubled = reference + reference[:-1]
        fwd_offset, rev_offset = doubled.find(observed), doubled.find(reverse)
        if fwd_offset >= 0 or rev_offset >= 0:
            result.update(status="MATCH",
                          orientation="forward" if fwd_offset >= 0 else "reverse_complement",
                          rotation_offset=fwd_offset if fwd_offset >= 0 else rev_offset,
                          mismatch_count=0, identity_percent=100.0,
                          note="Exact match after circular rotation.")
            return result
    direct_count = sum(a != b for a, b in zip(reference, observed))
    reverse_count = sum(a != b for a, b in zip(reference, reverse))
    use_reverse = reverse_count < direct_count
    aligned = reverse if use_reverse else observed
    count = reverse_count if use_reverse else direct_count
    differences = []
    for i, (a, b) in enumerate(zip(reference, aligned), 1):
        if a != b and len(differences) < MAX_REPORTED_MISMATCHES:
            differences.append({"position": i, "reference": a, "observed": b})
    result.update(status="MISMATCH",
                  orientation="reverse_complement" if use_reverse else "forward",
                  rotation_offset=0, mismatch_count=count,
                  identity_percent=round((len(reference) - count) * 100 / len(reference), 4),
                  mismatches=differences, mismatches_truncated=count > len(differences),
                  note=("Differences are relative to zero-offset coordinates; non-exact circular "
                        "rotations are not aligned." if circular else "Ungapped coordinate comparison."))
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Compare DNA consensus sequences (raw/FASTA)")
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--observed", type=Path, required=True)
    parser.add_argument("--circular", action="store_true", help="Accept exact circular rotations")
    args = parser.parse_args(argv)
    try:
        for path in (args.reference, args.observed):
            if path.stat().st_size > MAX_BASES * 4 + 8192:
                raise ValueError(f"File too large: {path}")
        report = verify_sequences(args.reference.read_text(encoding="utf-8-sig"),
                                  args.observed.read_text(encoding="utf-8-sig"),
                                  circular=args.circular)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.exit(1, f"Input error: {exc}\n")
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "MATCH" else 2


if __name__ == "__main__":
    raise SystemExit(main())
