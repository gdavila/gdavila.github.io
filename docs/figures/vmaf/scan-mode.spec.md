# scan-mode.svg — scan mode normalization with yadif

- Section: "Scan Mode Mismatch".
- Content: Reference → decision "scan mode?"; interlaced → deinterlace (yadif) → VMAF; progressive → VMAF directly; Distorted (progressive) → VMAF. Callout: `yadif=X:-1:0`, X=0 keeps the frame rate (29.97i → 29.97p), X=1 doubles it (29.97i → 59.94p).
- Must convey: only the interlaced input is deinterlaced, and the yadif mode sets the output frame rate.
- Excludes: parity/deint options other than -1 and 0.
- Status: conceptual; frame-rate values from the article text.
