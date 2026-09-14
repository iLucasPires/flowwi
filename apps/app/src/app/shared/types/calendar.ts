export interface iCalendarEvent {
  id: string
  title: string
  date: string
  color?: string
  icon?: string
  type?: string
  meta?: Record<string, unknown>
}

export interface iCalendarDay {
  date: number
  month: number
  year: number
  key: string
  isCurrentMonth: boolean
  isToday: boolean
  events: iCalendarEvent[]
}
