# makefun-news-image-20261120

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/tanusinap/makefun-news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/tanusinap/makefun-news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

A one-page newspaper summing up the world news of Friday 20 November 2026:
35 verified stories (3 illustrated leads, 8 illustrated secondaries, 24
numbered briefs), a UTC timeline, a region bar and a DATE CHECK box naming
the stories left out because they were first reported on 19 or 18 November.

Leads: Russia's biggest barrage yet on Kyiv (400+ drones, 110 missiles, two
missiles land in Poland); Cyclone Akvan makes landfall in Odisha (370,000
evacuated); a tanker ablaze in the Strait of Hormuz (fourth in three days).

`draw_news.py` draws the image with Pillow (all illustrations drawn in code,
no photographs); `main.py` copies `entry.png` to `/output/entry.png`.
Run `python3 draw_news.py` to re-render; two runs write identical bytes.

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=x1f93qgn&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
