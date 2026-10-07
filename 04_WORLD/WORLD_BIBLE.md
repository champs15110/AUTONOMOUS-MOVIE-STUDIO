# WORLD BIBLE — NINETY-TWO TURNS

**Project:** AMS-2026-001 · **Task:** T03_CHARACTER_WORLD · **Machine twin:** `WORLD_MANIFEST.json` · **Props:** `PROP_BIBLE.md`

The world is a drowned coastal town, so EVERYTHING is repurposed, barnacled and wet. Nothing is decorative. The world is modular and instanced to stay CPU-renderable. Three sets carry the whole film; the tower carries five of ten scenes through relighting alone.

## Global rules

**Lighting.** Almost entirely practical and motivated: one lamp, one spark, one beacon, one dawn. One warm light source per scene except the ignition. Volumetric shafts through rain. Heavy silhouette work so shapes read at any size.

**Weather progression.** SC01-SC03 still and calm. Rain begins sparse at SC04_SH003, steady by SC04_SH006. Full storm SC05-SC06 with wind from camera-right. Full gale SC07. Calm SC09-SC10. Rain never stops until SC09.

**Water.** A shaded plane with an animated normal map; gentle in SC03, violent from SC05. Largely hidden by rain and fog. No fluid simulation.

**Colour script.**

| Scenes | Key | Purpose |
|---|---|---|
| SC01, SC02, SC03 | cold teal, one warm practical | isolation, dusk |
| SC04, SC05 | storm slate, deep teal, amber spark | threat plus the thing worth protecting |
| SC06, SC07 | near-monochrome, high contrast, storm-white rim | the world reduced to effort |
| SC08 | black to full amber | the largest contrast event |
| SC09, SC10 | dawn rose-gold over wet stone | release, warmth returned |

---

## The Winding Plaza

**id:** `LOC_PLAZA` · **scenes:** SC01, SC02, SC03

**Architecture.** A barnacled stone harbour quay. Flagged stone paving, a low sea wall, and a row of cast-iron lamp posts. At the centre, the winding pillar: a fluted brass column ~2 m tall topped with a key socket. Behind the quay, the drowned town - submerged rooftops, arches and chimneys - rises out of black water. The unlit lighthouse tower stands on the far horizon.

**Scale.** Built at human scale so WICK reads as tiny against it. The pillar is 5x her height; the lamp posts ~7x. The town behind is vast and empty.

**Materials.** wet barnacled stone; cast iron, rusted at the base; aged brass pillar with verdigris; kelp and algae; still black water

**Lighting.** Dusk. A single warm practical from the one still-burning lamp post. Everything else cold teal ambient. The pillar and posts are dark except for that one lamp.

**Atmosphere.** Quiet, patient, going dark. Heavy damp haze over the water. No birds.

**Time of day.** Dusk, the last light of the day. Lit at dusk only; left behind at 01:32.

**Weather.** Still. No wind yet. The last calm of the film.

**Important background elements.** the winding pillar (stripped socket); the row of dead lamp posts; the ONE burning lamp post; the drowned rooftops and arches; the unlit tower on the horizon; kelp in the shallows

**Palette.** teal #2e4b52, wet stone grey #5c6468, brass #b98a3d, amber #ffb457 · **Modularity.** Quay kit of repeatable flag stones and sea-wall blocks; lamp posts and rooftops are instanced variants.

**Continuity.**
- Only one lamp burns, and it is always the same lamp - the source of the spark.
- The water line established here is the reference for SC03-SC04.
- The tower on the horizon must sit at the same bearing as SC02_SH004.

**Reference images:** 04_WORLD/REFERENCE_IMAGES/LOC_PLAZA_winding_plaza.png

---

## The Flooded Streets

**id:** `LOC_STREETS` · **scenes:** SC04, SC05

**Architecture.** A narrow half-submerged lane of the old town. Stone and timber shopfronts with dark empty windows and submerged doorways on both sides; a collapsed awning; a wrought-iron railing along one side just above the waterline; a submerged wooden market stall mid-lane. Overhead, a rusted steel gantry walkway spans the lane on iron brackets, its plating perforated and corroded.

**Scale.** Shot from water level so a 40 cm character reads against a flood. The gantry is ~2.5 m above the water - a serious climb for her.

**Materials.** waterlogged timber; stained stone; rusted wrought iron; corroded steel gantry plating; black reflective water

**Lighting.** Storm light, deep teal, near-flat and cold. The water is the brightest surface; reflections do the lighting. The spark becomes the only warm source once introduced.

**Atmosphere.** Treacherous, closing in. The street is a channel that funnels wind.

**Time of day.** Dusk deepening into night. The darkest interior-feeling space before the tower.

**Weather.** First raindrops at SC04_SH003, steady by SC04_SH006. Full storm and horizontal rain by SC05. Gantry swaying in gusts.

**Important background elements.** the gantry walkway (sways, and carries the pole loss); the iron railing; the submerged market stall (her first climb); the wall coping she hauls onto; black water with first ripples

**Palette.** storm slate #46525a, deep teal #1f3d44, cold steel #6b7880, amber spark #ffb457 · **Modularity.** Shopfronts are a repeatable facade module instanced along a curve; the gantry is one hero asset.

**Continuity.**
- Water level must match SC03_SH005 (same lane, other side) and stay constant through SC04-SC05.
- Wind direction is camera-right for all of SC05.
- The gantry plating the pole hits must be the same plating the pole is later found wedged in (SC07_SH005) - the storm carries it to the tower.

**Reference images:** 04_WORLD/REFERENCE_IMAGES/LOC_STREETS_flooded_streets.png

---

## The Tidelight Tower

**id:** `LOC_TOWER` · **scenes:** SC06, SC07, SC08, SC09, SC10

**Architecture.** A tapering iron lighthouse. Exterior: riveted iron plates in vertical courses, riveted handholds, narrow service bands, a railed gallery near the top and the glass lantern room above. A section of the internal spiral stair has torn away, leaving a jagged breach to the exterior. Interior: a cold stairwell where water runs down the wall; at the top, the burner chamber - an enormous room holding the giant brass burner mechanism under a curved glass-and-iron roof.

**Scale.** The tallest vertical set in the film. SC06 reads her small at the door; SC07 reads the sea far below; SC08 reads her tiny inside the vast chamber. The burner is room-sized; the socket is small by contrast.

**Materials.** riveted black iron, rust-streaked; salt-stained brass on the burner; cold glass lens rings; wet iron floor; curved storm glass roof

**Lighting.** SC06-SC07: storm-white rim outside, near-monochrome. Interior from SC06_SH004: her chest glow is the ONLY light until the ignition. SC08: black to full amber at the ignition. SC09: the beam, then dawn. SC10: dawn rose-gold.

**Atmosphere.** Vast, vertical, unforgiving - then, after the ignition, transcendent.

**Time of day.** Night for SC06-SC08. The beam sweeps the dark at SC09. Dawn for SC10.

**Weather.** Full gale on the exterior at SC07, dropping sharply inside the gallery lee at SC07_SH008. Calm by SC09-SC10.

**Important background elements.** the iron door, swollen and barnacled; the broken spiral stair and the exterior breach; the riveted handholds and service bands (the climb); the gallery rail; the burner with its single socket; the curved glass roof, dripping

**Palette.** black iron #10151a, storm white #dfe6ea, amber ignition #ffb457, dawn rose #e8b08c · **Modularity.** One vertical set reused across five scenes through relighting and camera height - the highest reuse ratio in the film. The climb and the ignition share geometry.

**Continuity.**
- The breach in SC06_SH005 must match the exit in SC07_SH001.
- The stair is destroyed at SC07_SH002 - no intact stair in any later shot.
- From SC06_SH004 to SC08_SH002 her glow is the only interior light.
- SC10 is the same burner chamber relit at dawn; pose must match SC09_SH003.

**Reference images:** 04_WORLD/REFERENCE_IMAGES/LOC_TOWER_exterior.png · 04_WORLD/REFERENCE_IMAGES/LOC_TOWER_burner_chamber.png

---
