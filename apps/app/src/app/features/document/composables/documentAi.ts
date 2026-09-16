import { API_DOCUMENT_URLS, apiFetch } from "@/app/core/clients/api";
import type { iDocument, iDocumentVersion } from "@/app/features/document/types";
export const DOCUMENT_AI_ACTIONS = [
  { key: "resumir", label: "Resumir doc" },
  { key: "continuar", label: "Continuar escrevendo" },
  { key: "titulos", label: "Sugerir títulos" },
  { key: "encurtar", label: "Encurtar 30%" },
];

/** Canned + free-text AI actions on the active document, appending results as new lines. */
export function useDocumentAi(
  activeDoc: ComputedRef<iDocument | undefined>,
  currentVersion: ComputedRef<iDocumentVersion | undefined>,
) {
  const toast = useToast();

  const prompt = ref("");
  const output = ref("");
  const activeLabel = ref("");
  const runningKey = ref<string | null>(null);
  const running = computed(() => runningKey.value != null);

  async function run(actionKey?: string) {
    const doc = activeDoc.value;
    if (!doc || (!actionKey && !prompt.value.trim())) return;

    runningKey.value = actionKey ?? "custom";
    try {
      const res = await apiFetch<{ output: string }>(API_DOCUMENT_URLS.AI_ASSIST(doc.id), {
        method: "POST",
        body: {
          action: actionKey ?? "",
          prompt: prompt.value.trim(),
        },
      });
      output.value = res.output;
      activeLabel.value = actionKey
        ? (DOCUMENT_AI_ACTIONS.find((a) => a.key === actionKey)?.label ?? "")
        : "Resultado";
    } catch {
      toast.add({ title: "Erro ao gerar com IA", color: "error" });
    } finally {
      runningKey.value = null;
    }
  }

  function clear() {
    output.value = "";
    activeLabel.value = "";
  }

  function insert() {
    const version = currentVersion.value;
    if (!version || !output.value || version.status === "published") return;

    version.content = version.content ? `${version.content}\n\n${output.value}` : output.value;

    apiFetch(`${API_DOCUMENT_URLS.VERSIONS}/${version.id}`, {
      method: "PATCH",
      body: { content: version.content },
    }).catch(() =>
      toast.add({
        title: "Erro ao salvar",
        color: "error",
      }),
    );

    clear();
  }

  return {
    prompt,
    output,
    activeLabel,
    running,
    runningKey,
    run,
    clear,
    insert,
  };
}
