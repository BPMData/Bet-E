# Contributing to Bet-E

Contributions are very welcome! Ideas that fit great here:
- **New period styles** in `styles/<style-name>/` (layout specs, prompt style blocks, and public-domain/original sample references)
- **New color palettes** or layout variations in existing `template.html` files
- **New example recipes** in `examples/`
- **Improvements to `scripts/`** (`build.py`, `make_contact_sheet.py`, `print_prompts.py`, `gen_images.py`)

## Before Opening a Pull Request
1. **Always use a Pull Request — never force-push to `main`.** Create a feature branch, run the tests, and open a PR for review.
2. **Run the CLI tests & verify the full build:**
   - Run `python3 -m unittest discover -s tests -v`.
   - Run `python3 scripts/make_contact_sheet.py ...` on any generated imagery and inspect every image visually.
   - Run `python3 scripts/build.py ... --preview-dir ...` and verify the resulting PDF is cleanly paginated (typically 2 US Letter pages per size) with no overlapping footers or clipped text.
3. **No copyrighted third-party assets:** Only include artwork, fonts (via open licenses), and text you created or have the right to distribute.
4. **Keep personal paths & keys out:** Never commit API keys, personal output directories, or `cost_log.txt`.

## License & CLA
- All code, templates, and documentation in this repo are licensed under the **GNU AGPL-3.0** (see `LICENSE`).
- By submitting a contribution, you agree to the **Contributor License Agreement** in [`CLA.md`](CLA.md), which grants the maintainer the right to sublicense and relicense contributions. Please include `I agree to the Bet-E Contributor License Agreement (CLA.md).` in your PR description.
