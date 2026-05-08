<script lang="ts">
  import { onMount } from "svelte";
  import { open as openDialog } from "@tauri-apps/api/dialog";
  import { invoke } from "@tauri-apps/api/tauri";

  type OutputFormat = "md" | "docx" | "html";
  type ThemeMode = "light" | "dark";

  type CoreResult = {
    ok: boolean;
    warnings: string[];
    outputs: Record<string, string>;
    error?: string;
  };

  const formatLabels: Record<string, string> = {
    md: "Markdown",
    docx: "Word",
    html: "HTML / Salvar PDF",
    png: "PNG do diagrama de relacionamentos"
  };
  const outputFormats: OutputFormat[] = ["md", "docx", "html"];

  let selectedPath = "";
  let outputPath = "";
  let exportResult: CoreResult | null = null;
  let errorMessage = "";
  let isExporting = false;
  let theme: ThemeMode = "light";
  let selectedFormats: Record<OutputFormat, boolean> = {
    md: true,
    docx: true,
    html: true
  };

  const labelForFormat = (format: string): string =>
    formatLabels[format] ?? format.toUpperCase();

  const parentFolder = (path: string): string =>
    path.replace(/[\\/][^\\/]+$/, "");

  const joinLabels = (labels: string[]): string => {
    if (labels.length <= 1) {
      return labels[0] ?? "";
    }
    return `${labels.slice(0, -1).join(", ")} e ${labels[labels.length - 1]}`;
  };

  const applyTheme = (mode: ThemeMode) => {
    theme = mode;
    document.documentElement.dataset.theme = mode;
    localStorage.setItem("bi-doc-maker-theme", mode);
  };

  onMount(() => {
    const storedTheme = localStorage.getItem("bi-doc-maker-theme");
    if (storedTheme === "light" || storedTheme === "dark") {
      applyTheme(storedTheme);
      return;
    }

    const systemTheme = window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
    applyTheme(systemTheme);
  });

  $: activeFormats = outputFormats.filter((format) => selectedFormats[format]);
  $: canExport =
    Boolean(selectedPath) &&
    Boolean(outputPath) &&
    activeFormats.length > 0 &&
    !isExporting;

  const toggleTheme = () => {
    applyTheme(theme === "dark" ? "light" : "dark");
  };

  const pickProjectFolder = async () => {
    const result = await openDialog({ directory: true, multiple: false });
    if (typeof result === "string") {
      selectedPath = result;
      if (!outputPath) {
        outputPath = result;
      }
      exportResult = null;
      errorMessage = "";
    }
  };

  const pickOutputFolder = async () => {
    const result = await openDialog({ directory: true, multiple: false });
    if (typeof result === "string") {
      outputPath = result;
      exportResult = null;
      errorMessage = "";
    }
  };

  const exportDocumentation = async () => {
    const formats = activeFormats;
    if (!selectedPath || !outputPath || formats.length === 0) {
      errorMessage = "Informe projeto, pasta de saida e ao menos um formato.";
      return;
    }

    isExporting = true;
    errorMessage = "";
    exportResult = null;

    try {
      const result = await invoke<CoreResult>("export_project", {
        path: selectedPath,
        outputDir: outputPath,
        formats
      });
      if (!result.ok) {
        throw new Error(result.error ?? "Falha ao gerar a documentacao.");
      }
      exportResult = result;
      if (result.outputs.html) {
        await invoke("open_output_file", { path: result.outputs.html });
      }
    } catch (error) {
      errorMessage = String(error);
    } finally {
      isExporting = false;
    }
  };

  const openOutputFolder = async () => {
    const firstOutput = exportResult ? Object.values(exportResult.outputs)[0] : "";
    const folder = firstOutput ? parentFolder(firstOutput) : outputPath;
    if (folder) {
      await invoke("open_output_folder", { path: folder });
    }
  };

  $: generatedFormats = exportResult
    ? Object.keys(exportResult.outputs).filter((format) => format !== "png")
    : [];
  $: generatedFormatsText = joinLabels(generatedFormats.map(labelForFormat));
  $: hasDiagramPng = Boolean(exportResult?.outputs.png);
  $: generatedMessage = `${generatedFormats.length > 1 ? "Foram salvos" : "Foi salvo"} ${
    generatedFormatsText || "o formato selecionado"
  }${hasDiagramPng ? " + PNG do diagrama de relacionamentos" : ""} na pasta Doc_BI.`;
</script>

<main class="app-shell">
  <section class="workspace">
    <header class="topbar">
      <div>
        <p class="eyebrow">BI Doc Maker</p>
        <h1>Documentacao PBIP</h1>
      </div>
      <button
        class="theme-toggle"
        type="button"
        aria-label={theme === "dark" ? "Ativar modo claro" : "Ativar modo escuro"}
        on:click={toggleTheme}
      >
        {theme === "dark" ? "Modo claro" : "Modo escuro"}
      </button>
    </header>

    <section class="panel">
      <div class="field-grid">
        <label>
          <span>Projeto</span>
          <div class="path-row">
            <input readonly value={selectedPath || "Nenhum projeto selecionado"} />
            <button type="button" on:click={pickProjectFolder}>Selecionar</button>
          </div>
        </label>

        <label>
          <span>Saida</span>
          <div class="path-row">
            <input readonly value={outputPath || "Nenhuma pasta selecionada"} />
            <button type="button" on:click={pickOutputFolder}>Alterar</button>
          </div>
        </label>
      </div>

      <div class="toolbar">
        <div class="formats" aria-label="Formatos de exportacao">
          {#each outputFormats as format}
            <label class="check">
              <input
                type="checkbox"
                bind:checked={selectedFormats[format]}
              />
              <span>{formatLabels[format]}</span>
            </label>
          {/each}
        </div>

        <button class="primary" type="button" disabled={!canExport} on:click={exportDocumentation}>
          {isExporting ? "Gerando..." : "Gerar documentacao"}
        </button>
      </div>
    </section>

    {#if isExporting}
      <section class="notice loading" aria-live="polite">
        <span class="spinner" aria-hidden="true"></span>
        <div>
          <strong>Gerando documentacao</strong>
          <span>Se HTML / Salvar PDF estiver marcado, o navegador sera aberto ao final.</span>
        </div>
      </section>
    {/if}

    {#if errorMessage}
      <section class="notice error">
        <strong>Erro</strong>
        <span>{errorMessage}</span>
      </section>
    {/if}

    {#if exportResult && Object.keys(exportResult.outputs).length > 0}
      <section class="panel outputs">
        <div>
          <h2>Documentacao salva</h2>
          <p class="output-summary">{generatedMessage}</p>
          <ul>
            {#each Object.entries(exportResult.outputs) as [format, path]}
              <li><strong>{labelForFormat(format)}:</strong> {path}</li>
            {/each}
          </ul>
        </div>
        <button type="button" on:click={openOutputFolder}>Abrir pasta</button>
      </section>
    {/if}
  </section>
</main>
