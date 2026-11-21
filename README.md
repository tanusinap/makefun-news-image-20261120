# 20 November 2026 in one image

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

## Badges

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![make.fun](https://img.shields.io/badge/make.fun-news--image--20261120-blue)](https://make.fun/bounty/news-image-20261120)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
