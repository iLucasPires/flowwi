export interface iMediaFeedback {
  id: number
  media: number
  version: number | null
  given_by: number
  decision: 1 | 2
  created_at: string
}

export interface iMediaComment {
  id: number
  media: number
  version: number | null
  author: number | null
  content: string
  block_index: number | null
  quote: string
  created_at: string
}

export interface iMediaVersion {
  id: number
  media: number
  number: number
  type: number
  file: string
  text_content: string
  feedbacks: iMediaFeedback[]
  comments: iMediaComment[]
  created_at: string
}

export const MEDIA_VERSION_TYPE_VIDEO = 2
export const MEDIA_VERSION_TYPE_TEXT = 5

export const MEDIA_TYPE_IMAGE = 1
export const MEDIA_TYPE_VIDEO = 2
export const MEDIA_TYPE_DOCUMENT = 3
export const MEDIA_TYPE_ART = 4

export type MediaType = 1 | 2 | 3 | 4

export interface iMedia {
  id: number
  task: number | null
  designer: number | null
  title: string
  notes: string
  type: MediaType
  is_approved: boolean
  share_token: string
  versions: iMediaVersion[]
  feedbacks: iMediaFeedback[]
  comments: iMediaComment[]
  created_at: string
  updated_at: string
}
