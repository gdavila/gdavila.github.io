# framerate.svg — frame rate adaptation with fps

- Section: "Frame Rate Mismatch".
- Content: Reference → VMAF unmodified; Distorted → decision "fps_dist = fps_ref?"; No → `fps=fps_ref` → VMAF; Yes → VMAF.
- Must convey: we adapt only the distorted stream and leave the reference untouched.
- Excludes: any suggestion that VMAF is valid for frame-rate conversion (the text warns it is not trained for it).
- Status: conceptual.
