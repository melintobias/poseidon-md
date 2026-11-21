# Logo

The Posidon logo pairs a trident with a sine wave. The wave stands for both the
sea and an audio signal, which ties the name to what the tool does. A faint
compass rose sits behind the trident, and the `i` in the wordmark has no dot
and ends in an anchor. The SVG files in this directory are the source of truth
for the logo.

## Files

The logo has one file for light backgrounds and one for dark backgrounds.

| Light backgrounds                      | Dark backgrounds                                 |
| -------------------------------------- | ------------------------------------------------ |
| [`posidon-logo.svg`](posidon-logo.svg) | [`posidon-logo-dark.svg`](posidon-logo-dark.svg) |

## Colors

| Role                  | Light     | Dark      |
| --------------------- | --------- | --------- |
| Trident and wordmark. | `#0B2A4A` | `#E6F6F4` |
| Wave.                 | `#38BDF8` | `#38BDF8` |
| Compass rose.         | `#E0F2FE` | `#0B2A4A` |

The wave uses the same blue on both backgrounds. The compass rose uses a color
close to each background so that it stays faint.

## Usage

- Use the light file on light backgrounds and the dark file on dark
  backgrounds.
- Keep clear space around the logo at least as large as the height of the
  lowercase letters.
- Keep the logo at least 64 px tall. Below that, the compass rose fades and the
  anchor flukes blur.
- Do not stretch, rotate, recolor, outline, or add effects to the artwork.

In Markdown rendered by GitHub, a `<picture>` element switches between the
files to match the reader's color scheme. The paths below are relative to the
repository root:

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

The symbol is drawn on a 128-unit grid with 10-unit strokes and round caps:

- The trident has three tines that end in spear points. Its shaft runs down
  from the middle tine and ends 8 units above the wave.
- The wave is a sine wave with a 44-unit period and a 5-unit amplitude. It
  spans 88 units and is symmetric about the shaft: it dips under the shaft and
  crests 22 units to either side.
- The compass rose is centered at (64, 70), where the shaft meets the curve of
  the tines, and is drawn behind the trident. It has four long points that
  reach 35.2 units from the center, four short points that reach 20.8 units,
  and a ring with a 25.6-unit radius and a 2.4-unit stroke. At that size it
  stays at least 3 units clear of the wave.

The wordmark sits beside the symbol at 84% scale. It uses the same 10-unit
stroke and is built from circles, elliptical arcs, straight lines, and curves.
The `i` is drawn as an anchor. It has no dot, so the stem starts at the
x-height and runs on below the baseline to the same depth as the descender on
the `p`, where it ends in the anchor arms. The arms are a filled crescent 48
units wide that is 10 units thick at the bottom, like the letter strokes, and 7
units thick at the ends. The arms rise 19 units from the bottom to their ends,
where a 16-unit arrow fluke caps each one. The whole anchor sits below the
bottoms of the other letters, so the letter spacing is unchanged.

Neither part uses a typeface, so the files render the same everywhere without
embedded or installed fonts.

When editing the artwork, keep the geometry, stroke widths, and scales the same
in both files, and change only the colors between them.

## Provenance

The artwork was drawn for Posidon from SVG primitives: lines, arcs, curves,
circles, and triangles. It contains no fonts, raster images, clip art, or other
third-party material, so no third-party license, attribution, or font license
applies to it.
