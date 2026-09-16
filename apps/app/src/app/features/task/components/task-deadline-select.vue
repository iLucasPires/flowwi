<script setup lang="ts">
import { formatDeadline } from '@/app/features/task/utils'
import type { CalendarDate } from '@internationalized/date'

const model = defineModel<CalendarDate | null>()

const props = defineProps<{
  size?: string
}>()

function toStr(deadline: CalendarDate | null | undefined): string | null {
  return deadline ? deadline.toString() : null
}

const label = computed(() => formatDeadline(toStr(model.value)) ?? 'Prazo')
</script>

<template>
  <UPopover>
    <UButton :size="props.size" variant="ghost" color="neutral" icon="i-lucide-calendar" :label="label" />
    <template #content>
      <div class="p-2">
        <UCalendar v-model="model" />
        <UButton
          v-if="model"
          label="Remover prazo"
          icon="i-lucide-x"
          color="neutral"
          variant="ghost"
          size="xs"
          block
          class="mt-1"
          @click="model = null"
        />
      </div>
    </template>
  </UPopover>
</template>
