/** Attribution stored alongside a cover — Unsplash requires it to be displayed. */
export interface iUnsplashCredit {
  source: 'unsplash'
  photo_id: string
  photo_url: string
  author_name: string
  author_username: string
  author_url: string
}

/** A photo as returned by the backend proxy (`/api/unsplash/photos`). */
export interface iUnsplashPhoto {
  id: string
  color: string | null
  blur_hash: string | null
  width: number
  height: number
  description: string
  thumb_url: string
  preview_url: string
  cover_url: string
  download_location: string
  credit: iUnsplashCredit
}

export interface iUnsplashPhotoPage {
  results: iUnsplashPhoto[]
  page: number
  total_pages: number | null
}
