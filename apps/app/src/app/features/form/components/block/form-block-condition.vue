<script setup lang="ts">
import { cFormBlockOperationItems } from '@/app/features/form/constants'
import type { iFormBlockCondition, iFormBlockDraft, tFormConditionOperator } from '@/app/features/form/types'

defineOptions({ name: 'FormBlockCondition' })

interface OperatorOption {
  label: string
  value: tFormConditionOperator
  icon: string
}

const props = defineProps<{
  block: iFormBlockDraft
  allBlocks?: iFormBlockDraft[]
  blockTypes: Record<string, { icon: string }>
  open?: boolean
}>()

const emit = defineEmits<{
  'update:block': [value: iFormBlockDraft]
  'update:open': [value: boolean]
}>()

const NO_VALUE_OPS = new Set<tFormConditionOperator>(['exists', 'not_exists'])

const operatorItems = cFormBlockOperationItems

const condition = computed(
  () => props.block.condition as iFormBlockCondition | Record<string, never>,
)
const hasCondition = computed(() => 'client_id' in condition.value)

const condSummary = computed(() => {
  if (!hasCondition.value) return ''
  const cond = condition.value as iFormBlockCondition
  const target = (props.allBlocks ?? []).find((b) => b.key === cond.client_id)
  const name = target?.title || 'Sem título'
  const op =
    operatorItems.find((o) => o.value === cond.operator)?.label?.toLowerCase() ?? cond.operator
  const val = NO_VALUE_OPS.has(cond.operator) ? '' : ` "${cond.value}"`
  return `Somente se: "${name}" ${op}${val}`
})

const otherBlocks = computed(() =>
  (props.allBlocks ?? [])
    .filter((b) => b.key !== props.block.key)
    .map((b) => ({
      label: b.title || 'Sem título',
      value: b.key,
      key: b.key,
      icon: props.blockTypes[b.type]?.icon ?? 'i-lucide-file-text',
    })),
)

const condBlockKey = ref<string | undefined>(
  hasCondition.value ? (condition.value as iFormBlockCondition).client_id : undefined,
)
const condOperator = ref<tFormConditionOperator>(
  hasCondition.value ? (condition.value as iFormBlockCondition).operator : 'eq',
)
const condValue = ref<string>(
  hasCondition.value ? String((condition.value as iFormBlockCondition).value ?? '') : '',
)

const condNeedsValue = computed(() => !NO_VALUE_OPS.has(condOperator.value))

function applyCondition() {
  if (condBlockKey.value === undefined) return
  emit('update:block', {
    ...props.block,
    condition: {
      client_id: condBlockKey.value,
      operator: condOperator.value,
      ...(condNeedsValue.value ? { value: condValue.value } : {}),
    },
  })
  emit('update:open', false)
}

function clearCondition() {
  emit('update:block', { ...props.block, condition: {} })
  condBlockKey.value = undefined
  condOperator.value = 'eq'
  condValue.value = ''
  emit('update:open', false)
}
</script>

<template>
  <UModal
    :open="open"
    title="Lógica condicional"
    :ui="{ content: 'sm:max-w-lg' }"
    @update:open="emit('update:open', $event)"
  >
    <template #body>
      <div class="flex flex-col gap-4">
        <p v-if="hasCondition" class="text-sm text-muted">{{ condSummary }}</p>

        <UFormField label="Mostrar esta pergunta somente se">
          <div class="flex flex-wrap items-center gap-2">
            <USelectMenu
              v-model="condBlockKey"
              :items="otherBlocks"
              value-key="key"
              label-key="label"
              placeholder="Selecione a pergunta..."
              variant="subtle"
              size="md"
              class="flex-1 min-w-40"
            >
              <template #item="{ item }">
                <UIcon :name="(item as { icon: string }).icon" class="size-4 text-muted" />
                <span class="truncate">{{ (item as { label: string }).label }}</span>
              </template>
            </USelectMenu>

            <USelectMenu
              v-model="condOperator"
              :items="operatorItems"
              value-key="value"
              label-key="label"
              variant="subtle"
              size="md"
              class="min-w-36"
            >
              <template #item="{ item }">
                <UIcon :name="(item as OperatorOption).icon" class="size-4 text-muted" />
                <span class="truncate">{{ (item as OperatorOption).label }}</span>
              </template>
            </USelectMenu>

            <UInput
              v-if="condNeedsValue"
              v-model="condValue"
              placeholder="Valor..."
              variant="subtle"
              size="md"
              class="flex-1 min-w-28"
            />
          </div>
        </UFormField>
      </div>
    </template>

    <template #footer>
      <div class="flex w-full justify-end gap-2">
        <UButton label="Limpar" variant="ghost" color="neutral" size="md" @click="clearCondition" />
        <UButton
          label="Aplicar"
          color="primary"
          size="md"
          :disabled="condBlockKey === undefined"
          @click="applyCondition"
        />
      </div>
    </template>
  </UModal>
</template>
