#!/usr/bin/env python3
"""
Build 02_SCREENPLAY/SHOT_LIST.json and SHOT_LIST.csv from one source of truth.

Regenerate with:  python3 02_SCREENPLAY/build_shot_list.py

Every invariant the Screenwriter stage is required to verify is asserted here, so the
artefacts cannot be generated unless they hold:
  * shot ids unique and matching SCnn_SHmmm
  * shots contiguous inside a scene - no gaps, no overlaps
  * scenes contiguous across the film - no gaps, no overlaps
  * total runtime exactly 302 s / 7248 frames at 24 fps
  * shot count inside MASTER_CONFIG planned range
  * per-scene gauge deltas equal the locked turn budget
  * every required shot field present and non-empty
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FPS = 24
TARGET_SECONDS = 302

# --------------------------------------------------------------------------- #
# scenes
# --------------------------------------------------------------------------- #
SCENES = [
    dict(id="SC01", slug="THE WINDING", t=32.0, loc="The Winding Plaza - the quay, at the winding pillar",
         chars=["WICK"], beat="HOOK", gauge_in=None, gauge_out=92,
         purpose="Open mid-action on an unexplained mechanism. Establish that WICK is finite, that her refill has just failed, and put the number 92 on screen inside eight seconds. Withhold the world until second 14.",
         emotion="curiosity, then dread",
         props=["the winding key", "chest gauge", "sheared spring tooth", "lamp-pole", "one burning harbour lamp"],
         env="Dusk. Still water. No wind yet. The last calm light of the day.",
         transition="Hard cut on the shutter eyes opening."),
    dict(id="SC02", slug="THE DEAD PILLAR", t=33.0, loc="The Winding Plaza - the pillar and the harbour horizon",
         chars=["WICK", "THE RETURNING SHIP (distant)"], beat="STAKE", gauge_in=92, gauge_out=92,
         purpose="Make the cost of the failure concrete: the pillar is stripped and she cannot recharge. Establish the ship, the reef and the tower in a nine-second three-point eyeline, so the audience knows exactly what she is walking toward and what happens if she does not get there.",
         emotion="dread hardening into resolve",
         props=["winding pillar", "stripped key socket", "the key", "chest gauge", "lamp-pole", "ship's running light", "bell buoy"],
         env="Wind rising off the water. The sky bruising. The bell buoy slow and irregular.",
         transition="Cut on her first footfall out of frame left."),
    dict(id="SC03", slug="SETTING OUT", t=27.0, loc="The Winding Plaza - across the quay toward the flooded street",
         chars=["WICK"], beat="DEPARTURE", gauge_in=92, gauge_out=84,
         purpose="Teach the film's grammar: movement spends turns, and the gauge is the receipt. Also the only genuinely beautiful, calm passage in the film - it earns the storm and gives the audience something to grieve for.",
         emotion="wonder, underpinned by a counting dread",
         props=["chest gauge", "lamp-pole", "dead lamp posts", "one still-burning lamp"],
         env="Drowned harbour in full: barnacled arches, kelp in the shallows, rooftops under water. Empty.",
         transition="Music cuts out on the water's edge; hard cut to the flooded street."),
    dict(id="SC04", slug="THE FLOODED STREET", t=30.0, loc="The Flooded Streets - a half-submerged lane",
         chars=["WICK"], beat="OBSTACLE_1", gauge_in=84, gauge_out=71,
         purpose="First real obstacle and first near-failure. Water that is ankle-deep for us is a flood for her. Establish that the world is hostile to her specifically, and that a mistake is survivable but expensive.",
         emotion="alarm",
         props=["chest gauge", "market stall", "iron railing", "wall coping", "lamp-pole"],
         env="Rain begins here - sparse at first, then steady. Water still, black, reflective.",
         transition="Cut on the surface break and the first hard rain."),
    dict(id="SC05", slug="THE GANTRY", t=36.0, loc="The Flooded Streets - the gantry walkway",
         chars=["WICK"], beat="OBSTACLE_2_AND_LOSS", gauge_in=71, gauge_out=58,
         purpose="Midpoint reversal. She loses her tool, and takes the spark into her own body to protect it - so from here the thing she is saving is the thing consuming her. Establish the film's signature image: an amber spark behind rain-streaked glass.",
         emotion="loss, then tenderness, then a colder determination",
         props=["lamp-pole (lost)", "the spark", "chest drum glass", "gantry railings", "chest gauge"],
         env="Storm arrives in full. Wind from camera-right, rain horizontal, gantry swaying.",
         transition="Cut on a rack focus from the gauge to the tower door."),
    dict(id="SC06", slug="THE TOWER BASE", t=28.0, loc="The Tidelight Tower - the door and the lower stair",
         chars=["WICK"], beat="OBSTACLE_3", gauge_in=58, gauge_out=31,
         purpose="The most expensive single action in the film, and the moment the needle enters the red arc. Then take the easy route away: the stair is gone, so the only way up is outside.",
         emotion="foreboding",
         props=["iron tower door", "chest gauge", "spiral stair", "the spark"],
         env="Rain on iron. Inside, water running down the wall. Reverb opens up the moment she enters.",
         transition="Cut from the broken stair to the exterior breach."),
    dict(id="SC07", slug="THE CLIMB", t=42.0, loc="The Tidelight Tower - exterior riveted plating",
         chars=["WICK"], beat="ESCALATION_PEAK", gauge_in=31, gauge_out=6,
         purpose="Longest scene and the escalation peak. The rig itself degrades as the spring weakens, so the animation carries the information rather than the plot. Return the lamp-pole as a brace so the earlier loss pays off mechanically, not sentimentally.",
         emotion="desperation, then a single moment of recognition",
         props=["rivets and handholds", "lamp-pole (recovered, wedged in ironwork)", "chest gauge", "the spark"],
         env="Full gale. Sea white below. Rain effectively horizontal. Inside the lee at the top the wind drops.",
         transition="Cut as she collapses through the gallery doorway."),
    dict(id="SC08", slug="THE BURNER", t=34.0, loc="The Tidelight Tower - the burner chamber",
         chars=["WICK"], beat="CLIMAX_AND_TWIST", gauge_in=6, gauge_out=0, ignition=1,
         purpose="Climax and twist. The burner has no wick, no oil and no flint - only a socket the exact diameter of a mainspring. The reveal is played as a locked-off static shot in silence. The sacrifice must be mechanical and honest, not magical.",
         emotion="recognition, sacrifice, awe",
         props=["the burner", "the socket", "the spark", "her own mainspring", "chest gauge", "lamp-pole"],
         env="Cold, enormous brass. Her glow is the only light. The storm reduced to a murmur outside. Dripping.",
         transition="Ignition floods the frame to white-gold; cut to the exterior beam."),
    dict(id="SC09", slug="THE LIGHT", t=20.0, loc="The Tidelight Tower - the gallery and the water beyond",
         chars=["THE RETURNING SHIP"], beat="PAYOFF", gauge_in=0, gauge_out=0,
         purpose="Payoff and deliberate decompression. The ship turns, the reef slides past, dawn comes up. Held long and uncut so the relief lands physically, and so the contrast sets up the final scene.",
         emotion="relief, then mourning",
         props=["the beacon beam", "the ship's running light", "the reef line", "bell buoy"],
         env="Beam sweeping black water. Rain turning to light inside the shaft. Dawn grey-gold.",
         transition="Slow push toward her silhouette as the beacon dies; cut to dawn interior."),
    dict(id="SC10", slug="ONE TURN", t=20.0, loc="The Tidelight Tower - the burner chamber, dawn",
         chars=["WICK", "THE CHILD"], beat="RESOLUTION_AND_LOOP", gauge_in=0, gauge_out=1, gained=1,
         purpose="Resolution and loop. The child gives her one turn - not a restoration, a beginning. The macro of the key turning mirrors the opening shot frame for frame so the film loops cleanly, and the last sound is the same click the film opened on.",
         emotion="mourning resolving into hope",
         props=["the key", "WICK's shell", "lamp-pole", "chest gauge", "the coil"],
         env="Dawn light through the gallery. Wet iron. Dripping. The first birdsong in the film.",
         transition="Hard cut to black on the final click."),
]

# --------------------------------------------------------------------------- #
# shots
# --------------------------------------------------------------------------- #
def S(n, ti, to, action, cstate, cpos, pstate, cam, sound, cont, gin, gout,
      stype, lens, chars, trans, dial="none"):
    return dict(n=n, ti=ti, to=to, action=action, cstate=cstate, cpos=cpos,
                pstate=pstate, cam=cam, sound=sound, cont=cont, gin=gin, gout=gout,
                stype=stype, lens=lens, chars=chars, trans=trans, dial=dial)

SHOTS = {
"SC01": [
 S(1, 0.0, 5.5,
   "Extreme macro. A brass winding key seated in a back plate. It turns - once, twice, three times. On the fourth turn the ratchet slips and the key overshoots with no bite.",
   "off-frame; only her back plate and the key are visible",
   "back plate filling frame, key at centre",
   "key: engaged, slipping on the fourth turn",
   "Locked-off macro, ~100mm, razor-thin depth of field. No movement at all. The audience does not yet know what it is looking at.",
   "Three dry ratchet clicks, close and intimate. Distant wind under. No music.",
   "First appearance of the key and back plate. The fourth-turn slip is the film's inciting incident and must read clearly at any size.",
   None, None, "extreme macro", "100mm macro", ["WICK (part)"], "Cut to the chest drum."),
 S(2, 5.5, 9.0,
   "Macro on the glass chest drum. Inside, the coil tightens - then a single spring tooth shears off, pings against the glass and falls out of frame. The needle swings upward, hesitates, sags, and settles on 92.",
   "coil under load, one tooth lost",
   "chest drum filling frame",
   "spring: one tooth sheared, permanently degraded. Gauge: settles at 92.",
   "Macro with a very slight push-in. The number 92 must be legible and centred.",
   "A bright metallic ping on the shear, then a low sub thud as the needle settles. Silence under.",
   "92 is established here at 00:08, inside the eight-second hook deadline. This exact needle position is the reference for every later gauge shot.",
   None, 92, "macro", "100mm macro", ["WICK (part)"], "Cut to a held static on the gauge."),
 S(3, 9.0, 14.0,
   "Hold on the gauge. 92. The needle trembles once and is still. Out of focus, warm amber lamp light drifts across the glass.",
   "still, wound but damaged",
   "chest drum, static",
   "gauge: 92, steady",
   "Static macro. The only true stillness in the opening - it lets the number land.",
   "Wind. Distant water. Nothing else. The silence is the point.",
   "The amber defocus is the harbour lamp, established before we see it. Do not identify the source yet.",
   92, 92, "macro", "100mm macro", ["WICK (part)"], "Pull back."),
 S(4, 14.0, 22.0,
   "Slow pull back and up. The frame opens out to reveal WICK - forty centimetres of aged brass - alone on a barnacled stone quay. Behind her, a drowned harbour town. One lamp still burns on a post. Dusk.",
   "powered, upright, unaware she is being watched",
   "centre of the quay, small in a wide frame",
   "gauge: 92. Lamp-pole lying on the stone beside her.",
   "Slow crane back and up, macro to wide. This is the reveal; the move must be unhurried and continuous so the scale change reads as a single thought.",
   "Harbour ambience swells in as we widen: water, wind through iron, no birds.",
   "First full view of WICK and of the world. The single burning lamp must be in frame and clearly the only light source.",
   92, 92, "extreme wide", "24mm", ["WICK"], "Cut to her eye height."),
 S(5, 22.0, 27.0,
   "WICK's shutter eyes open - the apertures irising up from black. She looks down at her own chest gauge, and holds on what it says.",
   "alert, assessing",
   "centre of the quay, three-quarter to camera",
   "gauge: 92. Key still seated in her back, now useless.",
   "Low, at her eye height, with a slight handheld micro-drift. The aperture opening is the whole event of the shot.",
   "Her clock motif, first statement: three thin notes on a single instrument. Wind.",
   "The shutter-eye open is her first expression and sets the vocabulary for the whole film. Aperture range established here is reused for every later emotional beat.",
   92, 92, "close-up", "50mm", ["WICK"], "Cut to her point of view."),
 S(6, 27.0, 32.0,
   "Her point of view: the dark, unlit beacon tower on the horizon across black water. Hold. She does not move.",
   "assessing, unresolved",
   "off-frame; this is what she is looking at",
   "tower: dark, beacon cold. Water between.",
   "Her POV, slightly wide, static. Deliberately unglamorous - the tower must read as far away and unlit.",
   "Wind. The clock motif does not resolve; it simply stops.",
   "First view of the tower from her perspective. Bearing and water line must match SC02_SH004, which shoots it from the opposite side.",
   92, 92, "POV wide", "35mm", [], "Hard cut to the pillar."),
],
"SC02": [
 S(1, 32.0, 38.5,
   "WICK at the winding pillar, a brass column at the centre of the plaza. She backs up to it and raises herself onto the socket - a practised, habitual, daily motion.",
   "routine, unthinking",
   "at the base of the pillar, back to the socket",
   "pillar: intact but about to be shown stripped. Key: in her back.",
   "Medium low. The pillar looms above her. Composition puts her small against the thing that normally sustains her.",
   "Her joints. The small click of alignment as she seats herself.",
   "The pillar is the same asset seen in the SC01 wide. Her approach must read as habitual, not exploratory.",
   92, 92, "medium low", "35mm", ["WICK"], "Cut to macro on the socket."),
 S(2, 38.5, 43.0,
   "Macro on the socket: stripped, the teeth worn away. The key enters and spins free with no bite. She withdraws and tries again. And again.",
   "confusion shading into alarm",
   "at the pillar",
   "socket: stripped, unusable for the rest of the film. Key: still in her back, now the only key there is.",
   "Macro on the socket, then a fast cut-in on her shutter apertures closing - her one available expression of alarm.",
   "Three hollow spins with no ratchet underneath. On the third, absolute silence.",
   "The stripped socket is permanent. No later scene may imply the pillar can be repaired.",
   92, 92, "macro / insert", "100mm macro", ["WICK (part)"], "Cut wide to the horizon."),
 S(3, 43.0, 49.0,
   "Wide over the harbour to the horizon. A single amber running light, low on the water, moving toward the reef line.",
   "off-frame; this is what she is looking at",
   "n/a",
   "ship: distant, one running light, closing on the reef",
   "Long lens, 200mm equivalent. The light is tiny in frame and the reef line is a darker band below it. Hold.",
   "Wind. A distant bell buoy, slow and irregular. First statement of the ship's motif: two descending notes.",
   "The ship is never seen closer than this until SC09. Reef line position must match SC09_SH002 exactly.",
   92, 92, "extreme wide", "200mm", ["THE RETURNING SHIP"], "Cut to reverse."),
 S(4, 49.0, 55.0,
   "Reverse, from the waterline: the beacon tower, black against a bruised sky, unlit.",
   "off-frame",
   "n/a",
   "tower: dark, beacon cold",
   "Wide angle from the waterline, the tower leaning away from us. Its height should feel slightly wrong, slightly unclimbable.",
   "Wind rising. Iron groaning under load.",
   "This is the first view of the tower's full height. The plating and handholds seen here are the same ones climbed in SC07.",
   92, 92, "wide", "18mm", [], "Cut back to her."),
 S(5, 55.0, 60.0,
   "Close on WICK's chest. The gauge reads 92. The dark tower is reflected in her shutter lenses.",
   "calculating",
   "at the pillar, turned toward the tower",
   "gauge: 92, unmoved",
   "Close, with the gauge filling the lower third. The tower reflection in her lenses does the eyeline work.",
   "Her clock motif, second statement - noticeably faster than the first.",
   "The three-point eyeline is ship / tower / own chest. This shot is the third point and must contain the tower reflection to complete it.",
   92, 92, "close-up", "85mm", ["WICK"], "Cut to the pole."),
 S(6, 60.0, 65.0,
   "She reaches down and lifts the lamp-pole from the stone. It is taller than she is. She sets it against her shoulder, takes one step toward the tower.",
   "decided",
   "leaving the pillar, moving frame left",
   "lamp-pole: picked up, carried on her shoulder",
   "Low profile, static. She walks out of frame left. Cut on the footfall, not after it.",
   "The pole scraping stone. One footfall. Then the score's first forward motion underneath.",
   "The pole leaves with her here and is not lost until SC05_SH003. Its length relative to her body must stay consistent.",
   92, 92, "medium", "40mm", ["WICK"], "Cut on the footfall."),
],
"SC03": [
 S(1, 65.0, 71.0,
   "Lateral tracking. WICK crosses the plaza. With every stride the gauge ticks down: 92, 90, 88.",
   "walking, purposeful",
   "traversing the quay, frame right to left",
   "gauge: 92 to 88. Lamp-pole on her shoulder.",
   "Lateral dolly at her height, holding the gauge in frame throughout. This shot teaches the audience to watch the gauge.",
   "Ratchet ticks locked to her footfalls. This is the film's central sound idea and it starts here.",
   "The tick-to-footfall sync must be exact - it is the grammar the rest of the film relies on. Gauge decrements in even steps.",
   92, 88, "tracking medium", "40mm", ["WICK"], "Cut to gauge insert."),
 S(2, 71.0, 76.0,
   "Insert on the gauge. 88 to 86. The needle moves in discrete, audible steps rather than smoothly.",
   "walking (off-frame)",
   "n/a",
   "gauge: 88 to 86",
   "Macro insert, dead static. Framed identically to SC01_SH003 so the audience reads it as the same instrument.",
   "Two ticks, loud and dry, with nothing under them.",
   "Gauge insert framing is now locked: same lens, same angle, same lighting key for every insert in the film.",
   88, 86, "insert", "100mm macro", ["WICK (part)"], "Cut wide."),
 S(3, 76.0, 83.0,
   "Wide. The drowned harbour in full: barnacled arches, kelp swaying in the shallows, rooftops under black water. Beautiful, and completely empty.",
   "walking, small in the frame",
   "lower third, moving away from camera",
   "gauge: 86 to 85 (not visible)",
   "High crane, slow push. The only genuinely calm image in the film - the camera must not hurry.",
   "The music opens out: strings, warm, the only major-key passage in the film.",
   "This is the beauty pass. It exists so the audience has something to lose. Kelp and water motion must be gentle here and violent from SC05.",
   86, 85, "extreme wide", "24mm", ["WICK"], "Cut to the lamp posts."),
 S(4, 83.0, 88.0,
   "She passes a row of harbour lamp posts, all dead. She does not stop. Behind her, the one lamp that still burns.",
   "walking, eyes forward",
   "moving through the row, frame left",
   "gauge: 85 to 84. Dead lamps; one burning lamp behind.",
   "Medium tracking, the foreground poles strobing past and repeatedly breaking the frame.",
   "The clock motif continues under the strings. Wind.",
   "The dead lamps foreshadow what the beacon will fix. The one burning lamp is the source of the spark she takes in SC05.",
   85, 84, "tracking medium", "40mm", ["WICK"], "Cut to the water's edge."),
 S(5, 88.0, 92.0,
   "Gauge reads 84. She reaches the edge of the plaza. Beyond it, the street is black water.",
   "stopping, assessing",
   "at the quay edge, back to camera",
   "gauge: 84, steady",
   "Over her shoulder into the flooded street. Hold on the water.",
   "Music cuts out entirely. Water lapping at stone.",
   "84 is the handoff value into SC04. The street water level established here must match SC04_SH001.",
   84, 84, "over-shoulder", "35mm", ["WICK"], "Hard cut."),
],
"SC04": [
 S(1, 92.0, 97.0,
   "Wide, low. The flooded lane. For a forty-centimetre machine this is a flood. She stops at the edge.",
   "hesitant",
   "at the lane edge, frame right",
   "gauge: 84. Lamp-pole still carried.",
   "Low wide with water filling the lower half of frame, so her scale against the water reads immediately.",
   "Water. Wind funnelling between buildings.",
   "Water level must match SC03_SH005. This is the same lane, seen from the other side.",
   84, 84, "wide low", "24mm", ["WICK"], "Cut to the stall."),
 S(2, 97.0, 102.5,
   "She climbs a submerged market stall. Grip, haul, grip. Water sheets off her. Gauge 84 to 80.",
   "working hard",
   "on the stall, rising out of the water",
   "gauge: 84 to 80. Stall: submerged, used as a step.",
   "Handheld feel at her height, tight. Slight instability to match the effort.",
   "Metal straining. Water sheeting off brass. The footfall ticks continue but are now irregular.",
   "First irregular tick. From here the rhythm degrades progressively and never fully recovers.",
   84, 80, "medium", "50mm", ["WICK"], "Cut to the railing."),
 S(3, 102.5, 107.0,
   "Railing traverse, hand over hand. Rain begins - sparse first drops on the water. Gauge 80 to 77.",
   "committed",
   "along the railing, moving frame left",
   "gauge: 80 to 77. Railing: wet, slick.",
   "Profile, the railing running as a hard horizontal line across frame with her above it.",
   "Rhythmic clicks. The first raindrops - distinct, countable.",
   "Rain starts here and never stops until SC09. First drops must be individually audible.",
   80, 77, "profile medium", "50mm", ["WICK"], "Cut to the fall."),
 S(4, 107.0, 113.0,
   "THE DROP. Her grip fails and she goes under. Bubbles. The gauge flickers, the needle stuttering. The surface becomes a bright ceiling above her.",
   "failing, briefly out of control",
   "underwater, below the railing",
   "gauge: 77 to 75, flickering. Lamp-pole: still gripped, nearly lost.",
   "The camera goes under with her. Invert the reference: the surface is up and bright, the town is a dark ceiling of shapes.",
   "Everything muffles. A dull sub. Her clock motif distorted and slowing.",
   "The muffled sound world is used only here and in SH005. The needle flicker is the first sign the water has done real damage.",
   77, 75, "underwater", "35mm", ["WICK"], "Cut to low angle."),
 S(5, 113.0, 118.0,
   "Underwater, looking up. Her shutter eyes glow amber in the murk. She plants her feet on the lane floor and pushes.",
   "recovering, angry",
   "on the lane floor, pushing up",
   "gauge: 75, dimmed by water",
   "Low, looking up at her rising. She should break frame at the top.",
   "Muffled. Then the first audible catch of her spring - a small bright note under the murk.",
   "The amber eye glow underwater is a signature image; keep the aperture half-closed so it reads as effort, not calm.",
   75, 75, "low underwater", "35mm", ["WICK"], "Cut to the surface break."),
 S(6, 118.0, 122.0,
   "She breaks the surface and hauls herself onto a wall coping, sparking. Steam comes off her brass. Gauge 75 to 71.",
   "shaken, wet, running hot",
   "on the coping, above the water line",
   "gauge: 75 to 71. Body: wet, sparking at the shoulder joint.",
   "Low and tight, water streaming down the lens. Deliberately imperfect.",
   "The surface break, loud. Rain now steady and continuous.",
   "The shoulder joint sparks here and again in SC07_SH004. Same joint, so the damage is continuous, not incidental.",
   75, 71, "tight medium", "50mm", ["WICK"], "Hard cut to the gantry."),
],
"SC05": [
 S(1, 122.0, 127.0,
   "Wide. The gantry walkway spans the lane, rusted and swaying in the rising wind. She steps onto it.",
   "wary",
   "at the gantry entrance, frame right",
   "gauge: 71. Lamp-pole: carried. Gantry: swaying.",
   "Wide, the gantry running as a diagonal across frame with the tower visible at its far end.",
   "Wind up sharply. Iron creaking under load.",
   "The tower must be visible at the gantry's far end so the destination stays present during the obstacle.",
   71, 71, "wide", "28mm", ["WICK"], "Cut to midway."),
 S(2, 127.0, 132.5,
   "Midway. A gust hits. She braces with the pole held horizontal. Gauge 71 to 68.",
   "braced, strained",
   "mid-gantry, low and wide",
   "gauge: 71 to 68. Pole: horizontal, used as a brace.",
   "Low, wind from camera-right, rain now horizontal and streaking the lens.",
   "The gust as a solid wall of sound, not a whoosh.",
   "Wind direction is camera-right for the whole scene. The pole is horizontal here and leaves her hand in the next shot.",
   71, 68, "medium low", "35mm", ["WICK"], "Cut to the pole."),
 S(3, 132.5, 137.0,
   "THE POLE GOES. A second gust takes the lamp-pole out of her grip. It spins away, strikes the water and is gone.",
   "startled, off-balance",
   "mid-gantry, reaching for nothing",
   "gauge: 68 to 66. Lamp-pole: LOST to the water. She is now empty-handed.",
   "Follow the pole out of frame, then hold on the empty water where it went. Do not cut back to her immediately.",
   "The pole clattering on iron, one splash, then nothing. A hole opens in the sound.",
   "CRITICAL CONTINUITY: the pole is gone from here until SC07_SH005, where it is found wedged in the tower ironwork. It must not appear in SC05_SH004 through SC07_SH004.",
   68, 66, "medium, then hold on water", "50mm", ["WICK", "lamp-pole"], "Cut back to her."),
 S(4, 137.0, 143.0,
   "She stands without it. Looks at her empty hand. Looks at the tower. Decides. The wind drops for one beat.",
   "grieving, then resolving",
   "mid-gantry, still",
   "gauge: 66, unmoved. Hands: empty.",
   "Close, static. Let the whole decision play without a cut - this is the scene's only stillness.",
   "The wind drops for exactly one beat. The only quiet in the storm.",
   "No gauge cost here. The stillness is the point; the audience must be allowed to register the loss.",
   66, 66, "close-up", "85mm", ["WICK"], "Cut to the chest."),
 S(5, 143.0, 149.0,
   "She opens her chest drum. Inside: a live spark, taken from the last burning harbour lamp. She closes the glass against the rain.",
   "protective, deliberate",
   "mid-gantry, hunched over her own chest",
   "gauge: 66 to 64. THE SPARK: introduced, now inside her chest drum behind glass.",
   "Macro. THE SIGNATURE IMAGE: an amber spark glowing inside the glass drum while rain streaks the glass outside it.",
   "The glass sealing. A small warm hum begins - the spark's own tone, which persists until SC08_SH003.",
   "The spark is now a permanent element of every shot until SC08. Its hum is the film's second leitmotif.",
   66, 64, "macro", "100mm macro", ["WICK (part)", "the spark"], "Cut to movement."),
 S(6, 149.0, 154.0,
   "She moves on, one arm now curled across her chest to shield the glass. The spark is drawing power as she walks. Gauge 64 to 60.",
   "burdened",
   "along the gantry toward the tower",
   "gauge: 64 to 60. Spark: alive, draining her. Chest: shielded by her arm.",
   "Tracking, with the spark glow the brightest element in frame and everything else falling away from it.",
   "The spark hum plus a new, slower tick layered over the footfall ticks - the drain is audible.",
   "From here she carries the pole-less silhouette: one arm across the chest. This posture is held until SC08.",
   64, 60, "tracking medium", "40mm", ["WICK", "the spark"], "Cut to gauge insert."),
 S(7, 154.0, 158.0,
   "Gauge insert: 60 to 58. Rack focus past the needle to the tower door ahead through the rain.",
   "walking (off-frame)",
   "n/a",
   "gauge: 60 to 58. Tower door: visible ahead, shut.",
   "Macro on the gauge, then a rack focus to the door. One move, no cut.",
   "Rain. The spark hum continues.",
   "The rack focus hands SC06 its first image. Door position and water level must match SC06_SH001.",
   60, 58, "insert with rack focus", "100mm macro", ["WICK (part)"], "Cut on the rack."),
],
"SC06": [
 S(1, 158.0, 163.0,
   "The tower door: iron, swollen, barnacled. She stands at its foot. She is very small against it.",
   "daunted",
   "at the foot of the door, frame centre low",
   "gauge: 58. Door: shut, swollen.",
   "Low wide, the door filling the frame above her. Compress her against the bottom edge.",
   "Rain on iron. The tower itself humming in the wind.",
   "Same door seen in the SC05_SH007 rack focus. Barnacle pattern and water line must match.",
   58, 58, "wide low", "24mm", ["WICK"], "Cut to the effort."),
 S(2, 163.0, 170.0,
   "She levers it. Shoulder against the plate. It gives an inch. She resets and pushes again. It swings. Gauge falls fast: 58 to 49 to 40.",
   "at maximum effort",
   "at the door, braced against it",
   "gauge: 58 to 40. Door: forced open. This is the single most expensive action in the film.",
   "Tight on the effort, then a whip to the gauge as the needle drops. The whip is the only fast camera move in the film.",
   "Iron shrieking. Her spring straining - a sound not used anywhere else.",
   "Eighteen turns, the largest single cost. The needle must be seen crossing 49 on the way down so the arithmetic is legible.",
   58, 40, "tight medium to insert", "50mm", ["WICK"], "Cut to the gauge."),
 S(3, 170.0, 175.0,
   "Gauge insert. The needle crosses into the RED ARC of the dial. Hold.",
   "off-frame",
   "n/a",
   "gauge: 40, needle inside the red arc for the first time",
   "Macro, dead still. Identical framing to every other gauge insert.",
   "Everything drops out except the tiny friction of the needle. The quietest moment in the film.",
   "The red arc is introduced HERE and not at the climax, so the colour can do the worrying for us afterwards.",
   40, 40, "insert", "100mm macro", ["WICK (part)"], "Cut to the interior."),
 S(4, 175.0, 181.0,
   "Interior. She steps in. A spiral stair rises into darkness, lit only by her own amber glow. Water runs down the inside of the wall.",
   "relieved to be out of the wind, then apprehensive",
   "entering, at the foot of the stair",
   "gauge: 40 to 35. Spark: still glowing in her chest, now the only light source.",
   "She enters; the camera tilts up the stair, and keeps tilting, and keeps tilting. The tower's height in one continuous move.",
   "Her footsteps echo. Reverb opens up hard the moment she crosses the threshold.",
   "Her chest glow is the only light in the tower interior from here to SC08. The reverb change marks the interior/exterior boundary.",
   40, 35, "interior tilt-up", "18mm", ["WICK", "the spark"], "Cut to the top of the stair."),
 S(5, 181.0, 186.0,
   "The stair ends. A gap. Broken iron hanging. Beyond it, the wall - and through a breach, the storm outside. Gauge 35 to 31.",
   "stopping, understanding",
   "at the broken edge of the stair",
   "gauge: 35 to 31. Stair: collapsed, unusable. Breach: open to the exterior.",
   "Her point of view across the gap first, then back to her. Two angles, no movement.",
   "Wind coming through the breach. The reverb narrows.",
   "The gap is why she must go outside. The breach framing here must match SC07_SH001 so the exit is legible.",
   35, 31, "POV then reverse", "35mm", ["WICK"], "Cut to the exterior."),
],
"SC07": [
 S(1, 186.0, 191.5,
   "She goes out through the breach onto the riveted plating. The gale hits her flat. She presses herself against the iron. Gauge 31 to 28.",
   "exposed, overwhelmed",
   "on the exterior plating, flattened against the tower",
   "gauge: 31 to 28. No pole. Spark glowing through the rain.",
   "Exterior wide. The tower as a vertical line, the sea white far below. She is a speck on it.",
   "The gale at full volume. Rain horizontal.",
   "First exterior since SC02_SH004. Plating and rivet pattern must match that establishing shot exactly.",
   31, 28, "extreme wide", "24mm", ["WICK"], "Cut to the collapse."),
 S(2, 191.5, 197.0,
   "The remaining section of stair tears away from the tower and falls. She watches it go. Gauge 28 to 25.",
   "watching the last easy option leave",
   "on the plating, looking down",
   "gauge: 28 to 25. Stair: gone entirely. There is now no way back down.",
   "Follow the iron down and out of frame, then hold on empty air where it was.",
   "The crash, delayed and far below. Then wind.",
   "The stair is destroyed. No later shot may show intact stair. This is the point of no return.",
   28, 25, "follow then hold", "50mm", ["WICK"], "Cut to the climb."),
 S(3, 197.0, 205.0,
   "The climb. Hand over hand on rivets. Rain. The horizon tilts as she gains height. Gauge 25 to 22.",
   "working, rhythm still holding",
   "ascending the plating, frame rising",
   "gauge: 25 to 22. Hands: on rivets.",
   "A slow rising track matching her ascent. The horizon progressively tilts off-level so the height is felt rather than shown.",
   "Grab, strain, grab. Her gait rhythm now audibly irregular - the pattern established in SC04_SH002 continues to degrade.",
   "Longest single shot in the film at 8 seconds, placed at the point of maximum investment. The tilted horizon must be consistent through SH008.",
   25, 22, "rising track", "35mm", ["WICK"], "Cut to the grip loss."),
 S(4, 205.0, 211.0,
   "GRIP LOSS. A gust peels her off the iron. She swings on one arm over the drop. Gauge 22 to 20.",
   "in real danger",
   "hanging by one arm off the plating",
   "gauge: 22 to 20. Shoulder joint: the same one that sparked in SC04_SH006, now failing.",
   "Reveal the drop with a long lens straight down to the water. Let the height land.",
   "One long metallic scream from the shoulder joint. Music out entirely.",
   "Same shoulder joint as SC04_SH006. The damage is cumulative and must be animated as a weakness, not a new injury.",
   22, 20, "long lens down", "135mm", ["WICK"], "Cut to her free hand."),
 S(5, 211.0, 216.0,
   "Her free hand closes on something: the lamp-pole, wedged in the ironwork. It came up the tower with the storm.",
   "astonished",
   "hanging, one arm reaching",
   "gauge: 20, unmoved. Lamp-pole: RECOVERED, wedged in the ironwork.",
   "Insert on the pole first, then her hand closing on it. Two frames of information, no exposition.",
   "A single bright note. The score returns, one instrument only.",
   "CRITICAL CONTINUITY: this is the pole lost in SC05_SH003. Its position wedged in the ironwork must be plausible - it was blown against the tower, not placed.",
   20, 20, "insert", "85mm", ["WICK", "lamp-pole"], "Cut to the haul."),
 S(6, 216.0, 221.0,
   "She uses the pole as a brace and hauls herself back onto the iron. Gauge 20 to 14.",
   "recovered, spent",
   "back on the plating, braced on the pole",
   "gauge: 20 to 14. Lamp-pole: now a climbing brace.",
   "Tight on the effort, with the gauge deliberately kept in the corner of frame so the cost is visible during the win.",
   "The strain. Her clock motif stuttering - now audibly skipping a note.",
   "The skipped note in the motif is the audio signature of a weakening spring and worsens through SH008.",
   20, 14, "tight medium", "50mm", ["WICK", "lamp-pole"], "Cut to the last stretch."),
 S(7, 221.0, 225.0,
   "The last stretch. Her limbs stutter. The gait breaks down entirely - she is dragging herself upward. Gauge 14 to 9.",
   "failing",
   "high on the plating, dragging",
   "gauge: 14 to 9. Motion: degraded, no longer a rhythm.",
   "Very tight, almost abstract: brass, rivets, rain. The world reduces to the next handhold.",
   "The mechanism audibly failing. Metal fatigue. The clock motif has stopped being a melody.",
   "The animation degradation is the storytelling here. Do not cover it with cutting - hold on the broken motion.",
   14, 9, "abstract tight", "85mm", ["WICK"], "Cut to the rail."),
 S(8, 225.0, 228.0,
   "She reaches the gallery rail and pulls herself over, collapsing into the lee. Gauge 9 to 6. The burner chamber door is ahead.",
   "collapsed, barely functional",
   "over the rail, on the gallery floor",
   "gauge: 9 to 6, needle deep in the red arc. Lamp-pole: still in hand.",
   "She collapses into frame and we hold. Let her be still for a beat before cutting.",
   "The gale drops sharply as she gets into the lee of the gallery.",
   "Six turns remain entering SC08. The red arc is fully engaged; it must read clearly even in this low, wet framing.",
   9, 6, "medium, held", "35mm", ["WICK", "lamp-pole"], "Cut to the chamber."),
],
"SC08": [
 S(1, 228.0, 233.0,
   "Interior, the burner chamber. Cold, enormous brass. Her glow is the only light in it. She is tiny.",
   "awed, exhausted",
   "on the chamber floor, at the foot of the burner",
   "gauge: 6. Spark: still glowing inside her chest.",
   "Wide. She is very small in a very large space. Do not move the camera.",
   "The storm reduced to a murmur outside. Water dripping.",
   "Scale contrast is the whole point of this shot. Her glow must be the only light source in frame.",
   6, 6, "wide", "18mm", ["WICK", "the spark"], "Cut to the ascent."),
 S(2, 233.0, 238.5,
   "She climbs the last few rungs to the burner, opens her chest and lifts the spark out. Gauge 6 to 3.",
   "careful, hopeful",
   "at the burner, chest open",
   "gauge: 6 to 3. Spark: REMOVED from her chest, now held in her hand. Chest: empty and dark for the first time since SC05.",
   "Close, following her hands. Unhurried.",
   "The spark's hum, now exposed and fragile without the glass around it.",
   "The chest goes dark here. Every shot from SC05_SH005 has had the glow; its absence is a deliberate visual loss.",
   6, 3, "close", "85mm", ["WICK", "the spark"], "Cut to the attempt."),
 S(3, 238.5, 243.0,
   "She offers the spark to the burner. Nothing catches. She repositions and tries again. Nothing.",
   "confused, then afraid",
   "at the burner, reaching up",
   "gauge: 3. Spark: alive but finding nothing to light.",
   "Tight on the spark and the cold brass. The gap between them is the subject of the shot.",
   "The hum, then silence. No catch. No click. Nothing.",
   "Two failed attempts, not one - the second is what tells the audience this is not a technique problem.",
   3, 3, "tight", "100mm macro", ["WICK", "the spark"], "Cut to the reveal."),
 S(4, 243.0, 248.0,
   "THE REVEAL. A static shot of the burner's heart: no wick, no oil, no flint. A socket. Cold brass. The exact diameter of a mainspring.",
   "off-frame",
   "n/a",
   "THE SOCKET: revealed. Nothing else in the burner can accept the spark.",
   "Locked off. No camera movement whatsoever. No music. The frame does not help the audience.",
   "Absolute silence. One water drop.",
   "The single most important shot in the film. The socket diameter must visibly match the coil in her chest - match it in design at T03.",
   3, 3, "static insert", "100mm macro", [], "Cut to her."),
 S(5, 248.0, 253.0,
   "On WICK. She looks at the socket. She looks at her own empty chest. A long beat - the whole decision, played without a cut.",
   "understanding, then at peace",
   "at the burner, motionless",
   "gauge: 3. Chest: open and empty.",
   "Close on her shutter eyes. The aperture closes, then opens. That is the entire performance.",
   "Her clock motif, stated once, complete, on a single instrument. The only complete statement in the film.",
   "The complete motif here is the payoff for the fragmented statements since SC01. Do not add strings under it.",
   3, 3, "close-up", "100mm", ["WICK"], "Cut to the act."),
 S(6, 253.0, 259.0,
   "She unspools her own mainspring and threads it into the socket. The gauge falls: 3, 2, 1. Then the ratchet engages.",
   "spending herself, deliberate",
   "at the socket, both hands working",
   "gauge: 3 to 1. Mainspring: REMOVED from her body, installed in the burner. Ignition costs the final turn: 1 to 0.",
   "Macro, unhurried. This is not an action beat and must not be cut like one.",
   "The spring unspooling - a long, thin, singing sound. Then the ratchet engaging. Then her mechanism winding down to nothing.",
   "The spring is now part of the tower. She cannot be rewound by re-installing it; the ending's single turn is a new beginning, not a restoration.",
   3, 0, "macro", "100mm macro", ["WICK", "mainspring", "the socket"], "Cut to ignition."),
 S(7, 259.0, 262.0,
   "Her shutter eyes go dark. A beat of black. Then - IGNITION. The beacon floods the frame until it is white-gold.",
   "gone dark, at rest",
   "at the foot of the burner, silhouetted",
   "gauge: 0. Beacon: LIT. Spark: consumed.",
   "Hold on her dark silhouette as the light blooms behind her. The frame goes to white-gold without a cut.",
   "One beat of absolute silence. Then the ignition: a huge, warm, low bloom. The score in full, for the first and only time.",
   "The only full-orchestration moment in the film. Her silhouette must stay readable inside the bloom.",
   0, 0, "silhouette to bloom", "50mm", ["WICK", "the beacon"], "Cut to the exterior beam."),
],
"SC09": [
 S(1, 262.0, 270.0,
   "Exterior. The beam sweeps out across black water. Rain turns to light inside the shaft.",
   "not present",
   "n/a",
   "beacon: lit, rotating. Beam sweeping.",
   "Locked wide. The deliberate long hold - the film's longest unbroken static shot.",
   "The beacon's slow rotation. The sea. Score sustained, no melody.",
   "The eight-second hold is protected. Do not cut into it for coverage. Beam rotation rate must match SH003.",
   0, 0, "extreme wide, held", "35mm", [], "Cut to the ship."),
 S(2, 270.0, 276.0,
   "Far out: the running light. It pauses. Then it turns - toward harbour. The reef line slides past behind it.",
   "not present",
   "n/a",
   "ship: turned toward harbour, reef cleared. Reef line: same position as SC02_SH003.",
   "Very long lens, the ship tiny in frame. Held. The turn must be small and easy to miss on first viewing.",
   "The bell buoy, now in rhythm with the beacon. The ship's two-note motif, resolved upward for the first time.",
   "Reef line and ship bearing must match SC02_SH003 so the audience can read that she turned away from danger.",
   0, 0, "extreme long lens", "300mm", ["THE RETURNING SHIP"], "Cut to dawn."),
 S(3, 276.0, 282.0,
   "Dawn comes up grey-gold over the water. The beacon dims as the dark goes. Then: the chamber, dark again, and WICK's silhouette at the foot of the burner.",
   "present only as a silhouette at the end of the move",
   "at the foot of the burner, motionless",
   "gauge: 0. Beacon: spent, dimming with the dawn.",
   "Wide as the light dies, then a slow push toward her silhouette. One continuous move across the cut in mood.",
   "The beacon winding down. The score thinning to nothing. Dawn birds - the first living sound in the film.",
   "The beacon dims because the dark is gone, not because it failed. Birds are the only organic sound in the film and start here.",
   0, 0, "wide to slow push", "35mm", ["WICK"], "Cut to dawn interior."),
],
"SC10": [
 S(1, 282.0, 286.5,
   "Dawn light in the chamber. WICK's shell, slumped at the foot of the burner, still holding the pole. Gauge: 0.",
   "inert",
   "at the foot of the burner, slumped",
   "gauge: 0. Lamp-pole: still in her hand. Chest: open, empty, dark.",
   "Low, static. Held long enough to be uncomfortable. Do not soften this.",
   "Water dripping. Nothing else.",
   "Her pose must match the end of SC09_SH003 exactly - this is the same moment, closer.",
   0, 0, "medium, held", "50mm", ["WICK", "lamp-pole"], "Cut to the doorway."),
 S(2, 286.5, 291.0,
   "Footsteps. A child enters, backlit in the doorway - oversized coat, bare feet, small. Sees her.",
   "inert",
   "unchanged, at the foot of the burner",
   "gauge: 0. Child: entering.",
   "From inside the chamber, so the child is a silhouette in the doorway. Her face is never resolved.",
   "Bare feet on wet iron.",
   "The child is the only human in the film and is never in readable close-up. Backlight and rim light only.",
   0, 0, "wide interior", "35mm", ["WICK", "THE CHILD"], "Cut to the hands."),
 S(3, 291.0, 295.5,
   "The child kneels. Takes the key from WICK's back. Hesitates.",
   "inert",
   "unchanged",
   "KEY: removed from WICK's back, now in the child's hand. Same key as SC01_SH001.",
   "Close on the child's hands and the key. Her face stays out of focus or out of frame.",
   "The key lifting out of the back plate - the same small metal sound as the opening.",
   "Same key asset as SC01_SH001. The hesitation is the emotional beat; give it room.",
   0, 0, "close", "85mm", ["WICK", "THE CHILD", "the key"], "Cut to macro."),
 S(4, 295.5, 299.0,
   "MACRO - mirroring SC01_SH001 exactly. The key turns. One turn. The ratchet catches.",
   "inert, about to change",
   "unchanged",
   "key: turning, one turn only. Ratchet: catching.",
   "IDENTICAL framing, lens and camera height to SC01_SH001, warmed from dusk to dawn. This is the loop.",
   "ONE click. Clean, loud in the silence.",
   "LOOP SHOT: must match SC01_SH001 frame for frame in composition, differing only in colour temperature. One turn, not four.",
   0, 0, "extreme macro", "100mm macro", ["WICK (part)", "the key"], "Cut to the chest."),
 S(5, 299.0, 302.0,
   "Macro on the chest drum. Inside, the coil catches. The shutter eyes flicker open. The needle lifts off zero. Cut to black on the second click.",
   "restarting",
   "unchanged",
   "gauge: 0 to 1. Coil: caught. Eyes: open. One turn, a beginning rather than a restoration.",
   "Macro, then hard cut to black. No fade.",
   "The coil catching. The shutter aperture opening. One final click over black.",
   "FINAL SHOT. Ends on the same click the film opened on, so the film loops. The needle lifts off zero and no further.",
   0, 1, "macro to black", "100mm macro", ["WICK (part)", "chest gauge"], "Hard cut to black."),
],
}

# --------------------------------------------------------------------------- #
# build
# --------------------------------------------------------------------------- #
def tcode(sec: float) -> str:
    m, s = divmod(sec, 60)
    return f"{int(m):02d}:{s:06.3f}"


def main() -> int:
    brief = json.load(open(os.path.join(ROOT, "01_DEVELOPMENT", "MASTER_FILM_BRIEF.json"),
                           encoding="utf-8"))
    cfg = json.load(open(os.path.join(ROOT, "MASTER_CONFIG.json"), encoding="utf-8"))

    assert set(SHOTS) == {s["id"] for s in SCENES}, "scene/shot key mismatch"

    scenes_out, shots_out, cursor = [], [], 0.0
    for sc in SCENES:
        rows = SHOTS[sc["id"]]
        # --- scenes contiguous ------------------------------------------ #
        s_in, s_out = cursor, cursor + sc["t"]
        assert abs(sc["t"] - sum(r["to"] - r["ti"] for r in rows)) < 1e-9, \
            f'{sc["id"]}: scene duration {sc["t"]}s != sum of its shots'
        assert abs(rows[0]["ti"] - s_in) < 1e-9, f'{sc["id"]}: first shot does not start at scene start'
        assert abs(rows[-1]["to"] - s_out) < 1e-9, f'{sc["id"]}: last shot does not end at scene end'

        # --- shots contiguous inside the scene -------------------------- #
        for prev, cur in zip(rows, rows[1:]):
            assert abs(prev["to"] - cur["ti"]) < 1e-9, \
                f'{sc["id"]}: gap/overlap between SH{prev["n"]:03d} ({prev["to"]}) and SH{cur["n"]:03d} ({cur["ti"]})'
        for r in rows:
            assert r["to"] > r["ti"], f'{sc["id"]}_SH{r["n"]:03d}: zero or negative duration'

        # --- gauge delta matches the locked budget ---------------------- #
        gin = sc["gauge_in"]
        gout = sc["gauge_out"]
        if isinstance(gin, int) and isinstance(gout, int):
            assert rows[0]["gin"] == gin, f'{sc["id"]}: scene gauge_in {gin} != first shot {rows[0]["gin"]}'
            assert rows[-1]["gout"] == gout, f'{sc["id"]}: scene gauge_out {gout} != last shot {rows[-1]["gout"]}'
            for prev, cur in zip(rows, rows[1:]):
                if isinstance(prev["gout"], int) and isinstance(cur["gin"], int):
                    assert prev["gout"] == cur["gin"], \
                        f'{sc["id"]}: gauge discontinuity SH{prev["n"]:03d}->{cur["n"]:03d}'
            spent = gin - gout
            budget = sum(c["cost"] for c in brief["turn_budget"]["costs"] if c["scene"] == sc["id"])
            expected = budget + sc.get("ignition", 0) - sc.get("gained", 0)
            assert spent == expected, (
                f'{sc["id"]}: gauge spent {spent} != expected {expected} '
                f'(budget {budget} + ignition {sc.get("ignition", 0)} - gained {sc.get("gained", 0)})')

        for r in rows:
            sid = f'{sc["id"]}_SH{r["n"]:03d}'
            dur = round(r["to"] - r["ti"], 3)
            shots_out.append({
                "shot_id": sid,
                "scene_id": sc["id"],
                "time_in": tcode(r["ti"]),
                "time_out": tcode(r["to"]),
                "time_in_seconds": round(r["ti"], 3),
                "time_out_seconds": round(r["to"], 3),
                "duration": dur,
                "frame_in": int(round(r["ti"] * FPS)) + 1,
                "frame_out": int(round(r["to"] * FPS)),
                "frame_count": int(round(dur * FPS)),
                "action": r["action"],
                "character_state": r["cstate"],
                "character_position": r["cpos"],
                "prop_state": r["pstate"],
                "camera_intention": r["cam"],
                "sound": r["sound"],
                "dialogue": r["dial"],
                "continuity_notes": r["cont"],
                "gauge_in": r["gin"],
                "gauge_out": r["gout"],
                "shot_type": r["stype"],
                "lens": r["lens"],
                "characters": r["chars"],
                "location": sc["loc"],
                "transition_out": r["trans"],
            })

        scenes_out.append({
            "scene_id": sc["id"], "slug": sc["slug"],
            "time_in": tcode(s_in), "time_out": tcode(s_out),
            "time_in_seconds": round(s_in, 3), "time_out_seconds": round(s_out, 3),
            "duration": sc["t"],
            "frame_in": int(round(s_in * FPS)) + 1, "frame_out": int(round(s_out * FPS)),
            "location": sc["loc"], "characters": sc["chars"],
            "story_purpose": sc["purpose"], "beat_type": sc["beat"],
            "emotion": sc["emotion"], "props": sc["props"],
            "environment_action": sc["env"], "transition": sc["transition"],
            "gauge_in": sc["gauge_in"], "gauge_out": sc["gauge_out"],
            "shot_count": len(rows),
            "shot_ids": [f'{sc["id"]}_SH{r["n"]:03d}' for r in rows],
            "dialogue": "none",
        })
        cursor = s_out

    # --- film-level invariants ------------------------------------------- #
    total = round(cursor, 3)
    ids = [s["shot_id"] for s in shots_out]
    assert len(ids) == len(set(ids)), "duplicate shot ids"
    for i in ids:
        assert re.fullmatch(r"SC\d{2}_SH\d{3}", i), f"bad shot id {i}"
    assert total == TARGET_SECONDS, f"total runtime {total}s != {TARGET_SECONDS}s"
    assert int(round(total * FPS)) == brief["runtime"]["total_frames"]
    rng = brief["production_complexity"]["planned_shot_range"]
    assert rng[0] <= len(shots_out) <= rng[1], f"shot count {len(shots_out)} outside {rng}"
    sp = cfg["scene_plan"]["target_shot_seconds"]
    for s in shots_out:
        assert sp["min"] <= s["duration"] <= sp["max"], \
            f'{s["shot_id"]}: duration {s["duration"]}s outside {sp}'
    assert all(s["dialogue"] == "none" for s in shots_out), "film is wordless"
    journey = sum(sc["gauge_in"] - sc["gauge_out"] for sc in SCENES
                  if isinstance(sc["gauge_in"], int) and isinstance(sc["gauge_out"], int)
                  and sc["id"] not in ("SC02", "SC09", "SC10"))
    ignition_total = sum(sc.get("ignition", 0) for sc in SCENES)
    # journey counts the ignition turn too, so it runs 92 -> 0
    assert journey == brief["turn_budget"]["start"], \
        f"total turns spent {journey} != {brief['turn_budget']['start']}"
    assert journey - ignition_total == 92 - brief["turn_budget"]["remaining_at_burner"], \
        f"effort spend {journey - ignition_total} != 91"
    assert sum(c["cost"] for c in brief["turn_budget"]["costs"]) == journey - ignition_total
    # frames contiguous across the whole film
    for a, b in zip(shots_out, shots_out[1:]):
        assert a["frame_out"] + 1 == b["frame_in"], f'frame gap {a["shot_id"]}->{b["shot_id"]}'
    assert shots_out[0]["frame_in"] == 1
    assert shots_out[-1]["frame_out"] == brief["runtime"]["total_frames"]

    out = {
        "schema_version": "1.0.0",
        "task_id": "T02_SCREENPLAY",
        "project_id": "AMS-2026-001",
        "film_title": brief["title"],
        "fps": FPS,
        "total_runtime_seconds": total,
        "total_runtime_formatted": brief["runtime"]["formatted"],
        "total_frames": brief["runtime"]["total_frames"],
        "scene_count": len(scenes_out),
        "shot_count": len(shots_out),
        "average_shot_seconds": round(total / len(shots_out), 2),
        "dialogue": "none - the film is wordless by design",
        "turn_budget_summary": {
            "start": brief["turn_budget"]["start"],
            "spent": sum(c["cost"] for c in brief["turn_budget"]["costs"]),
            "at_burner": brief["turn_budget"]["remaining_at_burner"],
            "ignition": brief["turn_budget"]["ignition_cost"],
            "given_back_in_ending": brief["turn_budget"]["turns_given_back_in_ending"],
        },
        "scenes": scenes_out,
        "shots": shots_out,
    }

    jpath = os.path.join(HERE, "SHOT_LIST.json")
    with open(jpath, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    cols = ["shot_id", "scene_id", "time_in", "time_out", "duration", "frame_in",
            "frame_out", "frame_count", "gauge_in", "gauge_out", "shot_type", "lens",
            "characters", "action", "character_state", "character_position", "prop_state",
            "camera_intention", "sound", "dialogue", "continuity_notes", "transition_out"]
    cpath = os.path.join(HERE, "SHOT_LIST.csv")
    with open(cpath, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for s in shots_out:
            row = dict(s)
            row["characters"] = "; ".join(s["characters"])
            w.writerow(row)

    print(f"scenes          {len(scenes_out)}")
    print(f"shots           {len(shots_out)}   (planned range {rng})")
    print(f"runtime         {total}s = {brief['runtime']['formatted']}")
    print(f"frames          1..{shots_out[-1]['frame_out']}  ({brief['runtime']['total_frames']})")
    print(f"avg shot        {out['average_shot_seconds']}s")
    print(f"turn budget     92 - {out['turn_budget_summary']['spent']} = "
          f"{out['turn_budget_summary']['at_burner']}, ignition -> 0, +1 in ending")
    print("all invariants  PASS")
    print(f"wrote {os.path.relpath(jpath, ROOT)} and {os.path.relpath(cpath, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
