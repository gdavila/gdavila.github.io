# easyvmaf-block-diagram.svg — easyVMAF high-level architecture

- Section: "Putting It All Together using easyVMAF".
- Content: options → read user inputs (model, sync window, …); Reference/Distorted → FFprobe reads video properties; both feed the Python step that builds the FFmpeg command → run FFmpeg; the FFmpeg filter chain: resolution → scan mode → FPS → frame-to-frame sync → VMAF → Score. Reference/Distorted also feed the filter chain.
- Must convey: easyVMAF only gathers information and builds one FFmpeg command; all video processing happens in the FFmpeg filter chain.
- Excludes: implementation details of the Python modules; the sync search loop is not drawn separately.
- Status: conceptual, matches the repository at the time of the article.
