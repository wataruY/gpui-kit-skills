# GPUI Kit skills

Skills-only derivative of [GPUI Kit](https://github.com/longbridge/gpui-kit).
Imported from `skills/` at commit `611b55e331170ca375214d580b6c5409db858f83`.
The framework, crates, website implementation, and unrelated tooling are not included.
This is an independent derivative repository, not a full GitHub network fork.

## Skills

- `skills/gpui-kit`: Rust API, application structure, and interaction/testing guidance.
- `skills/gpui-kit-design-guides`: native desktop product and interaction design guidance.

APM can install this bundle using `wataruY/gpui-kit-skills#<commit>`.

## Local extensions

The existing two skills retain their names. `gpui-kit` now routes repeated
API/trait/receiver errors to lock-matching local source lookup and relative-skill
reference resolution; native verification covers failure evidence and a small
PNG/window-dimension checker. `gpui-kit-design-guides` adds interaction-transition
checks. Upstream coding/design guide snapshots are left verbatim; additions live
in separate references. Helpers are read-only and never launch GUI input.

Python 3.11+ is required for helper TOML parsing. Test without Cargo, network or GUI:

```sh
python3 -m unittest discover -s skills/gpui-kit/scripts -p 'test_*.py' -v
```

The API helper inspects exact lock-version crates.io cache sources, not Cargo's
complete graph, Rust type resolution or macro expansion. The capture helper
checks PNG header dimensions against supplied measured bounds, not visual quality.

## Provenance and licensing

`UPSTREAM.json` records the imported revision and hashes of every baseline skill file.
Original copyright and licenses are retained in `LICENSE-APACHE` and `LICENSE-DOCS.md`.
Documentation copied from GPUI Kit keeps attribution and source links. The additional
CC BY 4.0 offer described in LICENSE-DOCS.md applies only to its stated documentation
scope; software and code examples retain Apache-2.0 terms.

For upstream updates, compare `skills/` at the recorded commit with the desired
upstream revision, apply the upstream changes while preserving local additions,
validate both skills and helper tests, and update the provenance record. Keep
verbatim upstream guide snapshots distinct from local extension references.
