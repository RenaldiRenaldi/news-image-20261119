[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/RenaldiRenaldi/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/RenaldiRenaldi/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

# The World Today — 19 November 2026

A compact newspaper front page for Thursday, 19 November 2026: **42 dispatches**, six regional sections, an original schematic world map, a Shenzhen summit lead, Market Pulse, Timeline of the Day, and Day in Numbers.

The grid contains Asia 8, Europe 7, Middle East 7, Americas 7, Africa 7, and Oceania 6. Large condensed headlines, ink-blue rules, muted green geography and restrained rust accents organize the page. The lead and strips repeat selected dispatches rather than adding to the count.

## Render

Requires Python 3, Pillow, and the system Noto Sans Condensed Bold / DejaVu font files named in `main.py`.

```sh
python3 -m pip install -r requirements.txt
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The program writes exactly one image, `entry.png`, to the selected output directory, defaulting to `out`. The output is a 1024 × 1024 RGB PNG. Rendering is offline, with fixed editorial content and geometry, no current-time reads, no randomness, and no image metadata timestamps.

## Reporting policy

Research was conducted during this recorded build using public pages fetched with curl and live web search. The edition combines developments reported by local outlets on 19 November with an explicitly labelled agenda of events scheduled for that date. Local publication dates are retained; a 19 November Asian or Pacific publication can have an 18 November UTC timestamp. Some international reports describe overnight developments from 18 November in the event's own time zone; the source ledger discloses these rather than silently redating them.

“Due”, “forecast”, “reports” and attribution are intentional. Scheduled meetings, judgments and rate decisions are not presented as completed outcomes. Allegations and reported IPO pricing remain attributed. The timeline mixes report-publication times with a clearly marked scheduled court time; all clock times there are UTC. The market strip identifies figures as the latest session quoted in a 19 November report, not live prices.

See [SOURCES.md](SOURCES.md) for the 42-item source and date ledger. `research.py` is a build-session research aid; it is not used or imported by the renderer and is not needed to run the entry.

No competition submission is performed by this repository.
