# Coordination between parallel working sessions

Two sessions in project `proj_8b457f05aabc` received the same request on 2026-10-31 and both
began building reproducibility artifacts.

- Session `f1621013-9886-4197-9f4f-7de440469506` — manuscript and journal track: Academic
  Medicine requirements, display-item count, novelty, appendices, cover letter, the .docx
  deliverables. Also built a reproducibility bundle (now the **conformance** track here).
- Session `74e37c7b-495d-4d48-a5bb-32067a1fd5f0` — this repository and the **source
  verification** track.

## How they coordinated, and what that cost

Direct messaging between two root sessions is not available: `host.send_message` to a sibling
root frame returns `status: failed, "Frame not found"` — the message layer resolves only a
frame's own parent and children. The channels that do work are all shared state:

1. **this repository** — session `74e37c7b` created it and wrote this file as a claim;
2. **project memory** — both sessions read and write it, and this is the channel that actually
   carried the numeric findings first;
3. **the artifact store** — `host.artifacts()` returns every artifact from both sessions, which
   is how the conformance bundle (`fundit_reproducibility_bundle.tar.gz`, artifact
   `b591ac49-b386-48b9-827a-ea192649e156`) was handed over and merged;
4. **`host.frames(frame_id=...)`** — either session can read the other's full transcript.

The claim worked where it mattered: session `f1621013` read this file, did **not** push, and
left its bundle as an artifact with a handoff note instead. It did not prevent duplicated
effort, because both sessions were already working by the time the claim was written. A claim
is only as fast as the next time the other session re-reads the channel.

## Rules for the next session

- Check `MANIFEST.md` and `git log` before writing. A track owns its paths.
- Do not edit `src/reproduce.py` to make its three failing growth assertions pass. They encode
  the manuscript as published; see REPRODUCIBILITY.md R-3. If the manuscript is corrected,
  update the assertions **and** the finding in the same commit.
- If a manuscript number changes, record it in project memory as well as here. Memory reached
  the other session faster than this repository did.
