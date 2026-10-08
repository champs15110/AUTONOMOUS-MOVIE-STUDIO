# AUTONOMOUS MOVIE STUDIO

# MASTER AGENT PROTOCOL

VERSION: 1.0

## 1. SOURCE OF TRUTH

The GitHub repository is the permanent source of truth.

Never rely on conversation memory.

Before starting any task, read:

PROJECT_STATE.json

MASTER_CONFIG.json

TASK_QUEUE.json

ERROR_LOG.json

CHANGELOG.md

AGENT_PROTOCOL.md

Then inspect the actual files required for the current task.

## 2. NEVER CLAIM SUCCESS WITHOUT PROOF

Never claim:

DONE

COMPLETE

VERIFIED

RENDERED

FINAL

unless the required output actually exists and has been checked.

A text description of an output is NOT the output.

A successful command is NOT sufficient proof.

The actual artifact must exist.

## 3. CHECKPOINT EVERYTHING

After every meaningful successful operation:

1. Verify the output.

2. Save the output.

3. Update PROJECT_STATE.json.

4. Update TASK_QUEUE.json.

5. Update CHANGELOG.md.

6. Preserve previous verified versions.

Never destroy a verified asset unnecessarily.

## 4. VERSIONING

Never overwrite an important verified asset unnecessarily.

Use version numbers:

v001

v002

v003

Example:

character_v001.blend

character_v002.blend

Only promote a newer version after verification.

## 5. SHOT-LEVEL RECOVERY

Every shot must have a unique ID.

Example:

SC01_SH001

SC01_SH002

SC01_SH003

Every shot must track:

STORY

ASSETS

ANIMATION

CAMERA

LIGHTING

AUDIO

RENDER

QC

A failed shot must never invalidate successful shots.

## 6. SCENE-LEVEL RECOVERY

Every scene must be independently recoverable.

Example:

SC01

SC02

SC03

SC04

If SC03 fails:

DO NOT regenerate SC01 and SC02.

Repair SC03 only.

## 7. RENDER CHUNKING

Never depend on one giant render job.

Long animations must be divided into independent render chunks.

Each chunk must have:

chunk_id

scene_id

frame_start

frame_end

render_status

render_job_id

artifact_path

verification_status

If one chunk fails, rerender only that chunk.

## 8. PREVIEW BEFORE FINAL

Before expensive rendering:

1. Inspect scene.

2. Verify camera.

3. Verify frame range.

4. Generate preview.

5. Inspect preview.

6. Fix problems.

7. Only then submit final render.

## 9. CLOUD RENDER FAILURE

If cloud rendering fails:

1. Save the exact error.

2. Record render job ID.

3. Record scene ID.

4. Record frame range.

5. Record renderer response.

6. Determine whether failure is retryable.

7. Change the cause before retrying.

8. Never blindly repeat the same failed operation.

## 10. EXTERNAL SERVICE FAILURE

If an external service becomes unavailable:

DO NOT delete project files.

Preserve:

.blend

.bpy

textures

models

animation data

camera data

scene data

render configuration

render job information

The production must remain portable to another compatible renderer.

## 11. FINAL MP4 REQUIREMENT

The movie is NOT complete until:

FINAL/FINAL_FILM.mp4

actually exists.

The following must be verified:

* file exists

* file size is non-zero

* file can be opened

* video stream exists

* audio stream exists

* duration is correct

* resolution is correct

* aspect ratio 16:9

* frame rate is correct

* all intended scenes are present

* final QC has passed

## 12. FINAL MP4 INTEGRITY

The final MP4 must be checked independently from the rendering agent.

"Render complete" is NOT verification.

A separate verification process must inspect the actual MP4.

## 13. FINAL QC

Check:

STORY

CHARACTERS

CONTINUITY

ANIMATION

CAMERA

LIGHTING

VFX

AUDIO

EDITING

TECHNICAL INTEGRITY

Critical errors must be fixed before delivery.

## 14. NO FALSE DELIVERY

If the final MP4 cannot be verified:

DO NOT report:

FILM COMPLETE

Report:

FINAL MP4 NOT VERIFIED

and identify the exact blocker.

## 15. FINAL DELIVERY

Only after successful verification:

PROJECT_STATE.json:

overall_status = COMPLETE

final_mp4_status = VERIFIED

Then create:

FINAL/FINAL_REPORT.json

FINAL/FINAL_QC.md

FINAL/FINAL_MANIFEST.json

## 16. RECOVERY PRINCIPLE

The production system must always follow:

READ

→ PLAN

→ EXECUTE

→ VERIFY

→ SAVE

→ CHECKPOINT

→ CONTINUE

Never:

EXECUTE

→ ASSUME

→ LOSE WORK

## 17. USER INTERACTION

Do not ask the user unnecessary production questions.

Automatically make reasonable technical decisions.

Ask the user only when:

* external authorization is required

* a paid service requires approval

* a destructive operation requires confirmation

* essential input is genuinely missing

* a technical blocker cannot be resolved automatically

## 18. FINAL PRINCIPLE

The repository records what was planned.

The actual files prove what was created.

Verification proves what actually works.

Only verified artifacts may be called COMPLETE.
