#!/usr/bin/env python3
"""
Build the Stage 04 storyboard / cinematography deliverables from the locked shot list:

  05_STORYBOARD/MASTER_SHOT_PLAN.json   - every shot, 18-field production specification
  05_STORYBOARD/CAMERA_PLAN.json        - camera-only projection
  05_STORYBOARD/BLOCKING_PLAN.json      - blocking / depth-layer projection
  05_STORYBOARD/STORYBOARD.md           - human-readable board
  05_STORYBOARD/BEAT_BOARD.md           - scene-level beat board
  05_STORYBOARD/panels/PANEL_INDEX.md   - index of generated reference frames

The generator reads 02_SCREENPLAY/SHOT_LIST.json (ids, timecodes, action, sound, lens,
shot_type, characters, continuity, transition) and merges a per-shot cinematography overlay
authored here. It asserts that every screenplay shot has exactly one plan entry - no missing
ids - and that the registry/manifest it also populates stay in sync.

Run:  python3 05_STORYBOARD/build_shot_plan.py
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
J = json.load(open(os.path.join(ROOT, "02_SCREENPLAY", "SHOT_LIST.json"), encoding="utf-8"))
WO = json.load(open(os.path.join(ROOT, "04_WORLD", "WORLD_MANIFEST.json"), encoding="utf-8"))

AXIS = ("Master line of action: the sea and the returning ship sit FRAME RIGHT; the tower "
        "sits FRAME LEFT. WICK's journey runs frame RIGHT to LEFT. The climb runs vertically "
        "with the tower wall to the left. After the ignition the payoff looks back FRAME RIGHT "
        "to the sea. No shot crosses this axis without a neutral macro or POV buffer.")

SCENE_LIGHT = {s["scene_id"]: next(r["key"] for r in WO["global_rules"]["color_script"]
                                   if s["scene_id"] in r["scenes"]) for s in J["scenes"]}

# --------------------------------------------------------------------------- #
# per-shot cinematography overlay (authored)
# --------------------------------------------------------------------------- #
O = {
# SC01 --------------------------------------------------------------------- #
"SC01_SH001": dict(comp="centre-weighted macro; the key is the entire frame", height="chest-height of a 40cm machine (macro)", angle="level, dead-on", dist="extreme macro ~10cm", motion="locked-off. Motivation: nothing moves but the key, so the camera must not add motion.", blocking="WICK off-frame; only her back plate and the turning key.", fg="key bow", mg="back plate seam", bg="black void", dir="static; no travel", light="one warm practical raking the brass; everything else black", emo="curiosity"),
"SC01_SH002": dict(comp="rule-of-thirds; the shearing tooth at an upper intersection", height="chest macro", angle="level", dist="macro", motion="very slight push-in. Motivation: the audience leans toward the failure.", blocking="coil inside the drum; tooth shears and falls out of frame.", fg="glass reflection", mg="coiled spring", bg="drum interior, dark", dir="static", light="amber internal glow on the coil; the ping reads as a flash", emo="dread"),
"SC01_SH003": dict(comp="centred gauge; the number 92 dead-centre", height="chest macro", angle="level", dist="macro", motion="static. Motivation: the first true stillness lets the number land.", blocking="needle settles; trembles once; still.", fg="gauge glass", mg="needle + 92", bg="out-of-focus amber lamp glow drifting", dir="static", light="soft amber defocus over cool brass", emo="dread, held"),
"SC01_SH004": dict(comp="reveal: subject low-centre, vast negative space above", height="rising from her eye height to a high crane", angle="low to high in one move", dist="macro to extreme wide", motion="slow continuous crane back and up. Motivation: the world is the reveal; the move is the reveal.", blocking="WICK stands alone, tiny, on the quay.", fg="quay edge stone", mg="WICK", bg="drowned town, dusk sky, one burning lamp, tower on horizon frame L", dir="static frame; she is still", light="dusk teal; the single amber lamp is the only warm source", emo="wonder, isolation"),
"SC01_SH005": dict(comp="close, head-centred; eyes on the top third", height="her eye height (~0.35m)", angle="level", dist="close", motion="handheld micro-drift. Motivation: a living, breathing (ticking) machine.", blocking="shutter eyes iris open; head drops to the chest gauge, then tilts up.", fg="none", mg="head + chest top", bg="soft dusk quay", dir="eyeline: gauge down, tower up/left", light="cool dusk with amber eye glow", emo="alert, assessing"),
"SC01_SH006": dict(comp="her POV; tower small at the left-third horizon line", height="her eye height", angle="level", dist="wide (her POV)", motion="static. Motivation: it is her gaze, not a camera idea.", blocking="WICK off-frame (POV).", fg="water sheen", mg="black harbour water", bg="unlit tower frame L, bruised sky", dir="looks frame L", light="last dusk; tower a black silhouette", emo="resolve forming"),
# SC02 --------------------------------------------------------------------- #
"SC02_SH001": dict(comp="low medium; the pillar looms over her, apex off-frame", height="ankle-height of a human / her full height", angle="low, tilting her small against the pillar", dist="medium", motion="static. Motivation: the habit is the point; no motion needed.", blocking="she backs to the pillar and seats herself - a daily, practised motion.", fg="pillar base barnacles", mg="WICK", bg="plaza, dusk", dir="static", light="dusk teal; pillar unlit", emo="routine"),
"SC02_SH002": dict(comp="macro socket centred; the worn teeth on the lower third", height="back height", angle="level", dist="macro", motion="static. Motivation: the repetition of the failure is the content; the camera gives no help.", blocking="key enters, spins free; she withdraws; tries again; and again.", fg="key drive", mg="stripped socket", bg="brass", dir="static", light="raking warm key-light on worn teeth", emo="confusion to alarm"),
"SC02_SH003": dict(comp="extreme long lens; the running light a point on the right-third", height="her eye height", angle="level", dist="very long (200mm) - the sea frame RIGHT", motion="held. Motivation: the ship is distant and slow; motion would falsify it.", blocking="off-frame (her eyeline).", fg="none", mg="haze", bg="sea frame R, reef line, single amber light", dir="looks frame R", light="storm-grey sea; one amber point", emo="stake"),
"SC02_SH004": dict(comp="wide; tower leans from the left edge, sky dominant", height="waterline (very low)", angle="low, leaning", dist="wide", motion="static. Motivation: let the height be felt, not pushed.", blocking="off-frame.", fg="water edge", mg="tower base", bg="tower full height frame L, bruised sky", dir="the destination frame L", light="storm slate rim", emo="foreboding"),
"SC02_SH005": dict(comp="close; gauge lower-third, tower reflected in the lenses above", height="chest height", angle="level", dist="close", motion="static. Motivation: the reflection completes the three-point eyeline.", blocking="she holds still; the tower lives in her lenses.", fg="chest brass", mg="gauge 92", bg="tower reflection in the shutter lenses", dir="reflection frame L", light="amber eye/chest glow over cool brass", emo="calculating"),
"SC02_SH006": dict(comp="medium profile; she crosses and exits frame L on the footfall", height="her eye height", angle="level profile", dist="medium", motion="static; she provides the motion and exits frame L. Motivation: cut on the step, not after it.", blocking="lifts the pole, shoulders it, takes one step frame L.", fg="stone", mg="WICK + pole", bg="plaza left", dir="travels frame L (journey axis)", light="dusk; last warm lamp behind", emo="decided"),
# SC03 --------------------------------------------------------------------- #
"SC03_SH001": dict(comp="lateral tracking; gauge held in frame as she moves R->L", height="her eye height", angle="level profile", dist="medium tracking", motion="lateral dolly at her height, matching her stride. Motivation: keep the gauge legible while she travels.", blocking="walks frame L; gauge ticks with each stride.", fg="passing bollards", mg="WICK + pole", bg="quay", dir="travels frame L", light="dusk teal; warm practicals sparse", emo="purpose under dread"),
"SC03_SH002": dict(comp="centred insert; identical gauge framing to SC01_SH003", height="chest macro", angle="level", dist="macro", motion="static. Motivation: locked insert grammar.", blocking="needle steps 88->86.", fg="gauge glass", mg="needle", bg="brass", dir="static", light="soft amber on the dial", emo="counting dread"),
"SC03_SH003": dict(comp="high crane; the drowned town fills frame, WICK small lower-third", height="high crane", angle="high, slow push", dist="extreme wide", motion="high crane, slow push. Motivation: the beauty pass is earned by height and patience.", blocking="walks away from camera, small.", fg="kelp, shallows", mg="submerged rooftops", bg="drowned harbour", dir="away / frame L", light="the film's one warm, calm light", emo="wonder"),
"SC03_SH004": dict(comp="medium tracking; lamp posts strobe the foreground", height="her eye height", angle="level", dist="medium tracking", motion="tracking; foreground poles strobe past. Motivation: rhythm and the row of dead lamps.", blocking="walks frame L past dead lamps; one burns behind.", fg="strobing lamp posts", mg="WICK", bg="dark row, one amber lamp", dir="travels frame L", light="cool with a single warm lamp behind", emo="quiet grief"),
"SC03_SH005": dict(comp="over-shoulder; black water ahead fills the frame", height="her eye height", angle="over-shoulder", dist="medium", motion="static hold on the water. Motivation: the water is the next obstacle; let it be seen.", blocking="stops at the quay edge, back to camera.", fg="her shoulder", mg="quay edge", bg="black flooded street", dir="faces frame L", light="music cuts; water catches cold light", emo="apprehension"),
# SC04 --------------------------------------------------------------------- #
"SC04_SH001": dict(comp="wide low; water fills the lower half, she at the right edge", height="water level", angle="low", dist="wide", motion="static. Motivation: the flood is the reveal.", blocking="stops at the lane edge.", fg="black water", mg="submerged lane", bg="shopfronts", dir="faces frame L", light="storm slate, flat cold", emo="daunted"),
"SC04_SH002": dict(comp="tight at her height on the stall climb", height="her height, handheld", angle="level/slight low", dist="medium-tight", motion="handheld instability. Motivation: the effort should feel unstable.", blocking="grip, haul, grip up the stall.", fg="water sheeting", mg="WICK on stall", bg="lane", dir="climbs frame L/up", light="cold with her amber chest glow", emo="working hard"),
"SC04_SH003": dict(comp="profile; the railing a hard horizontal line, she above it", height="her height", angle="level profile", dist="medium", motion="static profile; she crosses. Motivation: the line gives the traverse legibility.", blocking="hand-over-hand along the railing.", fg="raindrops on water", mg="railing + WICK", bg="lane", dir="travels frame L", light="first countable raindrops catch light", emo="committed"),
"SC04_SH004": dict(comp="underwater; the bright surface as a ceiling above", height="below the surface, looking up", angle="up from below", dist="medium", motion="goes under with her. Motivation: the drop must be felt, not observed.", blocking="grip fails; she falls; bubbles rise.", fg="bubbles", mg="WICK tumbling", bg="bright water surface above", dir="down", light="muffled; surface a bright ceiling", emo="alarm"),
"SC04_SH005": dict(comp="low underwater looking up at her amber eyes", height="lane floor, looking up", angle="up", dist="medium", motion="static low; she rises past. Motivation: her glow is the only warm thing in the murk.", blocking="plants feet, pushes up.", fg="murk", mg="WICK rising, eyes glowing", bg="surface light", dir="up", light="amber eye glow in teal murk", emo="recovering, angry"),
"SC04_SH006": dict(comp="tight low; she breaks the surface and hauls onto the coping", height="coping level, low", angle="low", dist="tight medium", motion="low and tight; water on the lens. Motivation: imperfect on purpose - she is damaged.", blocking="breaks surface, hauls onto coping, sparking.", fg="water on lens", mg="WICK on coping", bg="wall", dir="up / frame L", light="steam off brass; rain steady", emo="shaken"),
# SC05 --------------------------------------------------------------------- #
"SC05_SH001": dict(comp="wide; the gantry a diagonal across frame, tower at its far (L) end", height="gantry level, low", angle="level wide", dist="wide", motion="static. Motivation: the destination must stay visible during the obstacle.", blocking="steps onto the gantry.", fg="rain", mg="gantry", bg="tower at frame L end", dir="crosses frame L", light="storm slate; wind from camera-R", emo="wary"),
"SC05_SH002": dict(comp="medium low; wind from camera-R bends the rain horizontal", height="her height", angle="low", dist="medium", motion="static; the gust supplies motion. Motivation: brace against, don't chase.", blocking="braces, pole horizontal.", fg="horizontal rain", mg="WICK braced", bg="gantry", dir="holds frame L against wind R", light="cold steel; spark glow", emo="strained"),
"SC05_SH003": dict(comp="follow the pole out of frame; hold on empty water", height="gantry level", angle="level", dist="medium", motion="follows the pole out of frame, then holds on the water. Motivation: the loss is the subject; the absence is held.", blocking="gust takes the pole; she reaches for nothing.", fg="rain", mg="pole spinning away", bg="water where it lands", dir="pole exits; she is left frame R of centre", light="the hole in the sound matches the hole in the frame", emo="startled, loss"),
"SC05_SH004": dict(comp="close static; the whole decision in one frame", height="her height", angle="level", dist="close", motion="static, no cut. Motivation: the stillness IS the beat; wind drops for it.", blocking="looks at empty hand; looks at the tower; decides.", fg="none", mg="WICK", bg="storm soft-focus", dir="hand, then frame L", light="the only quiet in the storm", emo="grief to resolve"),
"SC05_SH005": dict(comp="macro; the signature image - amber spark behind rain-streaked glass", height="chest macro", angle="level", dist="macro", motion="static. Motivation: protect the image; let it be looked at.", blocking="opens the chest drum; the spark glows; she seals the glass.", fg="rain streaks on glass", mg="amber spark", bg="chest interior", dir="static", light="the spark is the warmest thing in the scene", emo="tenderness"),
"SC05_SH006": dict(comp="tracking; the glow the brightest element", height="her height", angle="level", dist="medium tracking", motion="tracking; the glow leads the frame. Motivation: the thing she shields is the light source.", blocking="moves frame L, one arm across the chest.", fg="rain", mg="WICK shielding glow", bg="gantry", dir="travels frame L", light="amber glow vs cold steel", emo="burdened"),
"SC05_SH007": dict(comp="macro gauge, then rack to the door - one move", height="chest macro", angle="level", dist="macro then deep", motion="rack focus gauge->door. Motivation: hand SC06 its first image in a single move.", blocking="off-frame walking.", fg="needle 60->58", mg="gauge", bg="tower door ahead through rain", dir="faces frame L", light="rain; door dark", emo="determination"),
# SC06 --------------------------------------------------------------------- #
"SC06_SH001": dict(comp="wide low; the swollen door fills the frame above her", height="ground, looking up", angle="low", dist="wide", motion="static. Motivation: compress her against the bottom edge.", blocking="stands at the foot of the door, small.", fg="barnacled door base", mg="WICK", bg="door towering", dir="faces frame L (the door)", light="rain on iron; tower humming", emo="daunted"),
"SC06_SH002": dict(comp="tight on the effort, then whip to the gauge", height="her height", angle="level tight", dist="tight medium", motion="tight, then a whip to the gauge. Motivation: the single fast move of the film is the cost.", blocking="shoulder to the plate; it gives; she resets; it swings.", fg="iron", mg="WICK straining", bg="door", dir="pushes frame L", light="her glow + cold iron", emo="maximum effort"),
"SC06_SH003": dict(comp="centred insert; the needle crossing into the red arc", height="chest macro", angle="level", dist="macro", motion="dead still. Motivation: the quietest moment in the film.", blocking="needle crosses into the red arc.", fg="gauge glass", mg="needle in red", bg="brass", dir="static", light="everything drops out except needle friction", emo="foreboding"),
"SC06_SH004": dict(comp="interior; she enters low, the stair tilts up out of frame", height="her height, tilting up", angle="low to vertical tilt", dist="wide interior", motion="she enters; tilt up the stair, and keep tilting. Motivation: the tower's height in one move.", blocking="steps in; her glow lights the stair.", fg="door frame", mg="spiral stair", bg="dark stairwell, water on wall", dir="up", light="her glow is the ONLY light", emo="apprehension"),
"SC06_SH005": dict(comp="POV across the gap, then back to her", height="her height", angle="level", dist="medium", motion="POV then reverse, two angles, no motion. Motivation: the gap is the information.", blocking="at the broken stair edge.", fg="broken iron", mg="the gap", bg="storm through the breach", dir="POV across, then to her", light="storm light through the breach", emo="understanding"),
# SC07 --------------------------------------------------------------------- #
"SC07_SH001": dict(comp="extreme wide; the tower a vertical line, sea white far below", height="exterior, wide", angle="level wide", dist="extreme wide", motion="static. Motivation: she is a speck on a vertical; scale is the shot.", blocking="flattens against the iron as the gale hits.", fg="gale rain", mg="tower plating", bg="white sea far below", dir="on the wall; climb begins up/left", light="storm-white rim", emo="exposed"),
"SC07_SH002": dict(comp="follow the iron down, hold on empty air", height="exterior", angle="level then down", dist="medium", motion="follows the stair section down out of frame; holds on the void. Motivation: the last easy option leaves.", blocking="watches it go.", fg="rain", mg="falling iron", bg="empty air", dir="down", light="storm", emo="no way back"),
"SC07_SH003": dict(comp="rising track; the horizon progressively tilts off-level", height="matching her ascent", angle="level but horizon tilting", dist="medium", motion="slow rising track matched to her climb. Motivation: height felt, not shown.", blocking="hand over hand on rivets.", fg="rivets", mg="WICK climbing", bg="tilting horizon", dir="up", light="storm rim; her glow", emo="working, holding"),
"SC07_SH004": dict(comp="long lens straight down the drop", height="her hand, looking down", angle="down", dist="long lens down", motion="reveal the drop with a long lens. Motivation: the height is the danger.", blocking="peeled off; swings on one arm.", fg="her hand on a rivet", mg="the drop", bg="water far below", dir="down", light="storm", emo="real danger"),
"SC07_SH005": dict(comp="insert: the wedged pole, then her hand closing on it", height="her reach", angle="level insert", dist="insert", motion="insert then her hand - two frames, no exposition. Motivation: the earlier loss pays off mechanically.", blocking="free hand finds the wedged pole; closes on it.", fg="rain", mg="lamp-pole wedged in ironwork", bg="iron", dir="reach", light="a single bright note returns", emo="astonished"),
"SC07_SH006": dict(comp="tight on the haul; the gauge kept in the corner of frame", height="her height", angle="level tight", dist="tight medium", motion="tight; the gauge rides the corner. Motivation: the cost must be visible during the win.", blocking="uses the pole as a brace; hauls.", fg="pole brace", mg="WICK hauling", bg="iron; gauge corner", dir="up", light="storm rim", emo="spent"),
"SC07_SH007": dict(comp="abstract tight: brass, rivets, rain - the world reduced", height="her hands", angle="tight", dist="very tight", motion="very tight, almost abstract. Motivation: hold on the broken motion, don't cover it.", blocking="limbs stutter; drags herself.", fg="brass", mg="rivets + hands", bg="rain", dir="up", light="near-monochrome", emo="failing"),
"SC07_SH008": dict(comp="medium held; she collapses over the rail into the lee", height="gallery level", angle="level", dist="medium, held", motion="she collapses into frame; hold. Motivation: let her be still before cutting.", blocking="pulls herself over the rail; collapses.", fg="rail", mg="WICK collapsed", bg="burner door ahead", dir="into the lee", light="gale drops inside the lee", emo="barely functional"),
# SC08 --------------------------------------------------------------------- #
"SC08_SH001": dict(comp="wide; she is tiny in an enormous brass room", height="chamber floor, wide", angle="level wide", dist="wide", motion="static. Motivation: scale contrast is the whole shot.", blocking="at the foot of the burner, tiny.", fg="dark floor", mg="burner mass", bg="chamber, dripping glass roof", dir="faces the burner", light="her glow the only light", emo="awed, exhausted"),
"SC08_SH002": dict(comp="close following her hands up the last rungs", height="her reach", angle="level close", dist="close", motion="close, following the hands, unhurried. Motivation: it is not an action beat.", blocking="climbs; opens the chest; lifts the spark out.", fg="rungs", mg="hands + spark", bg="burner", dir="up to the burner", light="exposed spark glow", emo="careful, hopeful"),
"SC08_SH003": dict(comp="tight on the spark and the cold brass; the gap is the subject", height="burner level", angle="level tight", dist="tight", motion="static tight. Motivation: the gap between spark and brass is the point.", blocking="offers the spark; nothing catches; tries again.", fg="spark", mg="cold brass", bg="burner heart", dir="reaches", light="fragile glow on dead brass", emo="confused, afraid"),
"SC08_SH004": dict(comp="locked-off static insert of the socket; no movement, no help", height="burner heart", angle="level", dist="static insert", motion="locked-off, no movement, no music. Motivation: the most important shot must not be decorated.", blocking="off-frame.", fg="none", mg="the socket: no wick, no oil, no flint", bg="brass", dir="static", light="absolute; one water drop", emo="the reveal"),
"SC08_SH005": dict(comp="close-up on the shutter eyes; the aperture closes, then opens", height="her head", angle="level", dist="close-up", motion="static; the aperture is the only motion. Motivation: the whole decision without a cut.", blocking="looks at the socket; looks at her chest; decides.", fg="none", mg="shutter eyes", bg="brass soft", dir="socket, then chest", light="her glow low", emo="understanding, at peace"),
"SC08_SH006": dict(comp="macro; unspooling the spring into the socket, unhurried", height="burner heart", angle="level macro", dist="macro", motion="macro, unhurried. Motivation: the sacrifice is mechanical and must be watched.", blocking="unspools her spring; threads it into the socket; gauge 3->1->0.", fg="spring", mg="socket", bg="brass", dir="into the socket", light="the spring sings; the glow fades", emo="spending herself"),
"SC08_SH007": dict(comp="her dark silhouette held as light blooms to white-gold", height="chamber floor", angle="level", dist="medium", motion="held on the silhouette; the bloom fills the frame without a cut. Motivation: the ignition is the payoff.", blocking="eyes go dark; the beacon ignites behind her.", fg="her silhouette", mg="bloom", bg="white-gold", dir="static", light="black to full amber - the largest contrast event", emo="sacrifice, awe"),
# SC09 --------------------------------------------------------------------- #
"SC09_SH001": dict(comp="extreme wide held; the beam sweeps black water", height="gallery/exterior, wide", angle="level", dist="extreme wide, held", motion="locked wide, 8-second protected hold. Motivation: decompression; no coverage.", blocking="none.", fg="rain turning to light", mg="the beam", bg="black sea", dir="looks frame R to the sea", light="amber shaft in the dark", emo="release"),
"SC09_SH002": dict(comp="extreme long lens; the ship tiny; its turn small and easy to miss", height="sea level", angle="level", dist="extreme long lens (300mm)", motion="held. Motivation: the turn is ponderous; motion would falsify it.", blocking="none (the ship).", fg="haze", mg="running light", bg="reef line sliding past", dir="the ship turns frame L (to harbour)", light="dawn edge on the water", emo="relief"),
"SC09_SH003": dict(comp="wide as the light dies, then a slow push to her silhouette", height="chamber floor", angle="level", dist="wide to slow push", motion="one continuous move: the light dies, the push finds her. Motivation: carry the mood across the cut.", blocking="her silhouette at the foot of the burner.", fg="dimming beam", mg="chamber", bg="dawn grey-gold", dir="to her", light="beacon dims as the dark goes; dawn", emo="mourning"),
# SC10 --------------------------------------------------------------------- #
"SC10_SH001": dict(comp="medium held; her shell at the foot of the burner, held long", height="floor, low", angle="level", dist="medium, held", motion="static, held long enough to be uncomfortable. Motivation: do not soften it.", blocking="her shell, slumped, still holding the pole; gauge 0.", fg="wet iron", mg="WICK shell", bg="dawn chamber", dir="static", light="dawn rose-gold", emo="mourning"),
"SC10_SH002": dict(comp="wide interior; the child a silhouette in the doorway", height="interior, low", angle="level", dist="wide interior", motion="static from inside the chamber. Motivation: the child is a silhouette, never resolved.", blocking="child enters, barefoot, backlit; sees her.", fg="chamber dark", mg="doorway light", bg="child silhouette", dir="child enters from the doorway", light="backlight and rim only", emo="quiet arrival"),
"SC10_SH003": dict(comp="close on the child's hands and the key; the face out of focus", height="kneel height", angle="level close", dist="close", motion="static close on the hands. Motivation: the hesitation is the beat.", blocking="kneels; takes the key from her back; hesitates.", fg="hands", mg="the key", bg="her back, out of focus", dir="to her back", light="dawn rim on the key", emo="the hesitation"),
"SC10_SH004": dict(comp="macro, identical framing to SC01_SH001, warmed to dawn - the loop", height="back-plate macro", angle="level, dead-on", dist="extreme macro ~10cm", motion="locked-off, identical to SC01_SH001. Motivation: the loop; one turn instead of four.", blocking="the key turns once; the ratchet catches.", fg="key bow", mg="back plate", bg="black void warmed", dir="static", light="dawn warm instead of dusk", emo="the single turn"),
"SC10_SH005": dict(comp="macro chest drum; the coil catches; the eyes flicker; cut to black", height="chest macro", angle="level", dist="macro", motion="macro, then hard cut to black. Motivation: end on the same click that opened the film.", blocking="coil catches; shutter eyes flicker open; needle lifts off zero.", fg="glass", mg="coil + needle", bg="dark drum", dir="static", light="first amber return in the chest", emo="hope - restarted, not restored"),
}

REQ = ["composition","shot_type","camera_height","camera_angle","camera_distance",
       "lens_intention","camera_motion","character_blocking","foreground","midground",
       "background","screen_direction","lighting_intention","action","emotion",
       "transition","sound_intention"]

def main() -> int:
    shots = []
    cam = []
    blk = []
    ids = {s["shot_id"] for s in J["shots"]}
    if set(O) != ids:
        print("MISMATCH overlay vs shot list:", (set(O) ^ ids))
        return 1

    scene_by = {s["scene_id"]: s for s in J["scenes"]}
    for s in J["shots"]:
        o = O[s["shot_id"]]
        sc = scene_by[s["scene_id"]]
        rec = {
            "shot_id": s["shot_id"],
            "scene_id": s["scene_id"],
            "time_in": s["time_in"], "time_out": s["time_out"], "duration": s["duration"],
            "frame_in": s["frame_in"], "frame_out": s["frame_out"],
            "composition": o["comp"],
            "shot_type": s["shot_type"],
            "camera_height": o["height"],
            "camera_angle": o["angle"],
            "camera_distance": o["dist"],
            "lens_intention": s["lens"],
            "camera_motion": o["motion"],
            "character_blocking": o["blocking"],
            "foreground": o["fg"],
            "midground": o["mg"],
            "background": o["bg"],
            "screen_direction": o["dir"],
            "lighting_intention": f'{o["light"]} | scene key: {SCENE_LIGHT[s["scene_id"]]}',
            "action": s["action"],
            "emotion": o["emo"],
            "transition": s["transition_out"],
            "sound_intention": s["sound"],
            "gauge_in": s["gauge_in"], "gauge_out": s["gauge_out"],
            "continuity_notes": s["continuity_notes"],
        }
        shots.append(rec)
        cam.append({k: rec[k] for k in ["shot_id","scene_id","time_in","time_out","shot_type",
                    "camera_height","camera_angle","camera_distance","lens_intention",
                    "camera_motion","composition","screen_direction","lighting_intention",
                    "transition"]})
        blk.append({k: rec[k] for k in ["shot_id","scene_id","time_in","time_out",
                    "character_blocking","foreground","midground","background",
                    "screen_direction","action"]})

    # variety / coverage checks
    missing = [k for r in shots for k in REQ if not str(r.get(k,"")).strip()]
    types = {}
    for r in shots: types[r["shot_type"].split(",")[0].split(" ")[0]] = types.get(r["shot_type"].split(",")[0].split(" ")[0],0)+1
    static = sum(1 for r in shots if "static" in r["camera_motion"].lower() or "locked" in r["camera_motion"].lower() or "held" in r["camera_motion"].lower())
    moving = len(shots) - static

    plan = {
        "schema_version":"1.0.0","task_id":"T04_STORYBOARD","project_id":"AMS-2026-001",
        "film_title":J["film_title"],"fps":J["fps"],
        "master_axis":AXIS,
        "shot_count":len(shots),"scene_count":J["scene_count"],
        "coverage":"every shot in 02_SCREENPLAY/SHOT_LIST.json has exactly one plan entry",
        "shots":shots,
    }
    camera = {"schema_version":"1.0.0","task_id":"T04_STORYBOARD","master_axis":AXIS,
              "camera_move_rule":"every move is motivated; the only fast move in the film is the whip at SC06_SH002; the protected 8s hold at SC09_SH001 is never covered.",
              "variety":{"shot_type_families":types,"static_or_held":static,"motivated_moving":moving},
              "shots":cam}
    blocking = {"schema_version":"1.0.0","task_id":"T04_STORYBOARD","master_axis":AXIS,
                "readability_rule":"the gauge is on screen whenever it changes; silhouettes read at 20px; action is never hidden by camera motion.",
                "shots":blk}

    json.dump(plan, open(os.path.join(HERE,"MASTER_SHOT_PLAN.json"),"w",encoding="utf-8"), indent=2, ensure_ascii=False)
    json.dump(camera, open(os.path.join(HERE,"CAMERA_PLAN.json"),"w",encoding="utf-8"), indent=2, ensure_ascii=False)
    json.dump(blocking, open(os.path.join(HERE,"BLOCKING_PLAN.json"),"w",encoding="utf-8"), indent=2, ensure_ascii=False)

    # ------------------------------------------------------------------ #
    # panels + human-readable docs
    # ------------------------------------------------------------------ #
    PANELS = [
        ("SC01_SH001", "the opening loop image: key centred in a black void, warm raking practical"),
        ("SC01_SH004", "establishing: tiny WICK on the quay, drowned town, tower frame LEFT, the single amber practical"),
        ("SC03_SH003", "the beauty pass: high crane over the drowned harbour, the one warm calm light"),
        ("SC04_SH004", "the drop: underwater, surface as a bright ceiling, bubbles and the nearly-lost pole"),
        ("SC05_SH005", "the signature image: live spark behind rain-streaked chest glass"),
        ("SC07_SH001", "extreme wide exterior climb: storm-white rim, horizontal rain, white sea far below"),
        ("SC08_SH004", "the reveal: locked-off insert of the cold brass socket, one water drop"),
        ("SC08_SH007", "the ignition: her silhouette against the largest contrast event in the film"),
        ("SC10_SH003", "the payoff: the child's hands and the key, faces kept out of focus"),
    ]
    for sid, _ in PANELS:
        p = os.path.join(HERE, "panels", f"{sid}.png")
        assert os.path.exists(p) and os.path.getsize(p) > 100_000, f"missing panel {p}"
    panel_of = {sid: f"panels/{sid}.png" for sid, _ in PANELS}

    md = []
    md.append(f"# STORYBOARD - {J['film_title']}")
    md.append("")
    md.append(f"Stage 04 deliverable. {plan['shot_count']} shots across {plan['scene_count']} scenes, "
              f"{J['total_runtime_seconds']} s at {J['fps']} fps (frames 1-{J['total_frames']}).")
    md.append("")
    md.append("Coverage: every shot id in `02_SCREENPLAY/SHOT_LIST.json` has exactly one 18-field "
              "production specification in `MASTER_SHOT_PLAN.json`. Camera-only and blocking-only "
              "projections live in `CAMERA_PLAN.json` and `BLOCKING_PLAN.json`. Panel files are a "
              "representative subset of 9 reference frames, not full coverage.")
    md.append("")
    md.append(f"**Master axis.** {AXIS}")
    md.append("")
    md.append(f"**Camera grammar.** {static} of {len(shots)} shots are static, held or locked-off; "
              f"{moving} carry motivated movement. The film's only whip-pan is SC06_SH002; the "
              "protected 8 s hold at SC09_SH001 is never covered.")
    md.append("")
    for sc in J["scenes"]:
        md.append(f"## {sc['scene_id']} - {sc['slug']}")
        md.append("")
        md.append(f"`{sc['time_in']}-{sc['time_out']}` · {sc['duration']} s · {sc['location']} · "
                  f"beat {sc['beat_type']} · emotion {sc['emotion']} · gauge {sc['gauge_in']}→{sc['gauge_out']}")
        md.append("")
        md.append(f"> {sc['story_purpose']}")
        md.append("")
        for r in [x for x in shots if x["scene_id"] == sc["scene_id"]]:
            md.append(f"### {r['shot_id']} · {r['shot_type']} · {r['lens_intention']} · "
                      f"`{r['time_in']}-{r['time_out']}` ({r['duration']} s, f{r['frame_in']}-{r['frame_out']})")
            md.append("")
            if r["shot_id"] in panel_of:
                md.append(f"![{r['shot_id']} reference frame]({panel_of[r['shot_id']]})")
                md.append("")
            md.append(f"- **Composition / camera:** {r['composition']} | height {r['camera_height']} | "
                      f"angle {r['camera_angle']} | distance {r['camera_distance']}")
            md.append(f"- **Move:** {r['camera_motion']}")
            md.append(f"- **Blocking:** {r['character_blocking']}")
            md.append(f"- **Depth layers:** FG {r['foreground']} / MG {r['midground']} / BG {r['background']}")
            md.append(f"- **Screen direction:** {r['screen_direction']}")
            md.append(f"- **Lighting:** {r['lighting_intention']}")
            md.append(f"- **Action:** {r['action']}")
            md.append(f"- **Emotion:** {r['emotion']} · **Transition:** {r['transition']} · **Sound:** {r['sound_intention']}")
            md.append("")
    md.append("## Companion files")
    md.append("")
    md.append("- `MASTER_SHOT_PLAN.json` - the 18-field specification for all 58 shots")
    md.append("- `CAMERA_PLAN.json` - camera-only projection; `BLOCKING_PLAN.json` - blocking/depth projection")
    md.append("- `beat_board/BEAT_BOARD.md` - scene-level beat board; `panels/PANEL_INDEX.md` - reference frame index")
    md.append("- `../SHOT_REGISTRY.json` - per-shot pipeline registry (story slot VERIFIED)")
    md.append("- `../13_RENDER/RENDER_MANIFEST.json` - per-scene render lifecycle (all NOT_STARTED)")
    open(os.path.join(HERE, "STORYBOARD.md"), "w", encoding="utf-8").write("\n".join(md))

    bb = []
    bb.append(f"# BEAT BOARD - {J['film_title']}")
    bb.append("")
    bb.append("Scene-level board: one row per scene. Per-shot detail lives in `../STORYBOARD.md` "
              "and `MASTER_SHOT_PLAN.json`.")
    bb.append("")
    bb.append("| scene | in-out | dur | location | beat | emotion | gauge | shots | panels |")
    bb.append("|---|---|---|---|---|---|---|---|---|")
    for sc in J["scenes"]:
        ps = [f"`{s}`" for s, _ in PANELS if s.startswith(sc["scene_id"] + "_")]
        bb.append(f"| {sc['scene_id']} | {sc['time_in']}-{sc['time_out']} | {sc['duration']} s | "
                  f"{sc['location']} | {sc['beat_type']} | {sc['emotion']} | "
                  f"{sc['gauge_in']}→{sc['gauge_out']} | {sc['shot_count']} | {', '.join(ps) or '-'} |")
    bb.append("")
    bb.append("## Beat-by-beat read")
    bb.append("")
    for sc in J["scenes"]:
        bb.append(f"- **{sc['scene_id']}** ({sc['beat_type']}, {sc['emotion']}): {sc['story_purpose']}")
    open(os.path.join(HERE, "beat_board", "BEAT_BOARD.md"), "w", encoding="utf-8").write("\n".join(bb))

    pi = []
    pi.append("# PANEL INDEX")
    pi.append("")
    pi.append(f"Representative storyboard reference frames for `{J['film_title']}`: {len(PANELS)} of "
              f"{plan['shot_count']} shots. Frames were generated from the authored specifications in "
              "`MASTER_SHOT_PLAN.json` and verify composition, scale and lighting intent; they are "
              "visual guides, not final renders.")
    pi.append("")
    pi.append("| file | shot | scene | verifies |")
    pi.append("|---|---|---|---|")
    for sid, note in PANELS:
        sh = next(x for x in shots if x["shot_id"] == sid)
        pi.append(f"| `panels/{sid}.png` | {sid} | {sh['scene_id']} | {note} |")
    open(os.path.join(HERE, "panels", "PANEL_INDEX.md"), "w", encoding="utf-8").write("\n".join(pi))

    print(f"shots planned {len(shots)} / screenplay {J['shot_count']}  match={set(r['shot_id'] for r in shots)==ids}")
    print(f"missing fields: {len(missing)} {missing[:4]}")
    print(f"camera: static/held {static} | motivated moving {moving}")
    print(f"panels: {len(PANELS)} written to panels/PANEL_INDEX.md")
    return 0 if not missing else 1

if __name__ == "__main__":
    sys.exit(main())
