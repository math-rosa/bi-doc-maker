<script lang="ts">
  import { onMount } from "svelte";
  import { open as openDialog } from "@tauri-apps/api/dialog";
  import { invoke } from "@tauri-apps/api/tauri";

  type OutputFormat = "md" | "docx" | "html";
  type ThemeMode = "light" | "dark";
  type BrandingSettings = {
    documentTitle: string;
    logoPath: string;
    primaryColor: string;
    secondaryColor: string;
    lightColor: string;
  };

  type CoreResult = {
    ok: boolean;
    warnings: string[];
    outputs: Record<string, string>;
    error?: string;
  };

  const formatLabels: Record<string, string> = {
    md: "Markdown",
    docx: "Word",
    html: "HTML / Salvar PDF"
  };
  const outputFormats: OutputFormat[] = ["md", "docx", "html"];
  const brandingStorageKey = "bi-doc-maker-branding";
  const defaultBranding: BrandingSettings = {
    documentTitle: "BI Doc Maker",
    logoPath: "",
    primaryColor: "#003D6B",
    secondaryColor: "#006DAA",
    lightColor: "#D6E8F5"
  };

  let selectedPath = "";
  let outputPath = "";
  let exportResult: CoreResult | null = null;
  let errorMessage = "";
  let isExporting = false;
  let theme: ThemeMode = "light";
  let brandingReady = false;
  let branding: BrandingSettings = { ...defaultBranding };
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

  const normalizeColor = (value: unknown, fallback: string): string => {
    const color = String(value ?? "").trim();
    return /^#[0-9a-fA-F]{6}$/.test(color) ? color.toUpperCase() : fallback;
  };

  const loadBranding = () => {
    const stored = localStorage.getItem(brandingStorageKey);
    if (!stored) {
      brandingReady = true;
      return;
    }

    try {
      const parsed = JSON.parse(stored) as Partial<BrandingSettings>;
      branding = {
        documentTitle: String(parsed.documentTitle ?? defaultBranding.documentTitle),
        logoPath: String(parsed.logoPath ?? ""),
        primaryColor: normalizeColor(parsed.primaryColor, defaultBranding.primaryColor),
        secondaryColor: normalizeColor(parsed.secondaryColor, defaultBranding.secondaryColor),
        lightColor: normalizeColor(parsed.lightColor, defaultBranding.lightColor)
      };
    } catch {
      branding = { ...defaultBranding };
    } finally {
      brandingReady = true;
    }
  };

  const persistBranding = () => {
    if (brandingReady) {
      localStorage.setItem(brandingStorageKey, JSON.stringify(branding));
    }
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
    } else {
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
      applyTheme(systemTheme);
    }

    loadBranding();
  });

  $: persistBranding();

  $: activeFormats = outputFormats.filter((format) => selectedFormats[format]);
  $: canExport =
    Boolean(selectedPath) &&
    Boolean(outputPath) &&
    activeFormats.length > 0 &&
    !isExporting;
  $: selectedFormatText =
    activeFormats.length === 1
      ? "1 formato selecionado"
      : `${activeFormats.length} formatos selecionados`;

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

  const pickLogoFile = async () => {
    const result = await openDialog({
      multiple: false,
      filters: [{ name: "Imagem", extensions: ["png", "jpg", "jpeg"] }]
    });
    if (typeof result === "string") {
      branding = { ...branding, logoPath: result };
      exportResult = null;
      errorMessage = "";
    }
  };

  const clearLogoFile = () => {
    branding = { ...branding, logoPath: "" };
    exportResult = null;
    errorMessage = "";
  };

  const exportBranding = () => ({
    documentTitle: branding.documentTitle.trim() || defaultBranding.documentTitle,
    logoPath: branding.logoPath.trim(),
    primaryColor: normalizeColor(branding.primaryColor, defaultBranding.primaryColor),
    secondaryColor: normalizeColor(branding.secondaryColor, defaultBranding.secondaryColor),
    lightColor: normalizeColor(branding.lightColor, defaultBranding.lightColor)
  });

  const exportDocumentation = async () => {
    const formats = activeFormats;
    if (!selectedPath || !outputPath || formats.length === 0) {
      errorMessage = "Informe o projeto, a pasta de saída e ao menos um formato.";
      return;
    }

    isExporting = true;
    errorMessage = "";
    exportResult = null;

    try {
      const result = await invoke<CoreResult>("export_project", {
        path: selectedPath,
        outputDir: outputPath,
        formats,
        branding: exportBranding()
      });
      if (!result.ok) {
        throw new Error(result.error ?? "Falha ao gerar a documentação.");
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

  $: generatedFormats = exportResult ? Object.keys(exportResult.outputs).map(labelForFormat) : [];
  $: generatedFormatsText = joinLabels(generatedFormats);
  $: generatedMessage = generatedFormatsText
    ? `Documentação salva na pasta Doc_BI (${generatedFormatsText}).`
    : "Documentação salva na pasta Doc_BI.";
</script>

<main class="app-shell" aria-busy={isExporting}>
  <section class="workspace">
    <header class="topbar">
      <div class="brand">
        <div class="brand-mark" aria-hidden="true">
          <span class="bar bar-blue"></span>
          <span class="bar bar-green"></span>
          <span class="bar bar-yellow"></span>
        </div>
        <div>
          <p class="eyebrow">BI Doc Maker</p>
          <h1>Documentação PBIP</h1>
        </div>
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

    <section class="panel control-panel">
      <div class="field-grid">
        <div class="field">
          <label for="project-path">Projeto PBIP</label>
          <div class="path-row">
            <input
              id="project-path"
              readonly
              value={selectedPath || "Nenhum projeto selecionado"}
              title={selectedPath || "Nenhum projeto selecionado"}
            />
            <button type="button" class="secondary-button" on:click={pickProjectFolder} disabled={isExporting}>
              Selecionar
            </button>
          </div>
        </div>

        <div class="field">
          <label for="output-path">Saída</label>
          <div class="path-row">
            <input
              id="output-path"
              readonly
              value={outputPath || "Nenhuma pasta selecionada"}
              title={outputPath || "Nenhuma pasta selecionada"}
            />
            <button type="button" class="secondary-button" on:click={pickOutputFolder} disabled={isExporting}>
              Alterar
            </button>
          </div>
        </div>
      </div>

      <section class="branding-section">
        <div class="section-heading">
          <div>
            <h3>Personalização</h3>
            <p>Defina título, logo e cores usadas nos documentos gerados.</p>
          </div>
        </div>

        <div class="branding-grid">
          <div class="field">
            <label for="document-title">Título do documento</label>
            <input
              id="document-title"
              class="text-input"
              bind:value={branding.documentTitle}
              disabled={isExporting}
              placeholder="BI Doc Maker"
            />
          </div>

          <div class="field">
            <label for="company-logo">Logo da empresa</label>
            <div class="path-row logo-row">
              <input
                id="company-logo"
                readonly
                value={branding.logoPath || "Logo padrão do BI Doc Maker"}
                title={branding.logoPath || "Logo padrão do BI Doc Maker"}
              />
              <button type="button" class="secondary-button" on:click={pickLogoFile} disabled={isExporting}>
                Selecionar
              </button>
              <button
                type="button"
                class="secondary-button compact-button"
                on:click={clearLogoFile}
                disabled={isExporting || !branding.logoPath}
              >
                Remover
              </button>
            </div>
          </div>
        </div>

        <div class="color-grid">
          <label class="color-control">
            <span>Primária</span>
            <input type="color" bind:value={branding.primaryColor} disabled={isExporting} />
            <code>{branding.primaryColor}</code>
          </label>
          <label class="color-control">
            <span>Secundária</span>
            <input type="color" bind:value={branding.secondaryColor} disabled={isExporting} />
            <code>{branding.secondaryColor}</code>
          </label>
          <label class="color-control">
            <span>Fundo claro</span>
            <input type="color" bind:value={branding.lightColor} disabled={isExporting} />
            <code>{branding.lightColor}</code>
          </label>
        </div>
      </section>

      <fieldset class="format-section" disabled={isExporting}>
        <legend>Formatos de saída</legend>
        <div class="format-grid">
          {#each outputFormats as format}
            <label class:selected={selectedFormats[format]} class="format-option">
              <input type="checkbox" bind:checked={selectedFormats[format]} />
              <span>{formatLabels[format]}</span>
            </label>
          {/each}
        </div>
      </fieldset>

      <div class="action-row">
        <div class="action-summary">
          <strong>{selectedFormatText}</strong>
          <span>A documentação será salva em Doc_BI.</span>
        </div>
        <button type="button" class="primary-button" on:click={exportDocumentation} disabled={!canExport}>
          {isExporting ? "Gerando..." : "Gerar documentação"}
        </button>
      </div>
    </section>

    {#if isExporting}
      <section class="notice loading" aria-live="polite">
        <span class="spinner" aria-hidden="true"></span>
        <div>
          <strong>Gerando documentação</strong>
          <span>Se HTML / Salvar PDF estiver marcado, o navegador será aberto ao final.</span>
        </div>
      </section>
    {/if}

    {#if errorMessage}
      <section class="notice error" role="alert">
        <strong>Não foi possível gerar</strong>
        <span>{errorMessage}</span>
      </section>
    {/if}

    {#if exportResult && Object.keys(exportResult.outputs).length}
      <section class="notice success" aria-live="polite">
        <div>
          <strong>Documentação gerada com sucesso</strong>
          <span>{generatedMessage}</span>
        </div>
        <button type="button" class="secondary-button" on:click={openOutputFolder}>Abrir pasta</button>
      </section>
    {/if}
  </section>
</main>
