import type { JSONContent } from '@tiptap/vue-3'
import type { iFieldAttrs } from './formEditorFieldNode'
import { FIELD_NODE_NAMES, FIELD_TYPE_BY_NODE_NAME } from './formEditorFieldNode'
import type { iFormBlockCondition, iFormBlockDraft } from '@/app/features/form/types'

function fieldNode(block: iFormBlockDraft): JSONContent {
  const nodeName = FIELD_NODE_NAMES[block.type as keyof typeof FIELD_NODE_NAMES]
  const attrs: iFieldAttrs = {
    blockKey: block.key,
    title: block.title,
    required: block.required,
    config: block.config,
    condition: block.condition,
  }
  return { type: nodeName, attrs }
}

function contentBlock(node: JSONContent): iFormBlockDraft {
  return {
    key: crypto.randomUUID(),
    title: '',
    type: 'content',
    required: false,
    config: { node },
    col_span: 0,
    col_start: 0,
    condition: {},
  }
}

/**
 * Converts the flat `iFormBlockDraft[]` list (the shape `useFormEditor`/the bulk-save API
 * already speak) into a Tiptap document. Non-content blocks become their dedicated field node
 * (`textField`, `emailField`… per {@link FIELD_NODE_NAMES}); `content` blocks re-embed their
 * stored ProseMirror node verbatim. Blocks that share a `col_start` (repurposed here as "how
 * many columns this row has", set by {@link docToBlocks}) of 2 or more are regrouped into a
 * `formColumns` row of that many `formColumn` cells — the structural stand-in for "these fields
 * sit side by side".
 *
 * Must stay a stable round-trip with {@link docToBlocks} (same key order, no normalization) —
 * `UEditor` diffs `JSON.stringify(doc)` against its live content on every keystroke and only
 * calls `setContent` when they differ, so any drift here causes cursor jumps while typing.
 */
export function blocksToDoc(blocks: iFormBlockDraft[]): JSONContent {
  const content: JSONContent[] = []
  let i = 0

  // A block's `col_start` (row width) decides grouping regardless of whether it's a field or
  // a `content` block — an empty column is still a column, so this check must come before the
  // content/field split, not after (checking content-type first meant an empty column's
  // placeholder paragraph could never be regrouped back into its formColumns row).
  while (i < blocks.length) {
    const block = blocks[i]!
    const rowWidth = block.col_start

    if (rowWidth >= 2) {
      const row: iFormBlockDraft[] = []
      let j = i
      while (j < blocks.length && row.length < rowWidth && blocks[j]!.col_start === rowWidth) {
        row.push(blocks[j]!)
        j++
      }

      if (row.length === rowWidth) {
        content.push({
          type: 'formColumns',
          attrs: { columns: rowWidth },
          content: row.map((b) => ({
            type: 'formColumn',
            content: [b.type === 'content' ? ((b.config?.node as JSONContent | undefined) ?? { type: 'paragraph' }) : fieldNode(b)],
          })),
        })
        i = j
        continue
      }
      // Fewer than `rowWidth` blocks actually share this row (e.g. one was deleted) — fall
      // through and emit them standalone rather than building an invalid formColumns node.
    }

    content.push(block.type === 'content' ? ((block.config?.node as JSONContent | undefined) ?? { type: 'paragraph' }) : fieldNode(block))
    i++
  }

  return {
    type: 'doc',
    content: content.length ? content : [{ type: 'paragraph' }],
  }
}

/** Inverse of {@link blocksToDoc}. */
export function docToBlocks(doc: JSONContent): iFormBlockDraft[] {
  const nodes = doc.content ?? []
  const blocks: iFormBlockDraft[] = []

  function pushFromNode(node: JSONContent, rowWidth: number) {
    const fieldType = node.type ? FIELD_TYPE_BY_NODE_NAME[node.type] : undefined
    if (fieldType) {
      const attrs = (node.attrs ?? {}) as Partial<iFieldAttrs>
      blocks.push({
        key: attrs.blockKey || crypto.randomUUID(),
        title: attrs.title ?? '',
        type: fieldType,
        required: !!attrs.required,
        config: attrs.config ?? {},
        col_span: rowWidth ? 1 : 0,
        col_start: rowWidth,
        condition: (attrs.condition ?? {}) as iFormBlockCondition | Record<string, never>,
      })
      return
    }

    blocks.push({ ...contentBlock(node), col_span: rowWidth ? 1 : 0, col_start: rowWidth })
  }

  for (const node of nodes) {
    if (node.type === 'formColumns') {
      const columns = (node.attrs?.columns as number | undefined) ?? node.content?.length ?? 2
      for (const columnNode of node.content ?? []) {
        for (const inner of columnNode.content ?? []) {
          pushFromNode(inner, columns)
        }
      }
      continue
    }

    if (node.type && FIELD_TYPE_BY_NODE_NAME[node.type]) {
      pushFromNode(node, 0)
      continue
    }

    blocks.push(contentBlock(node))
  }

  return blocks
}
