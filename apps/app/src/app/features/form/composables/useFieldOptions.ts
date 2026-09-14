import type { iFormBlockOption } from '@/app/features/form/types'

/** Shared add/remove/rename logic for the inline options list on select/choice field nodes. */
export function useFieldOptions(
  config: Ref<Record<string, unknown>>,
  updateConfig: (config: Record<string, unknown>) => void,
) {
  const currentOptions = computed<iFormBlockOption[]>(() =>
    Array.isArray(config.value?.options) ? (config.value.options as iFormBlockOption[]) : [],
  )

  const newOptionLabel = ref('')

  function addOption() {
    const label = newOptionLabel.value.trim()
    if (!label) return
    updateConfig({ ...config.value, options: [...currentOptions.value, { label, value: label }] })
    newOptionLabel.value = ''
  }

  function removeOption(index: number) {
    updateConfig({ ...config.value, options: currentOptions.value.filter((_, i) => i !== index) })
  }

  function updateOptionLabel(index: number, label: string) {
    updateConfig({
      ...config.value,
      options: currentOptions.value.map((opt, i) => (i === index ? { label, value: label } : opt)),
    })
  }

  return { currentOptions, newOptionLabel, addOption, removeOption, updateOptionLabel }
}
