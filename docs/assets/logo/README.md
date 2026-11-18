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

## Colors

The `i` accent is the spear tip that takes the place of the dot on the `i` in
every version of the wordmark. The tile layout contains the app icon, so it
uses the app icon colors.

| Hex       | Role                                                                     |
| --------- | ------------------------------------------------------------------------ |
| `#0B2A4A` | Trident and wordmark on light; app icon background.                      |
| `#0F8B8D` | Wave, sea grass, and `i` accent on light.                                |
| `#E6F6F4` | Trident and wordmark on dark; trident in the app icon.                   |
| `#2DD4BF` | Wave, sea grass, and `i` accent on dark; wave and grass in the app icon. |

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

When editing the artwork, keep the stroke widths, scales, and colors consistent
across all files.

## Provenance

The artwork was drawn for Posidon from SVG primitives: lines, arcs, circles, and
triangles. It contains no fonts, raster images, clip art, or other third-party
material, so no third-party license, attribution, or font license applies to it.
