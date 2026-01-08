def extract_text(run_result):
    if hasattr(run_result, "final_output"):
        return run_result.final_output

    if hasattr(run_result, "output_text"):
        return run_result.output_text

    if hasattr(run_result, "outputs"):
        # fallback (rare)
        return run_result.outputs[-1].content

    raise RuntimeError("Cannot extract text from RunResult")
