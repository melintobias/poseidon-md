# Logo

The Posidon logo pairs a trident with a sine wave. The wave stands for both the
sea and an audio signal, which ties the name to what the tool does. The SVG
files in this directory are the source of truth for the logo.

## Files

Each layout has one file for light backgrounds and a `-dark` file for dark
backgrounds. The app icon has its own background, so one file serves both.

### Primary logo

| Layout              | Light backgrounds                      | Dark backgrounds                                 |
| ------------------- | -------------------------------------- | ------------------------------------------------ |
| Symbol and wordmark | [`posidon-logo.svg`](posidon-logo.svg) | [`posidon-logo-dark.svg`](posidon-logo-dark.svg) |
| Symbol only         | [`posidon-mark.svg`](posidon-mark.svg) | [`posidon-mark-dark.svg`](posidon-mark-dark.svg) |
| App icon            | [`posidon-icon.svg`](posidon-icon.svg) | Same file                                        |

### Alternatives

The seagrass symbol adds two blades of sea grass that rise from the wave on
either side of the shaft. It uses the same grid and position as the primary
symbol. The blades blur at small sizes, so keep the primary symbol for favicons
and other small spaces.

Use the stacked layout where the space is close to square, such as a social
card. Use the tile layout where the logo should echo the app icon. Use the
wordmark on its own in short, wide spaces, such as a page header.

| Layout                            | Light backgrounds                                                        | Dark backgrounds                                                                   |
| --------------------------------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| Seagrass symbol and wordmark      | [`posidon-logo-seagrass.svg`](posidon-logo-seagrass.svg)                 | [`posidon-logo-seagrass-dark.svg`](posidon-logo-seagrass-dark.svg)                 |
| Seagrass symbol above wordmark    | [`posidon-logo-stacked-seagrass.svg`](posidon-logo-stacked-seagrass.svg) | [`posidon-logo-stacked-seagrass-dark.svg`](posidon-logo-stacked-seagrass-dark.svg) |
| Seagrass app icon beside wordmark | [`posidon-logo-tile-seagrass.svg`](posidon-logo-tile-seagrass.svg)       | [`posidon-logo-tile-seagrass-dark.svg`](posidon-logo-tile-seagrass-dark.svg)       |
| Seagrass symbol only              | [`posidon-mark-seagrass.svg`](posidon-mark-seagrass.svg)                 | [`posidon-mark-seagrass-dark.svg`](posidon-mark-seagrass-dark.svg)                 |
| Wordmark only                     | [`posidon-wordmark.svg`](posidon-wordmark.svg)                           | [`posidon-wordmark-dark.svg`](posidon-wordmark-dark.svg)                           |

### Detailed logo

The detailed logo adds nautical touches to the primary logo for spaces where it
is shown large, such as a banner or the head of a landing page:

- A faint compass rose sits behind the trident, centered where the shaft meets
  the curve of the tines.
- The wave is mirror-symmetric: it dips under the shaft and crests on either
  side.
- The wordmark keeps the plain letters, except for the `i`. A water droplet
  takes the place of its dot, and its stem runs on below the baseline into an
  anchor.

The compass rose fades and the anchor flukes blur at small sizes, so use the
primary logo anywhere the detailed logo would fall below its minimum height.

| Layout                       | Light backgrounds                                        | Dark backgrounds                                                   |
| ---------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------ |
| Detailed symbol and wordmark | [`posidon-logo-detailed.svg`](posidon-logo-detailed.svg) | [`posidon-logo-detailed-dark.svg`](posidon-logo-detailed-dark.svg) |

## Colors

The `i` accent takes the place of the dot on the `i`. It is a spear tip in
every version of the wordmark except the detailed logo, which uses a water
droplet. The tile layout contains the app icon, so it uses the app icon colors.

| Hex       | Role                                                                     |
| --------- | ------------------------------------------------------------------------ |
| `#0B2A4A` | Trident and wordmark on light; app icon background.                      |
| `#38BDF8` | Wave, sea grass, and `i` accent on light.                                |
| `#E6F6F4` | Trident and wordmark on dark; trident in the app icon.                   |
| `#BAE6FD` | Wave, sea grass, and `i` accent on dark; wave and grass in the app icon. |

The detailed logo uses the colors above for the trident and the wordmark. The
wave keeps the same blue on dark backgrounds as on light ones, to match the
water droplet:

| Light     | Dark      | Role                                     |
| --------- | --------- | ---------------------------------------- |
| `#38BDF8` | `#38BDF8` | Wave and the water droplet over the `i`. |
| `#E0F2FE` | `#0B2A4A` | Compass rose.                            |

## Usage

- Use the light variants on light backgrounds and the dark variants on dark
  backgrounds. The app icon works on either.
- Keep clear space around the logo at least as large as the height of the
  lowercase letters.
- Keep each file at or above its minimum height:
  - Primary symbol and wordmark only: 16 px.
  - Primary logo: 24 px.
  - Seagrass symbol and seagrass logo: 32 px.
  - Tile layout: 48 px.
  - Stacked layout: 64 px.
  - Detailed logo: 64 px.
- Do not stretch, rotate, recolor, outline, or add effects to the artwork.

In Markdown rendered by GitHub, a `<picture>` element switches between the
variants to match the reader's color scheme. The paths below are relative to
the repository root:

```html
<picture>
	<source
		media="(prefers-color-scheme: dark)"
		srcset="docs/assets/logo/posidon-logo-dark.svg"
	/>
	<img alt="Posidon" src="docs/assets/logo/posidon-logo.svg" width="320" />
</picture>
```

## Construction

The symbol is drawn on a 128-unit grid with 10-unit strokes and round caps.
The sea grass blades use thinner 8-unit strokes so that they stay secondary to
the trident. The wordmark uses the same 10-unit stroke and is built from
circles, elliptical arcs, and straight lines. In place of a dot, the `i` carries
a spear tip that echoes the trident's tines: an upward-pointing equilateral
triangle with 16-unit sides. That size gives it about the same area as a round
dot, and its base sits where the bottom of a dot would.
Neither part uses a typeface, so the files render the same everywhere without
embedded or installed fonts.

The layouts reuse that geometry at fixed scales:

- The side-by-side layouts scale the wordmark to 84% beside the symbol.
- The stacked layout scales the symbol to 125% above the wordmark at 84%.
- The tile layout scales the app icon to 87.5% beside the wordmark at 84%.
- The wordmark-only layout keeps the wordmark at full size.

The detailed logo keeps the primary geometry, scales, positions, and view box,
except for the following:

- The compass rose is centered at (64, 70), where the shaft meets the curve of
  the tines. It has four long points that reach 35.2 units from the center,
  four short points that reach 20.8 units, and a ring with a 25.6-unit radius
  and a 2.4-unit stroke. At that size it stays at least 3 units clear of the
  wave. It is drawn behind the trident.
- The wave has the same width, amplitude, and stroke as the primary wave, but
  its phase is shifted so that it is symmetric about the shaft: it dips under
  the shaft and crests 22 units to either side. The shaft runs 5 units further
  down than in the primary symbol, so the gap above the dip matches the gap in
  the primary symbol.
- The `i` keeps its full stem, which runs on below the baseline to the same
  depth as the descender on the `p`. There it meets the anchor arms: a filled
  crescent 48 units wide that is 10 units thick at the bottom, like the letter
  strokes, and 7 units thick at the ends. The arms rise 19 units from the bottom
  to their ends, where a 16-unit arrow fluke caps each one. The whole anchor
  sits below the bottoms of the other letters, so the letter spacing is
  unchanged.
- The water droplet over the `i` has a round base 15 units across that rises to
  a point level with the top of the `d`. The base sits about where the bottom
  of the spear tip sits in the other versions of the wordmark.

When editing the artwork, keep the stroke widths, scales, and colors consistent
across all files.

## Provenance

The artwork was drawn for Posidon from SVG primitives: lines, arcs, curves,
circles, and triangles. It contains no fonts, raster images, clip art, or other
third-party material, so no third-party license, attribution, or font license
applies to it.
