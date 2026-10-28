# Interaction verification (fork extension)

Apply these checks to the interaction being changed, not as a mandatory full
audit on every edit. They supplement the unchanged upstream Design Guides.

Before coding a new interaction, state its object, affected data, result, state
owner, keyboard path, overlay exit, and focus return. Separate selection, focus,
editing, commitment, cancellation, and persistence; do not infer one from another.

Use representative content early: long paths/refs, CJK labels, empty collections,
invalid drafts, loading/failure, the product's minimum and normal window sizes,
and both themes. Do not universalize one product's 1100×760 minimum. Record zoom
or display-scale conditions separately; an untested scale does not inherit a pass.

Check **transitions**, not only isolated screens:

- mode/category changes keep global navigation stable and preserve valid focus;
- filtering, rescanning, and source/root changes preserve or reset only the
  intended state, and stale asynchronous results cannot overwrite new state;
- entering/leaving edit mode preserves drafts as promised and returns focus;
- Select/menu arrows and Input Delete/Enter/Escape reach the child before an
  enclosing command; composition/IME is not mistaken for an application commit;
- cancel/reopen of a dialog restores a valid target and retains failed input;
- a long label cannot push a sibling row/action out of its intended bounds;
- after selection/reveal, the actual item is visible in the viewport, not merely
  named by a status label.

Choose the smallest test layer that proves the contract: pure state, GPUI entity
or UI integration, then isolated native input for window-system-dependent facts.
HTML/mock behavior is design evidence, not native execution evidence. Synthetic
marked text is not a real IME/screen-reader check. Label untested capabilities.

Use [native verification](../../gpui-kit/references/native-verification.md) for
failed waits, real window bounds, capture dimensions and result provenance.
Measure equal edges/gaps and stable navigation coordinates across the changed
states; a screenshot at one width does not prove the transition invariant.

An internal `ship` means the inspected scope is ready for a user to review. It
does not resolve a human review gate or approve unrelated changes. Preserve the
target version, user's actual feedback, adopted fixes, and next bounded scope.
