import type { Editor, NodeViewRenderer } from '@tiptap/core'
import { Node, mergeAttributes } from '@tiptap/core'
import type { Component } from 'vue'
import { VueNodeViewRenderer } from '@tiptap/vue-3'
import { cFormDefaultBlockConfigs } from '@/app/features/form/constants'
import type { iFormBlockCondition, tFormBlockType } from '@/app/features/form/types'

/** Attrs shared by every field node type — the type itself lives in the node *name*, not an attr. */
export interface iFieldAttrs {
  blockKey: string
  title: string
  required: boolean
  config: Record<string, unknown>
  condition: iFormBlockCondition | Record<string, never>
}

/** Maps a `tFormBlockType` (the flat, persisted shape) to its dedicated Tiptap node name. */
export const FIELD_NODE_NAMES: Record<Exclude<tFormBlockType, 'content'>, string> = {
  text: 'textField',
  email: 'emailField',
  number: 'numberField',
  date: 'dateField',
  time: 'timeField',
  select: 'selectField',
  choice: 'choiceField',
  file: 'fileField',
}

/** Reverse of {@link FIELD_NODE_NAMES}, built once. */
export const FIELD_TYPE_BY_NODE_NAME: Record<string, tFormBlockType> = Object.fromEntries(
  Object.entries(FIELD_NODE_NAMES).map(([type, name]) => [name, type as tFormBlockType]),
)

function jsonAttr(name: string, fallback: unknown) {
  return {
    default: fallback,
    parseHTML: (element: HTMLElement) => {
      const raw = element.getAttribute(`data-${name}`)
      if (!raw) return fallback
      try {
        return JSON.parse(raw)
      } catch {
        return fallback
      }
    },
    renderHTML: (attrs: Record<string, unknown>) => ({
      [`data-${name}`]: JSON.stringify(attrs[name] ?? fallback),
    }),
  }
}

/**
 * Builds one dedicated Tiptap node type for a single field type (e.g. `textField`,
 * `emailField`…) — kept as small, near-identical extensions rather than one generic node with
 * a `fieldType` switch, so each has its own simple, single-purpose NodeView.
 */
export function createFieldExtension(nodeName: string, component: Component) {
  return Node.create({
    name: nodeName,
    group: 'block',
    atom: true,
    draggable: true,
    addAttributes() {
      return {
        blockKey: jsonAttr('block-key', ''),
        title: jsonAttr('title', ''),
        required: jsonAttr('required', false),
        config: jsonAttr('config', {}),
        condition: jsonAttr('condition', {}),
      }
    },
    parseHTML() {
      return [{ tag: `div[data-type="${nodeName}"]` }]
    },
    renderHTML({ HTMLAttributes }) {
      return ['div', mergeAttributes(HTMLAttributes, { 'data-type': nodeName })]
    },
    addNodeView(): NodeViewRenderer {
      return VueNodeViewRenderer(component)
    },
  })
}

/**
 * Inserts a field node by name at the current selection (used by the slash-menu's custom
 * handler). Also inserts a trailing empty paragraph and lets `insertContent` select it: without
 * it, the atom node stays under a bare NodeSelection, and ProseMirror's default
 * Enter-near-selection heuristic inserts the *next* block before it whenever it's the first
 * child (i.e. on every insert into a short document) — which reverses the order typed.
 */
export function insertFieldNode(
  editor: Editor,
  nodeName: string,
  fieldType: tFormBlockType,
  configOverride?: Record<string, unknown>,
) {
  return editor
    .chain()
    .focus()
    .insertContent([
      {
        type: nodeName,
        attrs: {
          blockKey: crypto.randomUUID(),
          title: '',
          required: false,
          config: {
            ...structuredClone(cFormDefaultBlockConfigs[fieldType] ?? {}),
            ...configOverride,
          },
          condition: {},
        },
      },
      { type: 'paragraph' },
    ])
}
