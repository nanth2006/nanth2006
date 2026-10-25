# Setup

1. Create or update the repository named `nanth2006` (the profile README repository).
2. Copy all files and the `.github/workflows/github-snake.yml` workflow into its root.
3. Commit and push to `main`. Enable GitHub Actions if prompted, then run **Generate contribution snake** once from the Actions tab.
4. The action publishes `snake.svg` and `snake-dark.svg` to the `output` branch.
5. Update project links in README.md if repository names or deployment URLs have changed.

Notes:
- `banner.svg` embeds the supplied character as a transparent PNG data URI for Safari compatibility.
- SVG animations use SMIL/CSS only; GitHub's SVG sanitizer/browser rendering may suppress some animation features, and animation support varies by client.
- `banner-light.svg` is the white-page variant.
- SVG text is rendered as text rather than true font outlines, so a viewer's font fallback can differ slightly.
- The stats cards are self-contained local SVGs and intentionally use illustrative progress values rather than live GitHub API data.
