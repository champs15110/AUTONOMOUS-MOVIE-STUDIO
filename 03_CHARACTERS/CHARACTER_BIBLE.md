# CHARACTER BIBLE — NINETY-TWO TURNS

**Project:** AMS-2026-001 · **Task:** T03_CHARACTER_WORLD · **Machine twin:** `CHARACTER_MANIFEST.json`

All designs are original, authored in-house, and built to the no-GPU / CPU-renderable constraint: hard surface, no hair, no cloth, no facial blendshapes on any character. The human appears only in SC10 and is never in readable close-up.

**Reference images:** 03_CHARACTERS/REFERENCE_IMAGES/WICK_model_sheet.png · 03_CHARACTERS/REFERENCE_IMAGES/WICK_performance_sheet.png · 03_CHARACTERS/REFERENCE_IMAGES/CHILD_and_SHIP_reference.png

---

## WICK

**id:** `CHAR_WICK` · **role:** protagonist - wind-up brass lamplighter automaton · **provenance:** original design, authored in-house for this production

**Personality.** Methodical, patient, quietly dutiful. She treats her job as her whole reason for existing, which is exactly why spending herself is not a tragedy to her but a completion. Affectionate toward small things she never says. She solves problems with arithmetic until the arithmetic fails, then solves them with everything.

### Body
- **Proportions:** Top-heavy: a large rounded barrel torso over four comparatively thin jointed limbs. Head is a single domed brass shell fused to the top of the torso - no neck. Torso height ~ 60% of total; limbs long for her size so she can reach, giving a slightly gangly, endearing walk.
- **Height:** 40 cm (0.4 m). Scale reference: the human hand shown on the model sheet is larger than her whole body. The lamp-pole is taller than she is.
- **Silhouette:** A rounded egg on sticks. Must read at 20 pixels tall: the domed head, the barrel chest, the thin limbs and the one long pole are the only elements. The chest drum is a circle of light in the middle of the mass.
- **Buildable geometry:** Hard-surface only. Torso and head from a single lofted ovoid; limbs from cylinders with torus joints; chest drum from a boolean-cut circle plus a convex glass lens; mainspring from a swept spiral curve with a rectangular profile; key from two boxes and a cylinder. No subdivision surfaces, no cloth, no hair, no subsurface.

### Face
- **Face:** There is no face. The front of the domed head carries only the two shutter-lens eyes. This is the core design decision: emotion is never carried by a face, so there is nothing to lip-sync and nothing to blendshape.
- **Eyes:** Two round apertures built from overlapping brass iris (shutter) blades, like a camera lens. They glow warm amber from an internal light tied to her charge. The aperture width IS her expression: wide = alert/wonder, half = calm, slit = alarm/anger, closed = rest, flicker = failure, dark = gone. The blades are visible when open, which gives the eye a mechanical, non-biological glint.
- **Mouth:** None. Deliberately and permanently. All 'speech' in the film is sound design.

**Clothing.** None. Her shell is her clothing - aged brass plating with rivets and seams where a garment would have hems. A small worn maker's stamp (an abstract gear sigil, no letters) is embossed on her left shoulder plate.

**Materials.** aged brass, satin with soft scratches; verdigris green in every crevice and seam; barnacle and salt crust on the lower torso and feet - she has spent her life at the waterline; polished clear glass for the chest drum; blued steel for the mainspring; dulled iron for the limb joints

**Colours.** palette brass gold #b98a3d, verdigris #4f8f7b, wet stone grey #5c6468, blued steel #33404a · accent warm amber emission from the eyes and chest #ffb457

**Accessories.** the winding key (seated in her back, then carried/removed); the lamp-pole (carried, lost, recovered); the chest gauge and mainspring (her own body - diegetic countdown); the spark (carried inside the chest from SC05 to SC08)

**Expressions.** Aperture-based only, six canonical states: WIDE (85%), HALF (50%), SLIT (20%), CLOSED (0), FLICKER (irregular stutter), DARK (off). The iris blades make each state mechanically legible. Head tilt (0-25 degrees) is the second channel; a full 25-degree forward lean means focus, a backward jerk means alarm.

**Body language.** Economical and rounded. When uncertain she folds her limbs close and lowers the dome. When determined she leans 15 degrees into her travel. When protecting the spark she curls one arm across the chest drum and hunches, which changes her silhouette for the whole of SC05-SC08. In grief the head drops until the dome touches the chest. She never gesticulates - every motion has a purpose.

**Movement style.** A four-beat ratchet gait - a clean, rhythmic 'tick-tick-tick-tick' established at SC03_SH001. It degrades on a strict schedule: irregular after the underwater drop (SC04_SH002), skipping after the shoulder failure (SC07_SH006), fully broken dragging by SC07_SH007. The gait IS the performance and IS the soundtrack. Her centre of gravity is high, so she rocks slightly when she stops.

**Continuity.**
- The barnacle line never rises above the lower third of the torso - it records her waterline history.
- After SC04_SH006 the left shoulder joint sparks; the same joint fails at SC07_SH004. Animate the damage as a weakness, not a new injury.
- From SC05_SH005 to SC08_SH002 the chest drum glows with the spark; from SC08_SH002 it is dark. Never light again until the child's turn at SC10_SH005.
- The key is in her back from SC01 to SC10_SH002, absent SC10_SH003-005 (it is in the child's hand).
- The lamp-pole is present SC02_SH006-SC05_SH002, ABSENT SC05_SH003-SC07_SH004, present from SC07_SH005.

**Reference images:** 03_CHARACTERS/REFERENCE_IMAGES/WICK_model_sheet.png · 03_CHARACTERS/REFERENCE_IMAGES/WICK_performance_sheet.png

---

## THE RETURNING SHIP

**id:** `CHAR_SHIP` · **role:** the stake - never a character we meet closely · **provenance:** original design, authored in-house

**Personality.** Not a person; the embodiment of what WICK is spending herself on. It must read as tired but alive: a long voyage ending, a single light refusing to go out.

### Body
- **Proportions:** Low, broad cargo hull with a single raked mast slightly aft of centre. Deliberately unheroic - a working boat, not a tall ship.
- **Height:** n/a - seen only at long range
- **Silhouette:** A low black band on the water with one tilted mast and one amber point of light. No detail beyond that is ever shown.
- **Buildable geometry:** Low-poly hull, single mast cylinder, one emissive running-light sphere. Always rendered behind rain and fog so it never needs more.

### Face
- **Face:** n/a
- **Eyes:** n/a
- **Mouth:** n/a

**Clothing.** n/a

**Materials.** weathered black-painted timber hull; tarred rigging; brass running light

**Colours.** palette slate black #1b2126, storm grey #46525a · accent amber running light #ff9d3b

**Accessories.** one amber running light; a bell buoy on a line astern

**Expressions.** n/a - its 'expression' is its heading: toward the reef (danger) or toward harbour (relief). The single turn of its running light at SC09_SH002 is the whole performance.

**Body language.** n/a

**Movement style.** A slow, heavy roll in the swell. It never moves fast; its turns are ponderous, which is why the 20-second hold in SC09 works.

**Continuity.**
- Bearing and reef-line position must match between SC02_SH003 and SC09_SH002 so the turn reads as turning AWAY from danger.
- Never closer than extreme long lens. Never detailed. One running light only.

**Reference images:** 03_CHARACTERS/REFERENCE_IMAGES/CHILD_and_SHIP_reference.png

---

## THE CHILD

**id:** `CHAR_CHILD` · **role:** the closing gesture - the only human · **provenance:** original design, authored in-house

**Personality.** Quiet, unhurried, careful. Not grieving, not celebrating - doing a small necessary thing with the seriousness children give to ritual. They give one turn and do not ask for anything back.

### Body
- **Proportions:** Small for ~seven years, and visually smaller because the coat swamps the frame. Barefoot. Head is a soft silhouette; hands are the only resolved feature.
- **Height:** ~115 cm - roughly 2.9 times WICK's height, which makes the scale relationship legible without a shared frame.
- **Silhouette:** A small dark teardrop: oversized coat, hoodless, bare feet. Always backlit and rim-lit against dawn.
- **Buildable geometry:** Low-poly body with a single sculpted coat mesh; no facial rig, no hair cards, no cloth sim. The coat is a static sculpted shape, not a simulation.

### Face
- **Face:** Never resolved. The face stays in shadow or out of focus for the whole of SC10. Backlight and rim light only.
- **Eyes:** n/a - never shown
- **Mouth:** n/a - never shown; the film has no dialogue

**Clothing.** An oversized oilskin coat, sleeves far too long, hem dragging on the wet iron. Barefoot.

**Materials.** waxed oilskin, matte; damp cotton; bare skin on feet and hands

**Colours.** palette dawn-silhouetted umber #2a2018, wet umber grey #3a3634 · accent dawn rim light #ffd9a0

**Accessories.** the brass winding key, held in one hand, SC10_SH003-005

**Expressions.** Not shown. The performance lives entirely in the hands and the hesitation at SC10_SH003.

**Body language.** Kneels beside WICK rather than standing over her - an act of equality. Moves slowly and deliberately. The one hesitation before the turn is the only emotional beat.

**Movement style.** Barefoot, near-silent, weight low and careful on wet iron - the opposite of WICK's ticking gait. Organic where she is mechanical.

**Continuity.**
- Never in readable close-up. Backlit / rim-lit only.
- Only SC10. No human appears anywhere earlier.
- The key in the child's hand is the same asset as SC01_SH001.

**Reference images:** 03_CHARACTERS/REFERENCE_IMAGES/CHILD_and_SHIP_reference.png

---
