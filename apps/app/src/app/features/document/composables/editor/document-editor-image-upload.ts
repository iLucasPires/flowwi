import DocumentEditorImageUploadNode from "@/app/features/document/components/editor/document-editor-image-upload-node.vue";
import type { CommandProps, NodeViewRenderer } from "@tiptap/core";
import { Node, mergeAttributes } from "@tiptap/core";
import { VueNodeViewRenderer } from "@tiptap/vue-3";

declare module "@tiptap/core" {
  interface Commands<ReturnType> {
    imageUpload: {
      insertImageUpload: () => ReturnType;
    };
  }
}

/** Tiptap node that renders a drop-zone; picking a file inlines it as a data URL image. */
export function createImageUploadExtension() {
  return Node.create({
    name: "imageUpload",
    group: "block",
    atom: true,
    draggable: true,
    addAttributes() {
      return {};
    },
    parseHTML() {
      return [{ tag: 'div[data-type="image-upload"]' }];
    },
    renderHTML({ HTMLAttributes }) {
      return ["div", mergeAttributes(HTMLAttributes, { "data-type": "image-upload" })];
    },
    addNodeView(): NodeViewRenderer {
      return VueNodeViewRenderer(DocumentEditorImageUploadNode);
    },
    addCommands() {
      return {
        insertImageUpload:
          () =>
          ({ commands }: CommandProps) => {
            return commands.insertContent({ type: this.name });
          },
      };
    },
  });
}
