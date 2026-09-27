# frame-sync.svg — PSNR sliding-window first-frame alignment

- Section: "First Frame Mismatch", after "The iterations previously described are shown in the following figure."
- Content: reference strip with its first m frames selected (reference_subsample: 1 … m); distorted strip with a sync window of n frames; four iterations (1, 2, 3, n) where distorted_subsample_i holds frames i … i+m-1.
- Must convey: the reference subsample is fixed; the distorted subsample slides one frame per iteration inside the sync window; PSNR is computed per iteration.
- Excludes: actual PSNR values (they are in the table in the text); m and n values are symbolic.
- Correction vs. original PNG: last-frame labels are i+m-1 (m+2 for i=3, n+m-1 for i=n); the PNG showed m+3 and n+m.
- Status: conceptual.
