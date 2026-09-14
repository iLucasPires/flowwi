<script setup lang="ts">
import { cFormBlockTypeItems } from '@/app/features/form/constants'
import type { iFormBlockDraft } from '@/app/features/form/types'

defineOptions({ name: 'FormBlockConfig' })

const props = defineProps<{ block: iFormBlockDraft; open?: boolean }>()
const emit = defineEmits<{
  'update:block': [value: iFormBlockDraft]
  'update:open': [value: boolean]
}>()

const typeLabel = computed(
  () => cFormBlockTypeItems.find((item) => item.value === props.block.type)?.label ?? '',
)

function updateConfig(key: string, value: unknown) {
  emit('update:block', { ...props.block, config: { ...props.block.config, [key]: value } })
}

function str(val: unknown) {
  return val == null ? '' : String(val)
}
</script>

<template>
  <UModal
    :open="open"
    :title="`Configurações — ${typeLabel}`"
    :ui="{ content: 'sm:max-w-md' }"
    @update:open="emit('update:open', $event)"
  >
    <template #body>
      <div class="flex flex-col gap-4">
        <!-- Text / Email -->
        <template v-if="block.type === 'text' || block.type === 'email'">
          <UFormField v-if="block.type === 'text'" label="Texto longo" description="Exibe uma área de texto em vez de um campo de linha única.">
            <USwitch
              :model-value="!!block.config.long"
              size="md"
              @update:model-value="(v) => updateConfig('long', v)"
            />
          </UFormField>

          <div class="grid grid-cols-2 gap-4">
            <UFormField label="Mín. caracteres">
              <UInput
                :model-value="str(block.config.min_length)"
                type="number"
                placeholder="0"
                variant="subtle"
                size="md"
                class="w-full"
                @update:model-value="(v) => updateConfig('min_length', Number(v))"
              />
            </UFormField>
            <UFormField label="Máx. caracteres">
              <UInput
                :model-value="str(block.config.max_length)"
                type="number"
                placeholder="∞"
                variant="subtle"
                size="md"
                class="w-full"
                @update:model-value="(v) => updateConfig('max_length', Number(v))"
              />
            </UFormField>
          </div>
        </template>

        <!-- Number -->
        <div v-if="block.type === 'number'" class="grid grid-cols-3 gap-4">
          <UFormField label="Mínimo">
            <UInput
              :model-value="str(block.config.min)"
              type="number"
              placeholder="—"
              variant="subtle"
              size="md"
              class="w-full"
              @update:model-value="(v) => updateConfig('min', Number(v))"
            />
          </UFormField>
          <UFormField label="Máximo">
            <UInput
              :model-value="str(block.config.max)"
              type="number"
              placeholder="—"
              variant="subtle"
              size="md"
              class="w-full"
              @update:model-value="(v) => updateConfig('max', Number(v))"
            />
          </UFormField>
          <UFormField label="Step">
            <UInput
              :model-value="str(block.config.step)"
              type="number"
              placeholder="1"
              variant="subtle"
              size="md"
              class="w-full"
              @update:model-value="(v) => updateConfig('step', Number(v))"
            />
          </UFormField>
        </div>

        <!-- File -->
        <UFormField
          v-if="block.type === 'file'"
          label="Múltiplos arquivos"
          description="Permite que a pessoa envie mais de um arquivo nesta pergunta."
        >
          <USwitch
            :model-value="!!block.config.multiple"
            size="md"
            @update:model-value="(v) => updateConfig('multiple', v)"
          />
        </UFormField>

        <!-- Select / Choice (only multiple toggle, options are edited inline) -->
        <UFormField
          v-if="block.type === 'select' || block.type === 'choice'"
          label="Seleção múltipla"
          description="Permite escolher mais de uma opção."
        >
          <USwitch
            :model-value="!!block.config.multiple"
            size="md"
            @update:model-value="(v) => updateConfig('multiple', v)"
          />
        </UFormField>
      </div>
    </template>
  </UModal>
</template>
