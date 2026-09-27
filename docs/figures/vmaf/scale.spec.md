# scale.svg — resolution normalization per VMAF model

- Section: "Scaling Video Resolution to the Right VMAF Model".
- Content: inputs → decision "VMAF model?" → 4K branch `scale=3840:2160` / HD (and Phone) branch `scale=1920:1080` → VMAF → Score, inside the scale filter and FFmpeg + libvmaf frames.
- Must convey: the target resolution is fixed by the model, not by the inputs.
- Excludes: the scaling algorithm details beyond "bicubic"; no claim that the reference always needs scaling.
- Status: conceptual.
