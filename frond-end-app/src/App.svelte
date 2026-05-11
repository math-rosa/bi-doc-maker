<script lang="ts">
  import { onMount } from "svelte";
  import { open as openDialog } from "@tauri-apps/api/dialog";
  import { invoke } from "@tauri-apps/api/tauri";
  import { z } from "zod";
  import logoUrl from "./assets/bi-doc-maker-logo.png";

  type OutputFormat = "md" | "docx" | "html";
  type ThemeMode = "light" | "dark";

  type BrandingOptions = {
    logoPath: string;
    primaryColor: string;
    secondaryColor: string;
    lightColor: string;
  };

  const CoreResultSchema = z.object({
    ok: z.boolean(),
    warnings: z.array(z.string()).default([]),
    outputs: z.record(z.string()).default({}),
    error: z.string().optional()
  });

  type CoreResult = z.infer<typeof CoreResultSchema>;

  const outputFormats: OutputFormat[] = ["md", "docx", "html"];
  const formatLabels: Record<OutputFormat, string> = {
    md: "Markdown",
    docx: "Word",
    html: "HTML / Salvar PDF"
  };

  const defaultFormats: Record<OutputFormat, boolean> = {
    md: true,
    docx: true,
    html: true
  };

  const defaultBranding: BrandingOptions = {
    logoPath: "",
    primaryColor: "#003D6B",
    secondaryColor: "#006DAA",
    lightColor: "#D6E8F5"
  };

  const links = {
    linkedin: "https://www.linkedin.com/in/mathrosa96/",
    github: "https://github.com/math-rosa/bi-doc-maker",
    support: "https://nubank.com.br/cobrar/5iu9s/69ff8e6c-3a76-4fa3-9a60-d3b2e1e8885c"
  };

  let selectedPath = "";
  let exportResult: CoreResult | null = null;
  let errorMessage = "";
  let isExporting = false;
  let showOptions = false;
  let theme: ThemeMode = "light";
  let selectedFormats: Record<OutputFormat, boolean> = { ...defaultFormats };
  let branding: BrandingOptions = { ...defaultBranding };

  $: activeFormats = outputFormats.filter((format) => selectedFormats[format]);
  $: hasSelectedProject = Boolean(selectedPath);
  $: canExport = hasSelectedProject && activeFormats.length > 0 && !isExporting;
  $: selectedProjectLabel = selectedPath || "Nenhuma pasta PBIP selecionada";

  const applyTheme = (mode: ThemeMode) => {
    theme = mode;
    document.documentElement.dataset.theme = mode;
    localStorage.setItem("bi-doc-maker-theme", mode);
  };

  const persistPreferences = () => {
    localStorage.setItem("bi-doc-maker-formats", JSON.stringify(selectedFormats));
    localStorage.setItem("bi-doc-maker-branding", JSON.stringify(branding));
  };

  const loadPreferences = () => {
    const storedFormats = localStorage.getItem("bi-doc-maker-formats");
    if (storedFormats) {
      try {
        const parsed = JSON.parse(storedFormats) as Partial<Record<OutputFormat, boolean>>;
        selectedFormats = {
          md: parsed.md ?? true,
          docx: parsed.docx ?? true,
          html: parsed.html ?? true
        };
      } catch {
        selectedFormats = { ...defaultFormats };
      }
    }

    const storedBranding = localStorage.getItem("bi-doc-maker-branding");
    if (storedBranding) {
      try {
        const parsed = JSON.parse(storedBranding) as Partial<BrandingOptions>;
        branding = {
          logoPath: parsed.logoPath ?? "",
          primaryColor: parsed.primaryColor ?? defaultBranding.primaryColor,
          secondaryColor: parsed.secondaryColor ?? defaultBranding.secondaryColor,
          lightColor: parsed.lightColor ?? defaultBranding.lightColor
        };
      } catch {
        branding = { ...defaultBranding };
      }
    }
  };

  onMount(() => {
    loadPreferences();

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

  const toggleTheme = () => {
    applyTheme(theme === "dark" ? "light" : "dark");
  };

  const openExternal = async (url: string) => {
    try {
      await invoke("open_external_url", { url });
    } catch (error) {
      errorMessage = `Nao foi possivel abrir o link: ${String(error)}`;
    }
  };

  const pickProjectFolder = async () => {
    const result = await openDialog({ directory: true, multiple: false });
    if (typeof result === "string") {
      selectedPath = result;
      exportResult = null;
      errorMessage = "";
    }
  };

  const pickLogo = async () => {
    const result = await openDialog({
      multiple: false,
      filters: [{ name: "Imagens", extensions: ["png", "jpg", "jpeg"] }]
    });
    if (typeof result === "string") {
      branding = { ...branding, logoPath: result };
      persistPreferences();
    }
  };

  const removeLogo = () => {
    branding = { ...branding, logoPath: "" };
    persistPreferences();
  };

  const restoreDefaults = () => {
    selectedFormats = { ...defaultFormats };
    branding = { ...defaultBranding };
    persistPreferences();
  };

  const formatError = (err: string) => {
    if (err.includes("O core Python nao retornou resposta") || err.includes("timed out")) {
      return "O processamento falhou ou demorou demais para responder.";
    }
    return String(err);
  };

  const exportDocumentation = async () => {
    if (!selectedPath || activeFormats.length === 0) {
      errorMessage = "Selecione a pasta PBIP e ao menos um formato.";
      return;
    }

    isExporting = true;
    errorMessage = "";
    exportResult = null;

    try {
      const result: unknown = await invoke("export_project", {
        path: selectedPath,
        outputDir: selectedPath,
        formats: activeFormats,
        branding
      });

      const parsedResult = CoreResultSchema.parse(result);
      if (!parsedResult.ok) {
        throw new Error(parsedResult.error ?? "Falha ao gerar a documentação.");
      }

      exportResult = parsedResult;
      if (parsedResult.outputs.html) {
        await invoke("open_output_file", { path: parsedResult.outputs.html });
      }
    } catch (error) {
      errorMessage = formatError(String(error));
    } finally {
      isExporting = false;
    }
  };

  const parentFolder = (path: string): string =>
    path.replace(/[\\/][^\\/]+$/, "");

  const openOutputFolder = async () => {
    const firstOutput = exportResult ? Object.values(exportResult.outputs)[0] : "";
    const folder = firstOutput ? parentFolder(firstOutput) : `${selectedPath}\\Doc_BI`;
    if (folder) {
      await invoke("open_output_folder", { path: folder });
    }
  };
</script>

<main class="app-shell">
  <section class="workspace">
    <header class="topbar">
      <div class="brand" aria-label="BI Doc Maker">
        <img class="brand-logo" src={logoUrl} alt="" />
        <strong>BI Doc Maker</strong>
      </div>

      <nav class="top-actions" aria-label="Links e tema">
        <button class="icon-button" type="button" title="LinkedIn" aria-label="Abrir LinkedIn" on:click={() => openExternal(links.linkedin)}>
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.94 8.98H3.53V20h3.41V8.98ZM5.24 4a1.98 1.98 0 1 0 0 3.96 1.98 1.98 0 0 0 0-3.96ZM20.47 13.68c0-3.2-1.7-4.96-4.18-4.96-1.9 0-2.75 1.04-3.23 1.77V8.98H9.79V20h3.41v-5.46c0-1.44.27-2.84 2.06-2.84 1.76 0 1.79 1.65 1.79 2.93V20h3.42v-6.32Z"/></svg>
        </button>
        <button class="icon-button" type="button" title="GitHub" aria-label="Abrir GitHub" on:click={() => openExternal(links.github)}>
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.1.79-.25.79-.56v-2.14c-3.2.69-3.87-1.38-3.87-1.38-.52-1.33-1.28-1.68-1.28-1.68-1.04-.72.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.76 2.7 1.25 3.36.96.1-.75.4-1.25.73-1.54-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.28 1.18-3.09-.12-.29-.51-1.46.11-3.04 0 0 .97-.31 3.17 1.18a10.95 10.95 0 0 1 5.76 0c2.2-1.49 3.16-1.18 3.16-1.18.63 1.58.24 2.75.12 3.04.74.81 1.18 1.83 1.18 3.09 0 4.42-2.69 5.4-5.25 5.69.41.36.78 1.06.78 2.14v3.15c0 .31.21.67.8.56A11.51 11.51 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5Z"/></svg>
        </button>
        <button class="icon-button" type="button" title="Apoiar o projeto" aria-label="Apoiar o projeto" on:click={() => openExternal(links.support)}>
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21.35 10.55 20.03C5.4 15.36 2 12.27 2 8.5 2 5.41 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.08A5.98 5.98 0 0 1 16.5 3C19.58 3 22 5.41 22 8.5c0 3.77-3.4 6.86-8.55 11.54L12 21.35Z"/></svg>
        </button>
        <button class="icon-button" type="button" title={theme === "dark" ? "Modo claro" : "Modo escuro"} aria-label={theme === "dark" ? "Ativar modo claro" : "Ativar modo escuro"} on:click={toggleTheme}>
          {#if theme === "dark"}
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.76 4.84 5.34 3.42 3.92 4.84l1.42 1.42 1.42-1.42ZM1 13h3v-2H1v2Zm10-12v3h2V1h-2Zm9.08 3.84-1.42-1.42-1.42 1.42 1.42 1.42 1.42-1.42ZM17.24 19.16l1.42 1.42 1.42-1.42-1.42-1.42-1.42 1.42ZM20 11v2h3v-2h-3ZM4.92 19.16l1.42 1.42 1.42-1.42-1.42-1.42-1.42 1.42ZM11 20v3h2v-3h-2Zm1-14a6 6 0 1 0 0 12 6 6 0 0 0 0-12Z"/></svg>
          {:else}
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 14.7A8.5 8.5 0 0 1 9.3 3a8.5 8.5 0 1 0 11.7 11.7Z"/></svg>
          {/if}
        </button>
      </nav>
    </header>

    <section class="hero-panel">
      <button class="folder-picker" type="button" on:click={pickProjectFolder} aria-label="Selecionar pasta do arquivo PBIP">
        <span class="folder-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24"><path d="M3.75 7.25A2.25 2.25 0 0 1 6 5h4.15l2 2.5H18A2.25 2.25 0 0 1 20.25 9.75v7A2.25 2.25 0 0 1 18 19H6a2.25 2.25 0 0 1-2.25-2.25v-9.5Z"/></svg>
        </span>
        <span class="picker-copy">
          <strong>Selecione a pasta do arquivo PBIP</strong>
          <span title={selectedProjectLabel}>{selectedProjectLabel}</span>
        </span>
      </button>

      {#if hasSelectedProject}
        <div class="main-actions">
          <button class="primary action-button" type="button" disabled={!canExport} on:click={exportDocumentation}>
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v11m0 0 4-4m-4 4-4-4M5 19h14" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            <span>{isExporting ? "Gerando documentação..." : "Gerar Documentação"}</span>
          </button>
          <button type="button" class="secondary action-button" on:click={() => (showOptions = true)}>
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M7 12h10M10 17h4" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>
            <span>Mais Opções</span>
          </button>
        </div>
      {/if}
    </section>

    {#if isExporting}
      <section class="notice loading" aria-live="polite">
        <span class="spinner" aria-hidden="true"></span>
        <div>
          <strong>Gerando documentação</strong>
          <span>O HTML será aberto para visualização ao final quando esse formato estiver marcado.</span>
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
      <section class="notice success">
        <div>
          <strong>Documentação salva</strong>
          <span>Documentação salva na pasta Doc_BI.</span>
        </div>
        <button type="button" on:click={openOutputFolder}>Abrir pasta</button>
      </section>
    {/if}
  </section>
</main>

{#if showOptions}
  <div class="modal-backdrop" role="presentation" on:click|self={() => (showOptions = false)}>
    <section class="options-modal" role="dialog" aria-modal="true" aria-labelledby="options-title">
      <header class="modal-header">
        <div>
          <p class="eyebrow">Configurações</p>
          <h2 id="options-title">Mais Opções</h2>
        </div>
        <button class="icon-button" type="button" title="Fechar" aria-label="Fechar opções" on:click={() => (showOptions = false)}>
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>
        </button>
      </header>

      <div class="option-group">
        <h3>Formatos</h3>
        <div class="format-grid">
          {#each outputFormats as format}
            <label class="check">
              <input type="checkbox" bind:checked={selectedFormats[format]} on:change={persistPreferences} />
              <span>{formatLabels[format]}</span>
            </label>
          {/each}
        </div>
      </div>

      <div class="option-group">
        <h3>Logo da empresa</h3>
        <div class="logo-row">
          <input readonly value={branding.logoPath || "Nenhum logo selecionado"} title={branding.logoPath || "Nenhum logo selecionado"} />
          <button type="button" on:click={pickLogo}>Selecionar</button>
          <button type="button" on:click={removeLogo} disabled={!branding.logoPath}>Remover</button>
        </div>
      </div>

      <div class="option-group">
        <h3>Cores da documentação</h3>
        <div class="color-grid">
          <label class="color-control">
            <span>Primária</span>
            <input type="color" bind:value={branding.primaryColor} on:change={persistPreferences} />
            <code>{branding.primaryColor}</code>
          </label>
          <label class="color-control">
            <span>Secundária</span>
            <input type="color" bind:value={branding.secondaryColor} on:change={persistPreferences} />
            <code>{branding.secondaryColor}</code>
          </label>
          <label class="color-control">
            <span>Fundo claro</span>
            <input type="color" bind:value={branding.lightColor} on:change={persistPreferences} />
            <code>{branding.lightColor}</code>
          </label>
        </div>
      </div>

      <footer class="modal-footer">
        <button type="button" on:click={restoreDefaults}>Restaurar padrões</button>
        <button class="primary" type="button" on:click={() => (showOptions = false)}>Concluir</button>
      </footer>
    </section>
  </div>
{/if}
