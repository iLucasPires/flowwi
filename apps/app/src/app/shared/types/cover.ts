import type { iUnsplashCredit } from './unsplash'

/** Attribution for the current cover, when its source demands one. */
export type iCoverCredit = iUnsplashCredit | null

/**
 * What a cover picker hands back to the screen using it: an uploaded file, a style
 * (CSS color/gradient or an image URL), or `null` to clear the cover entirely.
 */
export type iCoverUpdate = { file: File } | { style: string; credit: iCoverCredit } | null
