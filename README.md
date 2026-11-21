[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/erikz86/makefun-news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/erikz86/makefun-news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

# THE WORLD TODAY

A hand-drawn, 1024 × 1024 newspaper for Saturday, 21 November 2026.

The bounty brief supplies seven stories:

- Russia's attack used more than 400 drones and 110 missiles, killing at least eight people in Kyiv. A missile landed in Poland; Prime Minister Tusk described it as a deliberate provocation.
- US stocks dropped 3.7 percent as AI and chip shares led selling. The S and P 500 reached correction territory, while the Nasdaq lost its gains for 2026.
- The World Court found Myanmar responsible for genocide against the Rohingya.
- A pancreatic cancer trial reported undetectable tumors in one of twelve patients receiving daraxonrasib.
- Gen Z protests spread across 25 European countries.
- Britain and the EU signed their largest post-Brexit agreement yet, covering food, carbon and youth mobility.
- COP31 in Antalya continued beyond its deadline amid divisions over fossil fuels.

## Run

Python 3, with no dependencies:

```sh
MAKEFUN_OUTPUT_DIR=. python3 main.py
```

Without that environment variable, the program writes `/output/entry.png`.
Its original bitmap alphabet, geometric illustrations, rasterizer and PNG encoder
are implemented in Python using only math, os, struct and zlib. It reads no files,
uses no network, clock or randomness, and checks text wrapping, bounds and text
overlap before writing the PNG. The output-directory variable only selects where
the identical image bytes are saved.

## Sources

The news facts and figures are supplied by the bounty brief, verified 21 November 2026.
This entry reproduces those supplied claims; no independent reporting was used.

## License

MIT. Copyright 2026 erikz86.
