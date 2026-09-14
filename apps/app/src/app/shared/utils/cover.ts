import type { CSSProperties } from 'vue'

/** True when a cover style holds an image URL instead of a CSS color/gradient. */
export function isCoverImageUrl(style?: string | null): boolean {
  return !!style && (/^https?:\/\//.test(style) || style.startsWith('/'))
}

/**
 * Background for a cover rendered as a plain element: an uploaded file or an image URL
 * becomes a centered cover image, anything else is used as a raw CSS background.
 */
export function coverBackgroundStyle(
  src?: string | null,
  style?: string | null,
): CSSProperties | undefined {
  const imageUrl = src || (isCoverImageUrl(style) ? style : null)

  if (imageUrl) {
    return {
      backgroundImage: `url(${imageUrl})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
    }
  }

  return style ? { background: style } : undefined
}

/** The URL to render in an `<img>` for a cover, if the cover is an image at all. */
export function coverImageSrc(src?: string | null, style?: string | null): string | null {
  if (src) return src

  return isCoverImageUrl(style) ? (style as string) : null
}
