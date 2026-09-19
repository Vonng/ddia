# Repository cards

Adapted from [SILO's repository cards](https://github.com/pgsty/silo/tree/main/buildscripts/repository-cards), using DDIA's existing boar logo and contributor roster.

The workflow publishes light and dark contributor and Star History SVGs to `codex/repository-cards` every day at 00:00 UTC (08:00 Asia/Shanghai), and after changes to the generator or reviewed roster. GitHub may queue scheduled runs. Generated assets stay out of the source branch.

## Contributor credit

`data/contributors.yaml` is the reviewed roster shared with the website. Every human issue or PR author counts, including open and unmerged work. Existing credit is retained, bots are excluded, and merged work is ordered before proposals and reports. Gold rings preserve the major contributions already acknowledged in the book.

The deleted-account placeholder `ghost` is not counted as an identifiable contributor; its issue remains in the activity table. The roster's `excluded_issues` excludes unrelated content: #396 is an off-topic “AI pipeline” message, not feedback on the book.

The daily workflow discovers new authors for the images. To synchronize the website roster, README names, and both editions' contribution tables as well, use an authenticated GitHub token:

```sh
uv run --with PyYAML==6.0.3 -- python bin/repository-cards/update.py \
  --output /path/to/repository-cards --sync-roster
make translate
make check
```

Set `GH_TOKEN` in the environment. Keep the output checkout's existing `history.json` and `contributors.json` when updating; they preserve history and provide cached avatars. Review and commit the source changes after synchronization.

## Star history

The first run reconstructs a weekly curve from GitHub's [star-history API](https://docs.github.com/en/rest/activity/starring#get-repository-star-history). This reconstruction is not a log of observed historical totals. Later runs append the repository's observed daily total, allow decreases, and replace an observation when rerun on the same UTC day. Missed daily observations are not fabricated.

The SVGs embed their avatars and logo, so GitHub image rendering does not depend on external requests from inside the SVG. An unavailable avatar reuses its previous image or falls back to the contributor's initial.

## Validation

```sh
uv run --with PyYAML==6.0.3 -- python -m unittest discover \
  -s bin/repository-cards -p 'test_*.py' -v
```

The scripts retain the original SILO generator's [AGPL-3.0-or-later license](LICENSE) and copyright notices. The generated-assets branch contains only images, their data, and a short provenance document; do not merge it into `main`.
