# Figure specs: "Simplifying the way to use VMAF"

Destination: `_video/Vmaf/2020-03-05-Vmaf.md` (public URL `/video/Vmaf/`).
SVG sources live beside the post in `_video/Vmaf/` and are served as `/video/Vmaf/<name>.svg`.
They redraw the six PNG figures of the OTTVerse article "EasyVMAF: Running VMAF in the Wild" (Nov. 2020), by the same author.

Shared visual rules:
- Self-contained light card (white background, rounded) so each figure reads the same on a light or dark page; no page CSS is inherited through `<img>`.
- Neutral grey = inputs/outputs; blue = FFmpeg filter step; indigo = VMAF; green/red = reference/distorted (always also labelled in text).
- Dashed amber frame = "runs inside FFmpeg + libvmaf"; dashed grey frame = a single FFmpeg filter.
- Arrows carry video streams; dotted lines are callouts/zoom, never data flow.
