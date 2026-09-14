<script setup lang="ts">
import { parseDate } from '@internationalized/date'
import type { DateValue } from 'reka-ui'

const model = defineModel<string | undefined>()

const dateValue = computed<DateValue | undefined>({
  get() {
    if (!model.value) return undefined
    try {
      return parseDate(model.value)
    } catch {
      return undefined
    }
  },
  set(val) {
    model.value = val?.toString() ?? undefined
  },
})
</script>

<template>
  <UInputDate v-model="dateValue" v-bind="$attrs" />
</template>
