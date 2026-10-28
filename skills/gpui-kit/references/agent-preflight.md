# Agent preflight (fork extension)

Avoid fixing the same missing method or reference path by guesswork. These helpers only read local files; they do not compile, download, modify Cargo, launch an app, or repair code.

## Missing skill reference

Resolve a Markdown link relative to the file **containing the link**, not the skill root or project cwd:

```sh
python3 <gpui-kit-skill-dir>/scripts/resolve_ref.py \
  --skill .agents/skills/impeccable \
  --from reference/new-work.md degraded/documenter.md
```

This resolves to `reference/degraded/documenter.md`. If missing, list actual matches instead of inventing another prefix:

```sh
python3 <gpui-kit-skill-dir>/scripts/resolve_ref.py \
  --skill .agents/skills/impeccable --find documenter.md
```

The resolver checks file existence and skill-root containment, not Markdown anchors. It refuses external URLs and references escaping the skill; handle an intentional external reference separately. Do not edit generated/deployed skill copies to compensate for a mistaken reader path.

## GPUI method or variant

Read the relevant GPUI guides as usual. Before expanding a new API pattern, identify the receiver type, required trait, argument list, and retained owner. Inspect the lock-matching local source:

```sh
python3 <gpui-kit-skill-dir>/scripts/api_lookup.py --project . \
  --crate gpui-pre --symbol role
python3 <gpui-kit-skill-dir>/scripts/api_lookup.py --project . \
  --crate gpui-pre --symbol focus_handle
python3 <gpui-kit-skill-dir>/scripts/api_lookup.py --project . \
  --crate gpui-base --symbol set_placeholder
python3 <gpui-kit-skill-dir>/scripts/api_lookup.py --project . \
  --crate gpui-component --symbol IconName
```

The output includes version, source location, nearby textual owner, and bounded excerpts. Read the enclosing implementation when the receiver constraint matters. [Known contracts](api-contract-pitfalls.md) lists demonstrated pitfalls for the observed version only.

This is **text lookup of Cargo.lock-matching crates.io cache sources**, not Cargo's resolved dependency graph, Rust name resolution, macro expansion, or a compile check. Multiple versions require `--version`; duplicate caches, git/path sources, and unavailable sources fail explicitly. A vendored/source-replaced or patched build needs its actual source checked separately. No result means no textual candidate, not proof the API is absent.

For example, the observed `IconName` is populated through an assets macro. Searching the component crate for `Trash2` alone returns no match even though the variant is usable. Follow the macro/catalog owner rather than synthesizing a similarly named variant or treating an empty lookup as absence.

For E0599 distinguish a missing trait from an incompatible receiver or genuinely unavailable API. In particular, a larger import list cannot make a stateful-only method work on an ordinary `Div`. Preserve stable domain-based IDs when making an element stateful. For test modules, check imports again: a parent module's trait imports need not be in scope.

After changing one pattern, run the existing focused `cargo check` or test target before repeating it across a feature. A successful lookup is not completion evidence. If the same diagnostic remains, compare the exact receiver/import/signature; do not broaden the patch or keep retrying unchanged commands.

Helper contract tests: `python3 -m unittest discover -s <gpui-kit-skill-dir>/scripts -p 'test_*.py'`. These use temporary fixtures and do not run Cargo or GUI input.
