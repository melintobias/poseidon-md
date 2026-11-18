# Logo

The Posidon logo pairs a trident with a sine wave. The wave stands for both the
sea and an audio signal, which ties the name to what the tool does. The SVG
files in this directory are the source of truth for the logo.

## Files

| File                                             | Use                                                      |
| ------------------------------------------------ | -------------------------------------------------------- |
| [`posidon-logo.svg`](posidon-logo.svg)           | Symbol and wordmark for light backgrounds.               |
| [`posidon-logo-dark.svg`](posidon-logo-dark.svg) | Symbol and wordmark for dark backgrounds.                |
| [`posidon-mark.svg`](posidon-mark.svg)           | Symbol only, for light backgrounds.                      |
| [`posidon-mark-dark.svg`](posidon-mark-dark.svg) | Symbol only, for dark backgrounds.                       |
| [`posidon-icon.svg`](posidon-icon.svg)           | App icon with its own background, for avatars and icons. |

### Alternative symbol

The seagrass symbol adds two blades of sea grass that rise from the wave on
either side of the shaft. It uses the same grid and position as the primary
symbol, so it can replace that symbol in any layout. The blades blur below
about 32 px, so keep the primary symbol for favicons and other small sizes.

| File                                                               | Use                                          |
| ------------------------------------------------------------------ | -------------------------------------------- |
| [`posidon-mark-seagrass.svg`](posidon-mark-seagrass.svg)           | Seagrass symbol only, for light backgrounds. |
| [`posidon-mark-seagrass-dark.svg`](posidon-mark-seagrass-dark.svg) | Seagrass symbol only, for dark backgrounds.  |

## Colors

| Hex       | Role                                              |
| --------- | ------------------------------------------------- |
| `#0B2A4A` | Trident and wordmark on light; icon backdrop.     |
| `#0F8B8D` | Wave, sea grass, and the dot on the `i` on light. |
| `#E6F6F4` | Trident and wordmark on dark and in the icon.     |
| `#2DD4BF` | Wave, sea grass, and the dot on the `i` on dark.  |

## Usage

- Use the light variants on light backgrounds and the dark variants on dark
  backgrounds. The icon works on either.
- Keep clear space around the logo at least as large as the height of the
  lowercase letters.
- Keep the symbol at least 16 px tall, and the full logo at least 24 px tall.
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
circles, elliptical arcs, and straight lines, scaled to 84% beside the symbol.
Neither part uses a typeface, so the files render the same everywhere without
embedded or installed fonts.

When editing the artwork, keep the stroke widths and colors consistent across
all files.

## Provenance

The artwork was drawn for Posidon from SVG primitives: lines, arcs, circles, and
triangles. It contains no fonts, raster images, clip art, or other third-party
material, so no third-party license, attribution, or font license applies to it.
