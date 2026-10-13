# Plasmid Sequence Verification Agent

Compare an expected plasmid DNA sequence with an observed consensus sequence. A standalone browser interface and a standard-library Python script provide deterministic, **ungapped** comparison. The repository also retains an older numeric-metric audit CLI and FastAPI service; those modes do **not** inspect nucleotide sequences.

## Browser application

Open `web/index.html` in a current browser, or use the repository's configured GitHub Pages deployment when available. Paste raw DNA or a **single-record FASTA** in both panels (or choose local files), optionally enable **exact circular rotations**, and select **Compare sequences**. Review the outcome, mismatched reference positions, orientation, and identity percentage; export the report as JSON.

The browser processes sequences locally in JavaScript without a server, external libraries, authentication, file uploads, or persistent storage.

## Python sequence comparison

Python 3.9 or newer is supported. From the repository root:

```bash
python sequence_verification.py --reference expected.fasta --observed observed.fasta
python sequence_verification.py --reference expected.fasta --observed observed.fasta --circular
```

The command emits JSON. Exit status: `0` for an exact match, `2` for a mismatch or unequal length, `1` for invalid/unreadable inputs. The sequence comparator requires **no third-party packages**.

### Scope and limitations

- Accepts raw DNA text or one FASTA record per input, limited to 200,000 `A/C/G/T/N` bases per sequence. `N` is matched literally, not as a wildcard.
- Compares corresponding bases with optional reverse-complement orientation. Substitution positions are 1-based reference coordinates; JSON lists at most 500 differences while preserving their total count.
- Supports **exact** circular rotations, including reverse complements. For non-exact rotated plasmids, reported differences are at zero offset and must not be interpreted as a variant alignment.
- Unequal lengths are reported without assigning indel events. This is **not** a gapped aligner, read assembler, chromatogram interpreter, coverage/Q-score analyzer, junction/ORF annotator, or laboratory validation system.

## Existing metric-audit workflow (retained)

The older numeric workflow classifies `primary_metric`, `secondary_metric`, a critical flag, and a text descriptor. These generic thresholds are not plasmid sequence quality metrics and do not independently establish biological construct identity.

```bash
python -m pip install -e ".[api,dev]"
python cli.py audit --task-id TASK-001 --target TARGET-01 --primary 28.5 --secondary 14.2 --status DISCORDANT
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
```

The API exposes `GET /health`, `GET /metrics`, `POST /api/audit`, `POST /api/chat`, and `GET /api/audit/logs`. An alternate CLI is available through `plasmid-sequence-verification-engine` (also `plasmid-sequence-verification-agent`). Its metric-audit model is distinct from the new sequence comparator.

For containers, run `docker build -t plasmid-check .` and `docker run -p 8000:8000 -e AUDIT_SECRET_KEY=... plasmid-check`, or use `docker compose up --build`. Keep service endpoints restricted to trusted networks; **the API does not implement authentication**.

## Testing

```bash
python -m pip install -e ".[api,dev]"
python -m pytest -q
node --test web/tests/sequence.test.cjs
```

Node 22 is used in CI for browser-logic tests. CI also checks Python 3.10–3.13 and Python syntax. Python dependencies for the legacy API are declared as optional extras; the browser app has no build step.

## Privacy, security, and limitations

The browser app neither transmits nor retains entered DNA. In contrast, the optional server processes inputs in memory, exposes audit metadata over HTTP, and does not provide access control; do not deploy it openly or submit sensitive identifiers. The legacy regex guard recognizes only selected identifier patterns and should **not** be treated as comprehensive PHI de-identification. Its HMAC-SHA256 audit chain is tamper-evident within the running process; logs and any session-generated key are not persisted.

## Technology and license

Python (standard library, Pydantic 2 for the legacy agent, optional FastAPI/Uvicorn), vanilla HTML/CSS/JavaScript, GitHub Actions, and Docker. Intended for modern browsers supporting `File.text()`, `Blob`, and `URL.createObjectURL()`. Licensed under [MIT](LICENSE).
