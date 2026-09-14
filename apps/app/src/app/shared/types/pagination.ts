export interface iPaginationNumber<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface iPaginationCursor<T> {
  cursor: string | null
  results: T[]
}
