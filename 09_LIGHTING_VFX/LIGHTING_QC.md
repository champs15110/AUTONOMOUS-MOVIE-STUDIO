# Stage 09 — Lighting/VFX QC (NINETY-TWO TURNS)

Generated: 2026-10-08T01:24:31+00:00 · harness: `run_lighting_tests.py` (structural, stub bpy)

Checks per scene: shadow-coherence, character-lit, face-readability, materials,
background, design-adherence, vfx-objects, wind-direction (storm scenes),
exposure-proxy, shot-timing (SC04/07/08). Global: 58/58 shot coverage with
setup ref + grade note; every effect has a story purpose.

**Exposure note:** `exposure-proxy` is a structural estimate (key-light energy at
the character anchor). Broadcast-range legality on real frames is measured at
render QC in task T11 — not claimed here.

| Scene | Status | Detail |
|---|---|---|
| SC01 | VERIFIED | shadow-coherence: ok; character-lit: ok; exposure-proxy: ok; face-readability: ok; materials: ok; background: ok; design-adherence: ok; vfx-objects: ok |
| SC02 | VERIFIED | shadow-coherence: ok; character-lit: ok; exposure-proxy: ok; face-readability: ok; materials: ok; background: ok; design-adherence: ok; vfx-objects: ok |
| SC03 | VERIFIED | shadow-coherence: ok; character-lit: ok; exposure-proxy: ok; face-readability: ok; materials: ok; background: ok; design-adherence: ok; vfx-objects: ok |
| SC04 | VERIFIED | shadow-coherence: ok; character-lit: ok; exposure-proxy: ok; face-readability: ok; materials: ok; background: ok; design-adherence: ok; vfx-objects: ok; shot-timing: ok |
| SC05 | VERIFIED | shadow-coherence: ok; character-lit: ok; exposure-proxy: ok; face-readability: ok; materials: ok; background: ok; design-adherence: ok; vfx-objects: ok; wind-direction: ok |
| SC06 | VERIFIED | shadow-coherence: ok; character-lit: ok; exposure-proxy: ok; face-readability: ok; materials: ok; background: ok; design-adherence: ok; vfx-objects: ok; wind-direction: ok |
| SC07 | VERIFIED | shadow-coherence: ok; character-lit: ok; exposure-proxy: ok; face-readability: ok; materials: ok; background: ok; design-adherence: ok; vfx-objects: ok; wind-direction: ok; shot-timing: ok |
| SC08 | VERIFIED | shadow-coherence: ok; character-lit: ok; exposure-proxy: ok; face-readability: ok; materials: ok; background: ok; design-adherence: ok; vfx-objects: ok; shot-timing: ok |
| SC09 | VERIFIED | shadow-coherence: ok; character-lit: ok; exposure-proxy: ok; face-readability: ok; materials: ok; background: ok; design-adherence: ok; vfx-objects: ok |
| SC10 | VERIFIED | shadow-coherence: ok; character-lit: ok; exposure-proxy: ok; face-readability: ok; materials: ok; background: ok; design-adherence: ok; vfx-objects: ok |
| ALL | VERIFIED | coverage: 58/58 shots with setup+grade; purposeless effects: 0 |
