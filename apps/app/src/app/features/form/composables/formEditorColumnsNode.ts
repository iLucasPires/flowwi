import FormEditorColumnsNode from '@/app/features/form/components/editor/node/form-editor-columns-node.vue'
import type { NodeViewRenderer } from '@tiptap/core'
import { Node, mergeAttributes } from '@tiptap/core'
import { VueNodeViewRenderer } from '@tiptap/vue-3'

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    formColumns: {
      insertFormColumns: (columns: number) => ReturnType
    }
  }
}

/** A row of `columns` equal-width `formColumn` cells — the structural unit for side-by-side fields. */
export function createFormColumnsExtension() {
  return Node.create({
    name: 'formColumns',
    group: 'block',
    content: 'formColumn{2,4}',
    addAttributes() {
      return { columns: { default: 2 } }
    },
    parseHTML() {
      return [{ tag: 'div[data-type="form-columns"]' }]
    },
    renderHTML({ HTMLAttributes }) {
      return ['div', mergeAttributes(HTMLAttributes, { 'data-type': 'form-columns' }), 0]
    },
    addNodeView(): NodeViewRenderer {
      return VueNodeViewRenderer(FormEditorColumnsNode)
    },
    addCommands() {
      return {
        // Built via raw node creation + `replaceSelectionWith` rather than the higher-level
        // `insertContent` JSON helper: at a collapsed cursor inside a plain paragraph,
        // `insertContent` was silently "fitting" this deeply nested tree down to just its
        // leaf paragraphs, dropping the formColumns/formColumn wrappers entirely.
        // `replaceSelectionWith` is the primitive built for "swap the selection for this one
        // block node" and handles the surrounding paragraph correctly.
        insertFormColumns:
          (columns: number) =>
          ({ tr, dispatch, state }) => {
            const { schema } = state
            const columnType = schema.nodes.formColumn
            const columnsType = schema.nodes.formColumns
            const paragraphType = schema.nodes.paragraph
            if (!columnType || !columnsType || !paragraphType) return false

            const node = columnsType.create(
              { columns },
              Array.from({ length: columns }, () => columnType.create(null, paragraphType.create())),
            )

            if (dispatch) tr.replaceSelectionWith(node)
            return true
          },
      }
    },
  })
}

/** One cell inside a `formColumns` row. Isolating so backspace/selection can't merge across cells. */
export function createFormColumnExtension() {
  return Node.create({
    name: 'formColumn',
    content: 'block*',
    defining: true,
    isolating: true,
    parseHTML() {
      return [{ tag: 'div[data-type="form-column"]' }]
    },
    renderHTML({ HTMLAttributes }) {
      return ['div', mergeAttributes(HTMLAttributes, { 'data-type': 'form-column' }), 0]
    },
  })
}
