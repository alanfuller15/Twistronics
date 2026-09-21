# Pre-freeze development checks

23 targeted numerical/join assertion cases passed in 0.66 s before the numerical freeze. This was a targeted development run, not the complete publication suite. It exercised bounded/unwrapped roots, failed optimizer results, both exterior minima, loop retry restrictions, and wrong seed/basis/gauge joins.

During the numerical run, 14 targeted saved-frame/runtime assertions passed in 0.92 s (24 other reconciliation cases deselected). These checked corrupted hashes/records/frames, polar-orientation reflection and actual executable alias equivalence versus changed runtime fields. This targeted run did not constitute the final publication suite. No numerical runner, threshold or plan changed.
