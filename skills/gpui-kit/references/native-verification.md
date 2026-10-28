# Native verification (fork extension)

Use this when real-window waits fail or captures are prepared for review. It is
an observation contract, not permission to automate a user's active desktop.

## Diagnose one failed run

Keep the existing platform isolation harness. On Linux, automated input must use
a private display and D-Bus session, verified before launch/input. If an existing
`isolated-gui-test` harness is present, use its launcher and `require_isolation()`;
do not recreate or bypass the guard. Without a verified isolated input capability,
report the obstruction and do not fall back to the shared desktop.

Give each wait an expected state/control name. On failure, retain the predicate,
elapsed time, last observed state, application PID/exit status, current focus,
matching control role/name/enabled state, bounds, and a screenshot. Record the
binary hash and test case so a later log read does not have to reconstruct which
application ran. Re-query accessibility after state changes; indexes are snapshots.

Distinguish process/loader exit, missing accessibility service, target not found,
off-screen target, incorrect focus/context, and actual owner/state mismatch.
Do not turn all of them into a longer sleep or an automatic rerun. A focused
control does not prove a command worked; inspect the resulting state or saved data.

## Capture the window that actually exists

Resize through the private window connection, then measure the **current window**
position and size after layout. Use those bounds to capture it, not a hard-coded
root crop at `(0, 0)`. Ensure the private display can contain the requested window.
Separate logical units from physical image pixels at non-default display scales.

Two observed invalid cases must be rejected before visual review:

- a 1100×760 window inside a 1440×960 root screenshot with desktop padding;
- a 1440×960 window cut down to a 1100×760 crop.

Check the saved PNG against **measured physical window bounds**, for example:

```sh
python3 <gpui-kit-skill-dir>/scripts/check_capture.py capture.png --width 1100 --height 760
```

This helper checks PNG header dimensions only. It does not capture a window,
verify that supplied bounds were measured, inspect content, prove selection
visibility, validate the entire image, or establish UI/human acceptance. Record
the actual display scale/bounds alongside the image and still inspect its content.

Selection messages are not visual proof: assert the selected range and its
intersection with the real viewport, then capture before/after the action. A
success label can appear while its target remains below the viewport.

## Keep outcomes attributable

Run only the check needed for the change, widening after new evidence demands it.
When commands are batched, retain each exit code and full log; a final successful
`cat`, `rg`, or test does not cancel an earlier failed check. Return the first
useful diagnostic and log path in the same result. Expected guard rejections and
search no-matches are not application regressions.

Use unique output locations; do not overwrite earlier accepted captures or mix
sources and binaries from different runs. Report case names and actual outcomes,
not just aggregate counts. Keep automated verification, internal review, design
direction approval, and human application acceptance separate.
