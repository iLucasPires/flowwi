<script setup lang="ts">
import { parseTime } from '@internationalized/date'
import type { TimeValue } from 'reka-ui'

const model = defineModel<string | undefined>()

const timeValue = computed<TimeValue | undefined>({
  get() {
    if (!model.value) return undefined
    try {
      return parseTime(model.value) as TimeValue
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
  <UInputTime v-model="timeValue" v-bind="$attrs" />
</template>
z
