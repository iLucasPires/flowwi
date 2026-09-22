<script setup lang="ts">
import type { iDocumentVersion } from "@/app/features/document/types";
import { useWorkplaceMember } from "@/app/features/workplace/composables/workplaceMember";
import type {
  DropdownMenuItem,
  EditorCustomHandlers,
  EditorEmojiMenuItem,
  EditorMentionMenuItem,
  EditorSuggestionMenuItem,
  EditorToolbarItem,
} from "@nuxt/ui";
import { mapEditorItems } from "@nuxt/ui/utils/editor";
import type { Editor, JSONContent } from "@tiptap/vue-3";
import { Emoji, gitHubEmojis } from "@tiptap/extension-emoji";
import { TextAlign } from "@tiptap/extension-text-align";
import { upperFirst } from "scule";
import { CodeBlockShiki } from "tiptap-extension-code-block-shiki";
import { createImageUploadExtension } from "@/app/features/document/composables/editor/document-editor-image-upload";

defineOptions({ name: "DocumentEditor" });

const props = defineProps<{
  currentVersion: iDocumentVersion | undefined;
}>();

const emit = defineEmits<{
  contentChange: [value: string];
}>();

const { members: workplaceMembers } = useWorkplaceMember();

const mentionItems = computed<EditorMentionMenuItem[]>(() =>
  workplaceMembers.value.map((member) => ({
    label: member.profile?.username || "Sem nome",
    avatar: { src: member.profile?.photo || undefined, alt: member.profile?.username },
  })),
);

const emojiItems: EditorEmojiMenuItem[] = gitHubEmojis.filter(
  (emoji) => !emoji.name.startsWith("regional_indicator_"),
);

const customHandlers = {
  imageUpload: {
    canExecute: (editor: Editor) => editor.can().insertContent({ type: "imageUpload" }),
    execute: (editor: Editor) => editor.chain().focus().insertContent({ type: "imageUpload" }),
    isActive: (editor: Editor) => editor.isActive("imageUpload"),
    isDisabled: undefined,
  },
} satisfies EditorCustomHandlers;

const headingItems = [
  { kind: "heading", level: 1, icon: "i-lucide-heading-1", label: "Título 1" },
  { kind: "heading", level: 2, icon: "i-lucide-heading-2", label: "Título 2" },
  { kind: "heading", level: 3, icon: "i-lucide-heading-3", label: "Título 3" },
] as const;

const listItems = [
  { kind: "bulletList", icon: "i-lucide-list", label: "Lista com marcadores" },
  { kind: "orderedList", icon: "i-lucide-list-ordered", label: "Lista numerada" },
] as const;

const textAlignItems = [
  {
    kind: "textAlign" as const,
    align: "left" as const,
    icon: "i-lucide-align-left",
    label: "Alinhar à esquerda",
  },
  {
    kind: "textAlign" as const,
    align: "center" as const,
    icon: "i-lucide-align-center",
    label: "Centralizar",
  },
  {
    kind: "textAlign" as const,
    align: "right" as const,
    icon: "i-lucide-align-right",
    label: "Alinhar à direita",
  },
  {
    kind: "textAlign" as const,
    align: "justify" as const,
    icon: "i-lucide-align-justify",
    label: "Justificar",
  },
];

const bubbleToolbarItems = [
  [
    {
      label: "Transformar em",
      trailingIcon: "i-lucide-chevron-down",
      activeColor: "neutral",
      activeVariant: "ghost",
      tooltip: { text: "Transformar em" },
      content: { align: "start" },
      ui: { label: "text-xs" },
      items: [
        { type: "label", label: "Transformar em" },
        { kind: "paragraph", label: "Texto", icon: "i-lucide-type" },
        ...headingItems,
        ...listItems,
        { kind: "blockquote", label: "Citação", icon: "i-lucide-text-quote" },
        { kind: "codeBlock", label: "Bloco de código", icon: "i-lucide-square-code" },
      ],
    },
  ],
  [
    { kind: "mark", mark: "bold", icon: "i-lucide-bold", tooltip: { text: "Negrito" } },
    { kind: "mark", mark: "italic", icon: "i-lucide-italic", tooltip: { text: "Itálico" } },
    {
      kind: "mark",
      mark: "underline",
      icon: "i-lucide-underline",
      tooltip: { text: "Sublinhado" },
    },
    { kind: "mark", mark: "strike", icon: "i-lucide-strikethrough", tooltip: { text: "Riscado" } },
    { kind: "mark", mark: "code", icon: "i-lucide-code", tooltip: { text: "Código" } },
  ],
  [
    { slot: "link" as const, icon: "i-lucide-link" },
    { kind: "imageUpload", icon: "i-lucide-image", tooltip: { text: "Imagem" } },
  ],
  [
    {
      icon: "i-lucide-align-justify",
      tooltip: { text: "Alinhamento" },
      content: { align: "end" },
      items: textAlignItems,
    },
  ],
] satisfies EditorToolbarItem<typeof customHandlers>[][];

function imageToolbarItems(editor: Editor): EditorToolbarItem[][] {
  const node = editor.state.doc.nodeAt(editor.state.selection.from);

  return [
    [
      {
        icon: "i-lucide-download",
        to: node?.attrs?.src,
        download: true,
        tooltip: { text: "Baixar" },
      },
      {
        icon: "i-lucide-refresh-cw",
        tooltip: { text: "Substituir" },
        onClick: () => {
          const { state } = editor;
          const pos = state.selection.from;
          const targetNode = state.doc.nodeAt(pos);
          if (targetNode && targetNode.type.name === "image") {
            editor
              .chain()
              .focus()
              .deleteRange({ from: pos, to: pos + targetNode.nodeSize })
              .insertContentAt(pos, { type: "imageUpload" })
              .run();
          }
        },
      },
    ],
    [
      {
        icon: "i-lucide-trash-2",
        tooltip: { text: "Excluir" },
        onClick: () => {
          const { state } = editor;
          const pos = state.selection.from;
          const targetNode = state.doc.nodeAt(pos);
          if (targetNode && targetNode.type.name === "image") {
            editor
              .chain()
              .focus()
              .deleteRange({ from: pos, to: pos + targetNode.nodeSize })
              .run();
          }
        },
      },
    ],
  ];
}

const selectedNode = ref<{ node: JSONContent; pos: number }>();

function handleItems(editor: Editor): DropdownMenuItem[][] {
  if (!selectedNode.value?.node?.type) return [];

  return mapEditorItems(
    editor,
    [
      [
        { type: "label", label: upperFirst(selectedNode.value.node.type) },
        {
          label: "Transformar em",
          icon: "i-lucide-repeat-2",
          children: [
            { kind: "paragraph", label: "Texto", icon: "i-lucide-type" },
            ...headingItems,
            ...listItems,
            { kind: "blockquote", label: "Citação", icon: "i-lucide-text-quote" },
            { kind: "codeBlock", label: "Bloco de código", icon: "i-lucide-square-code" },
          ],
        },
        {
          kind: "clearFormatting",
          pos: selectedNode.value?.pos,
          label: "Limpar formatação",
          icon: "i-lucide-rotate-ccw",
        },
      ],
      [
        {
          kind: "duplicate",
          pos: selectedNode.value?.pos,
          label: "Duplicar",
          icon: "i-lucide-copy",
        },
        {
          label: "Copiar texto",
          icon: "i-lucide-clipboard",
          onSelect: async () => {
            if (!selectedNode.value) return;
            const node = editor.state.doc.nodeAt(selectedNode.value.pos);
            if (node) await navigator.clipboard.writeText(node.textContent);
          },
        },
      ],
      [
        {
          kind: "moveUp",
          pos: selectedNode.value?.pos,
          label: "Mover para cima",
          icon: "i-lucide-arrow-up",
        },
        {
          kind: "moveDown",
          pos: selectedNode.value?.pos,
          label: "Mover para baixo",
          icon: "i-lucide-arrow-down",
        },
      ],
      [
        {
          kind: "delete",
          pos: selectedNode.value?.pos,
          label: "Excluir",
          icon: "i-lucide-trash-2",
        },
      ],
    ],
    customHandlers,
  ) as DropdownMenuItem[][];
}

const suggestionItems = [
  [
    { type: "label", label: "Blocos básicos" },
    {
      kind: "paragraph",
      label: "Texto",
      description: "Comece a escrever texto comum.",
      icon: "i-lucide-type",
    },
    {
      kind: "heading",
      level: 1,
      label: "Título 1",
      description: "Título de seção grande.",
      icon: "i-lucide-heading-1",
    },
    {
      kind: "heading",
      level: 2,
      label: "Título 2",
      description: "Título de subseção médio.",
      icon: "i-lucide-heading-2",
    },
    {
      kind: "heading",
      level: 3,
      label: "Título 3",
      description: "Título pequeno de subseção.",
      icon: "i-lucide-heading-3",
    },
    {
      kind: "bulletList",
      label: "Lista com marcadores",
      description: "Crie uma lista simples com marcadores.",
      icon: "i-lucide-list",
    },
    {
      kind: "orderedList",
      label: "Lista numerada",
      description: "Crie uma lista numerada ordenada.",
      icon: "i-lucide-list-ordered",
    },
    {
      kind: "blockquote",
      label: "Citação",
      description: "Destaque uma citação ou reflexão.",
      icon: "i-lucide-text-quote",
    },
    {
      kind: "codeBlock",
      label: "Bloco de código",
      description: "Trecho de código com destaque de sintaxe.",
      icon: "i-lucide-square-code",
    },
    {
      kind: "horizontalRule",
      label: "Divisor",
      description: "Divida blocos visualmente com uma linha.",
      icon: "i-lucide-minus",
    },
  ],
  [
    { type: "label", label: "Mídia e Conexões" },
    {
      kind: "imageUpload",
      label: "Imagem",
      description: "Envie ou incorpore uma imagem.",
      icon: "i-lucide-image",
    },
    {
      kind: "mention",
      label: "Mencionar pessoa",
      description: "Mencione um membro da sua equipe.",
      icon: "i-lucide-at-sign",
    },
    {
      kind: "emoji",
      label: "Emoji",
      description: "Insira um emoji expressivo.",
      icon: "i-lucide-smile-plus",
    },
  ],
] satisfies EditorSuggestionMenuItem<typeof customHandlers>[][];
</script>

<template>
  <UEditor
    v-if="props.currentVersion"
    :key="props.currentVersion.id"
    v-slot="{ editor, handlers }"
    :model-value="props.currentVersion.content"
    content-type="markdown"
    :starter-kit="{ codeBlock: false }"
    :extensions="[
      TextAlign.configure({ types: ['heading', 'paragraph'] }),
      Emoji,
      createImageUploadExtension(),
      CodeBlockShiki.configure({
        defaultTheme: 'material-theme',
        themes: { light: 'material-theme-lighter', dark: 'material-theme-palenight' },
      }),
    ]"
    :handlers="customHandlers"
    placeholder="Pressione '/' para comandos..."
    :ui="{
      base: [
        'pl-0! pr-0! pt-0! pb-0!',
        'sm:pl-20! sm:-ml-20!',
        '[&_h1]:text-3xl [&_h1]:font-bold [&_h1]:tracking-tight [&_h1]:text-highlighted [&_h1]:mt-6 [&_h1]:mb-2',
        '[&_h2]:text-2xl [&_h2]:font-semibold [&_h2]:tracking-tight [&_h2]:text-highlighted [&_h2]:mt-5 [&_h2]:mb-1.5',
        '[&_h3]:text-xl [&_h3]:font-semibold [&_h3]:tracking-tight [&_h3]:text-highlighted [&_h3]:mt-4 [&_h3]:mb-1',
        '[&_p]:text-[15px] [&_p]:leading-7 [&_p]:text-default [&_p]:my-1',
        '[&_blockquote]:border-s-3 [&_blockquote]:border-default [&_blockquote]:ps-4 [&_blockquote]:my-2 [&_blockquote]:text-toned [&_blockquote]:italic',
        '[&_ul]:list-disc [&_ul]:ps-5 [&_ul]:my-1.5 [&_ul]:leading-relaxed',
        '[&_ol]:list-decimal [&_ol]:ps-5 [&_ol]:my-1.5 [&_ol]:leading-relaxed',
        '[&_hr]:border-default [&_hr]:my-4',
      ],
    }"
    @update:model-value="emit('contentChange', $event as string)"
  >
    <UEditorToolbar
      :editor="editor"
      :items="bubbleToolbarItems"
      layout="bubble"
      :should-show="
        ({ editor, view, state }) => {
          if (editor.isActive('imageUpload') || editor.isActive('image')) return false;
          const { selection } = state;
          return view.hasFocus() && !selection.empty;
        }
      "
    >
      <template #link>
        <CDocumentEditorLinkPopover :editor="editor" />
      </template>
    </UEditorToolbar>

    <UEditorToolbar
      :editor="editor"
      :items="imageToolbarItems(editor)"
      layout="bubble"
      :should-show="({ editor, view }) => editor.isActive('image') && view.hasFocus()"
    />

    <UEditorSuggestionMenu :editor="editor" :items="suggestionItems" />

    <UEditorMentionMenu :editor="editor" :items="mentionItems" />

    <UEditorEmojiMenu :editor="editor" :items="emojiItems" />

    <UEditorDragHandle
      v-slot="{ ui, onClick }"
      :editor="editor"
      @node-change="selectedNode = $event"
    >
      <UButton
        icon="i-lucide-plus"
        color="neutral"
        variant="ghost"
        size="sm"
        :class="typeof ui?.handle === 'function' ? ui.handle() : ''"
        @click="
          (event) => {
            event.stopPropagation();
            const selected = onClick?.();
            handlers.suggestion?.execute(editor, { pos: selected?.pos }).run();
          }
        "
      />

      <UDropdownMenu
        v-slot="{ open }"
        :modal="false"
        :items="handleItems(editor)"
        :content="{ side: 'left' }"
        :ui="{ content: 'w-48', label: 'text-xs' }"
        @update:open="editor.chain().setMeta('lockDragHandle', $event).run()"
      >
        <UButton
          color="neutral"
          variant="ghost"
          active-variant="soft"
          size="sm"
          icon="i-lucide-grip-vertical"
          :active="open"
          :class="typeof ui?.handle === 'function' ? ui.handle() : ''"
        />
      </UDropdownMenu>
    </UEditorDragHandle>
  </UEditor>
</template>
