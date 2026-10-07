# RESEARCH — *NINETY-TWO TURNS*

**Project:** AMS-2026-001 · **Task:** T01_DEVELOPMENT
**Researched:** 2026-10-07 · **Method:** live web research, three queries
**Purpose:** ground the format, pacing and production decisions in `MASTER_FILM_BRIEF.md`
in current evidence — **without taking anything from any existing film.**

---

## 0. How to read this document

Every section ends with **→ APPLIED**, stating the concrete decision it produced in the
brief. Nothing here is a design source. Where an existing film is named, it is cited only
as evidence that a *technique* works; no character, design, story, scene or line has been
taken from it. See `MASTER_FILM_BRIEF.md` §10.

**Applicability caveat, stated up front.** Most retention data below comes from short-form
vertical video (YouTube Shorts, TikTok, Reels), not from 3–7 minute 16:9 narrative
animation. The *mechanisms* — early hook, visible stakes, cadence, silent legibility,
looping — transfer cleanly. The specific completion-rate benchmarks do **not** transfer
directly, because a viewer who chose a five-minute film has already committed. Where a
number is quoted below, treat it as directional evidence for pacing, not as our KPI.

---

## 1. How fast viewers decide

| Finding | Source |
|---|---|
| Viewers decide in roughly **one second** whether to keep watching | YouTube Shorts product lead Todd Sherman, via the YouTube Blog deep dive, Jan 2025 |
| A hook in the first **2 seconds** retains ~**19 %** more viewers than a slow start | Zebracat 2025 Shorts statistics |
| The typical viewer swipes after ~**5–6 seconds** if not hooked | Our Own Brand, 2025 |
| Average watch before swiping is ~**14.3 seconds** | Zebracat 2025 |
| "Drop viewers mid-action: skip the setup and open on the peak moment." Treat the opening like the climax, not the build-up | Shorts creator Jenny Hoyos |

Sources: [How to Go Viral on YouTube Shorts (2026)](https://www.teleprompter.com/blog/how-to-go-viral-on-youtube-shorts),
[The First 3 Seconds](https://virvid.ai/blog/first-3-seconds-hook-faceless-shorts-2026),
[How to Increase Retention & Watch-Time](https://virvid.ai/blog/ai-shorts-increase-retention-watch-time).

**→ APPLIED.** `MASTER_CONFIG.json` sets `hook_deadline_seconds: 8`. The brief beats it:
the irreversible failure lands at **00:04** and the number 92 at **00:08**. SC01 opens on a
macro of the mechanism already in motion — no title, no establishing shot, no character
reveal until second 20. The "drop viewers mid-action" principle is applied literally: the
film's first frame is the fourth turn of a key that is about to fail.

---

## 2. Completion rate and what earns distribution

| Finding | Source |
|---|---|
| YouTube Shorts average ~**73 %** retention | Socialinsider, Nov 2025 |
| Viral Shorts (1 M+ views) average ~**76 %** retention | AffiliateBooster 2025 study |
| Shorts above ~**75 %** retention have a **3×** higher chance of wider distribution | AffiliateBooster / Kit |
| A 30-second Short at 85 % watch time outranks a 60-second Short at 50 % | creator-data analyses of the Shorts algorithm |

Sources: [How to Increase Retention & Watch-Time](https://virvid.ai/blog/ai-shorts-increase-retention-watch-time),
[YouTube Shorts Algorithm Secrets](https://bosswallah.com/blog/creator-hub/youtube-shorts-algorithm-secrets-what-actually-works-in-2025/).

**→ APPLIED.** Target set at **≥ 70 % average percentage viewed** in the brief. The
"shorter beats longer at equal quality" finding is the reason the film is 302 s and not
closer to the 420 s ceiling — every scene that does not spend a turn or move the gauge was
cut during concept.

---

## 3. Cadence: a turn every 20–40 seconds

Retention analyses consistently recommend "cut relentlessly," "tease and pay off," and a
mid-video switch-up to reset attention. The practical translation for narrative work is a
**turn** — a reversal, a reveal, a threshold crossed — on a regular cadence.

Sources: [How to Increase Retention & Watch-Time](https://virvid.ai/blog/ai-shorts-increase-retention-watch-time).

**→ APPLIED.** `MASTER_CONFIG.json` encodes "a turn every 20–40 s; no dead air longer than
6 s." The brief's turn cadence is **4 · 32 · 65 · 92 · 122 · 158 · 186 · 205 · 228 · 262 ·
282** — maximum gap **36 s**.

> **Verification note.** The first draft of this cadence had a 42-second gap across SC07,
> which violated the rule. An intra-scene turn was added at 03:25 (the stair collapse,
> gauge 31 → 22). The maximum gap is now 36 s, checked programmatically.

---

## 4. Silent viewing is the default, not the exception

**More than 60 % of mobile viewers watch without sound.** A hook that only works with audio
misses over half the potential audience.

Source: [The First 3 Seconds](https://virvid.ai/blog/first-3-seconds-hook-faceless-shorts-2026).

**→ APPLIED.** The film is **wordless by design** and fully comprehensible muted. Colour,
silhouette, framing and the chest gauge carry 100 % of the plot. Music and mechanism sound
deepen it but are never load-bearing. This is a creative decision *and* a production
decision: no dialogue means no voice recording, no lip sync and no phoneme work.

---

## 5. Wordless animation is a proven emotional register

Speechless storytelling works because it transfers the load to **body language, lighting
and colour, sound design, camera placement and editing rhythm** — and because it removes the
language barrier entirely, making the work universally distributable. Animation is
particularly strong at it, since every element of the frame is under the author's control.

Evidence for the technique (cited as technique only, never as a design source):
posture and framing carrying emotion; cool tones signalling danger and warm tones
signalling safety; fast cuts during danger and slow ones during rest; environments telling
the audience how unsafe the world is without exposition.

Sources: [The Power of Speechless Storytelling](https://fredanderic.com/stories/the-power-of-silent-storytelling-how-to-convey-emotion-without-words),
[wordless-film analysis of *Flow*](https://wellwhisk.com/does-flow-movie-have-words/),
[*Flow* review](https://videolibrarian.com/reviews/film/flow/).

**→ APPLIED.** WICK has **no face to animate** — two shutter lenses, no mouth, no
blendshapes. Emotion is carried by shutter aperture, head tilt, limb posture and gait
rhythm. The colour script runs cold teal → storm slate → amber ignition → dawn rose-gold,
with warm and cold used as emotional signals exactly as the research describes. SC09 uses a
deliberate 20-second hold as the "slow cut during rest" beat.

**Originality guard:** these sources informed the *decision to make the film wordless*. No
character, creature, design, setting, plot point or image has been taken from any film named
in them.

---

## 6. Serialised and animated content is a growth area

Animated series and recurring digital storylines are growing strongly, and viewers reward
ongoing narratives because they create anticipation. Animation is explicitly called out as a
strength area for 2025–2026.

Source: [YouTube trends 2025: 9 creator insights](https://www.tubebuddy.com/blog/youtube-trends-2025/).

**→ APPLIED.** The brief is written so that WICK and the Tidelight can carry further
stories without any additional asset work — the harbour, the tower and the automaton are a
reusable world. This costs nothing at T01 and preserves option value. **No serialisation is
assumed for this deliverable:** the film has a complete beginning, middle, climax and ending
and stands alone.

---

## 7. Looping and rewatch as a compounding signal

Looping structure and loopable endings compound watch time without extra production work.

Sources: [How to Go Viral on YouTube Shorts (2026)](https://www.teleprompter.com/blog/how-to-go-viral-on-youtube-shorts),
[The First 3 Seconds](https://virvid.ai/blog/first-3-seconds-hook-faceless-shorts-2026).

**→ APPLIED.** The closing macro of the key turning mirrors the opening macro **frame for
frame**, so the film loops cleanly. The rewatch reward is structural, not decorative: on a
second viewing the audience knows the socket reveal is coming, and can watch SC01–SC07 as a
machine being led to its purpose.

---

## 8. Production: simplify the vision, or the schedule eats you

The industry guidance for CG shorts is blunt:

> "Simplicity in design and execution are worthwhile goals for a CG short. Minimizing the
> complexity of your proposed film idea can significantly lower your production costs…
> Can you tell your story using fewer characters? Each character in your film needs to be
> modeled, rigged and animated… Perhaps your goofy cartoon alien works just as well with
> three fingers instead of five. Maybe you don't need to actually model every single tree.
> Look into instancing or using 2D cards or background plates instead."

Source: ['Inspired 3D Short Film Production': Production Planning, AWN](https://www.awn.com/vfxworld/inspired-3d-short-film-production-production-planning-part-5).

**→ APPLIED.** This is the single most influential source in the brief. Concrete results:

| Guidance | Decision taken |
|---|---|
| Fewer characters | **One** rigged character. Two others appear as a distant silhouette and a backlit child for 17 s. |
| Simplify characters | No facial rig, no mouth, no hair, no cloth. Two shutter lenses. |
| Instance, don't model | Modular, instanced harbour architecture; no unique building geometry. |
| Shorter film, shorter cycle | 302 s, ten scenes, and every scene must spend a turn or move the gauge. |
| Reuse sets | The tower carries **five of ten scenes** through relighting alone. |

---

## 9. Production: render strategy on constrained hardware

| Finding | Source |
|---|---|
| Denoising reduces render time by producing clean images at **lower sample counts** | Blender/Cycles short-film workflow guidance |
| Real-time engines (Eevee-class) cut production time **20–30 %** vs traditional offline rendering | Unity short-film production study |
| Render **individual frames**, not the whole video — it allows re-rendering specific frames when issues arise | Blender short-film workflow guidance |
| Split shots into separate scenes so you only render the visible elements | Blender short-film tips |

Sources: [Making a Short Film in Blender](https://reelmind.ai/blog/making-a-short-film-in-blender-3d-animation-techniques),
[Production of 3D Animated Short Films in Unity 5](https://www.academia.edu/34095494/Production_of_3D_Animated_Short_Films_in_Unity_5_Can_Game_Engines_Replace_the_Traditional_Methods),
[5 Tips For Making Animated Shorts in Blender](https://garagefarm.net/blog/5-tips-for-making-animated-shorts-in-blender).

**→ APPLIED.** Three decisions, all of which validate the pipeline already built in this
repository:

1. **Stylised-realistic, not photoreal.** A stylised look tolerates low sample counts plus
   denoising — the biggest CPU render-time lever available to us. This is why the look is
   "brass and barnacle" rather than physically accurate.
2. **Scene-level renders only.** This is exactly what `13_RENDER/RENDER_MANIFEST.json`
   enforces with its `SCENE → PREVIEW → QC → FINAL_RENDER → VERIFY` lifecycle. The research
   independently confirms the architecture.
3. **Frames written individually.** Required by the manifest rules so any single shot can be
   re-rendered without touching verified scene output.

The "only render visible elements" finding is a direct instruction for T05/T06: per-shot
scene assembly rather than one monolithic set file.

---

## 10. Risks this research surfaces

| Risk | Response |
|---|---|
| Short-form benchmarks may not describe long-form animated audiences | Targets in the brief are set as internal goals, not promises. The 70 % completion target is treated as a pacing diagnostic. |
| Wordless films can lose audiences who expect dialogue | Mitigated by a hard, visible countdown that supplies continuous explicit stakes — the strongest available substitute for exposition. |
| Simplification can read as cheap | Mitigated by spending the saved complexity on **lighting and camera**, which is where the cinematic register actually lives. |
| The gauge is a small on-screen detail | Framing rules guarantee it screen area on every change; it is never cut away from during a decrement. |
| Retention tactics can flatten emotional pacing | The 20-second hold in SC09 is deliberately protected. Cadence rules apply to *turns*, not to cutting rate. |

---

## 11. Summary of decisions driven by research

1. Hook at 00:04, ahead of an 8-second internal deadline. (§1)
2. 302 seconds rather than the 420-second ceiling. (§2)
3. Turn cadence with a 36-second maximum gap. (§3)
4. Wordless, and fully legible with the sound off. (§4, §5)
5. One rigged character; three locations; tower reused across five scenes. (§8)
6. Stylised-realistic look to permit low samples plus denoising on CPU. (§9)
7. Scene-level render architecture, independently validated. (§9)
8. Loopable ending that mirrors the opening macro. (§7)
9. Reusable world design preserving serialisation option value. (§6)

---

## Appendix — queries run

| # | Query | Date |
|---|---|---|
| 1 | short animated film audience retention first seconds hook YouTube 2025 trends | 2026-10-07 |
| 2 | wordless animated short film visual storytelling no dialogue why it works emotional | 2026-10-07 |
| 3 | indie 3D animated short film production scope reduce complexity stylized look Blender CPU render time | 2026-10-07 |

**Not consulted, deliberately:** reference images or design material from any existing
animated film. Design references for T03 will be generated or authored in-house with
provenance recorded per `MASTER_CONFIG.creative_constraints`.
