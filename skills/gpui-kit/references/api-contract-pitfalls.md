# Observed GPUI 0.8.0 pitfalls

These observations apply to `gpui-kit`, `gpui-base`, and `gpui-component` 0.8.0 with `gpui-pre` 0.3.9 in apm-editor2. Recheck the resolved source for another version; these are not automatic rewrite rules.

| Symptom | What to inspect |
| --- | --- |
| `Div.role(...)` gives E0599 | `role` is on `StatefulInteractiveElement`. `div().id(stable_id)` yields a stateful element; the trait must also be available. Do not insert arbitrary index/random IDs or remove accessibility to silence the compiler. |
| `focus_handle` missing or wrong arguments | `Focusable::focus_handle` takes `&App` in gpui-pre. Recheck the concrete type and imports inside the test module; do not copy an unrelated inherent method's argument list. |
| `Input.placeholder(...)` missing | Placeholder belongs to retained input state in the observed API. `set_placeholder` needs window/context parameters. Inspect the constructor/state setter, not just the rendered Input. |
| `font_semibold`, `when`, `child`, window dialog methods missing | Inspect `StyledExt`, `FluentBuilder`, `ParentElement`, `WindowExt` respectively. Rustc's suggested trait is evidence; similarly named replacement methods may change behavior. |
| `IconName::Trash` missing | Inspect the published enum/variant source (the observed variant is `Trash2`). Do not infer icon names from web examples. |

Inspect the exact owner and parameters with `scripts/api_lookup.py`. A textual search does not prove which trait or implementation applies, especially for macro-generated size helpers or generic state types. Use the compiler to check the small resulting pattern.
