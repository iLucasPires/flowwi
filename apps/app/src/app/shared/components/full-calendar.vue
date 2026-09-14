<script setup lang="ts">
import type { iCalendarDay, iCalendarEvent } from '@/app/shared/types/calendar'
defineOptions({ name: 'UiCalendar' })

const props = withDefaults(
  defineProps<{
    events: iCalendarEvent[]
    title?: string
    description?: string
    embedded?: boolean
  }>(),
  { title: 'Calendário', description: 'Visualização de eventos e prazos', embedded: false },
)

const emit = defineEmits<{
  select: [event: iCalendarEvent]
  'day-click': [date: string]
}>()

const today = new Date()
const currentMonth = ref(today.getMonth())
const currentYear = ref(today.getFullYear())
const weekDays = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']

const monthLabel = computed(() =>
  new Date(currentYear.value, currentMonth.value).toLocaleDateString('pt-BR', {
    month: 'long',
    year: 'numeric',
  }),
)

function prevMonth() {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else currentMonth.value--
}
function nextMonth() {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else currentMonth.value++
}
function goToday() {
  currentMonth.value = today.getMonth()
  currentYear.value = today.getFullYear()
}

function eventsForDate(dateKey: string): iCalendarEvent[] {
  return props.events.filter((e) => e.date === dateKey)
}

const days = computed<iCalendarDay[]>(() => {
  const year = currentYear.value,
    month = currentMonth.value
  const firstDay = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const daysInPrevMonth = new Date(year, month, 0).getDate()
  const result: iCalendarDay[] = []
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`

  for (let i = firstDay - 1; i >= 0; i--) {
    const d = daysInPrevMonth - i,
      m = month === 0 ? 11 : month - 1,
      y = month === 0 ? year - 1 : year
    const key = `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    result.push({
      date: d,
      month: m,
      year: y,
      key,
      isCurrentMonth: false,
      isToday: false,
      events: eventsForDate(key),
    })
  }

  for (let d = 1; d <= daysInMonth; d++) {
    const key = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    result.push({
      date: d,
      month,
      year,
      key,
      isCurrentMonth: true,
      isToday: key === todayStr,
      events: eventsForDate(key),
    })
  }

  const remaining = 42 - result.length
  for (let d = 1; d <= remaining; d++) {
    const m = month === 11 ? 0 : month + 1,
      y = month === 11 ? year + 1 : year
    const key = `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    result.push({
      date: d,
      month: m,
      year: y,
      key,
      isCurrentMonth: false,
      isToday: false,
      events: eventsForDate(key),
    })
  }

  return result
})
</script>

<template>
  <div class="size-full flex flex-col overflow-hidden">
    <!-- Header -->
    <div class="flex items-center gap-3 px-6 py-4">
      <UPageFeature
        v-if="!embedded"
        :title="title"
        :description="description"
        color="neutral"
        size="sm"
      />
      <div class="ml-auto flex items-center gap-2">
        <span class="text-sm font-semibold capitalize">{{ monthLabel }}</span>
        <UButton
          icon="i-lucide-chevron-left"
          variant="ghost"
          color="neutral"
          size="xs"
          @click="prevMonth"
        />
        <UButton label="Hoje" variant="outline" color="neutral" size="xs" @click="goToday" />
        <UButton
          icon="i-lucide-chevron-right"
          variant="ghost"
          color="neutral"
          size="xs"
          @click="nextMonth"
        />
      </div>
    </div>

    <!-- Grid -->
    <div class="flex-1 overflow-y-auto px-6 pb-4">
      <div class="grid grid-cols-7 border-b border-neutral-800">
        <div
          v-for="day in weekDays"
          :key="day"
          class="py-2 text-center text-xs font-medium text-neutral-500"
        >
          {{ day }}
        </div>
      </div>

      <div class="grid grid-cols-7 flex-1 auto-rows-fr">
        <div
          v-for="day in days"
          :key="day.key"
          class="border-b border-r border-neutral-800/50 p-1.5 min-h-[90px] cursor-pointer transition-colors hover:bg-white/[0.02]"
          :class="{ 'bg-white/[0.015]': day.isCurrentMonth }"
          @click="emit('day-click', day.key)"
        >
          <div class="flex items-center justify-between mb-1">
            <span
              class="text-xs font-medium size-6 flex items-center justify-center rounded-full"
              :class="[
                day.isToday
                  ? 'bg-primary text-white'
                  : day.isCurrentMonth
                    ? 'text-neutral-300'
                    : 'text-neutral-600',
              ]"
            >
              {{ day.date }}
            </span>
          </div>
          <div class="space-y-0.5">
            <button
              v-for="event in day.events.slice(0, 3)"
              :key="event.id"
              class="w-full flex items-center gap-1 px-1.5 py-0.5 rounded text-left transition-colors hover:bg-white/5 group"
              @click.stop="emit('select', event)"
            >
              <span
                class="size-1.5 rounded-full shrink-0"
                :style="{ backgroundColor: event.color ?? '#6b7280' }"
              />
              <span class="text-[11px] truncate text-neutral-300 group-hover:text-white">{{
                event.title
              }}</span>
            </button>
            <p v-if="day.events.length > 3" class="text-[10px] text-neutral-500 px-1.5">
              +{{ day.events.length - 3 }} mais
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
