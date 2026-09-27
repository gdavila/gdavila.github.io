# overview.svg — normalization pipeline before VMAF

- Section: introduction, after "Finally, we introduce easyVMAF".
- Content: Reference and Distorted inputs → "Scale resolution to VMAF model" → "Frame-to-frame sync" → VMAF → Score; all inside an FFmpeg + libvmaf frame. Callouts: scaling depends on model (HD, 4K, Phone); sync covers scan mode, frame rate, first frame.
- Must convey: VMAF needs two normalization stages (spatial, then temporal) before the metric is computed, all within FFmpeg.
- Excludes: any claim about processing cost or ordering being mandatory in libvmaf itself; it is the order we recommend.
- Status: conceptual.
