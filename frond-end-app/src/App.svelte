<script lang="ts">
  import { onMount } from "svelte";
  import { open as openDialog } from "@tauri-apps/api/dialog";
  import { invoke } from "@tauri-apps/api/tauri";
  import { getVersion } from "@tauri-apps/api/app";
  import { z } from "zod";
  import { t, locale, localeForCore, setLocale, translate, type Locale } from "./i18n";

  type OutputFormat = "md" | "docx" | "html";
  type ThemeMode = "light" | "dark";

  type BrandingOptions = {
    documentTitle: string;
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

  const PbipEntrySchema = z.object({
    name: z.string(),
    path: z.string(),
    // "pbip" = pronto para documentar; "pbix" = precisa converter no Desktop.
    kind: z.enum(["pbip", "pbix"]).default("pbip")
  });
  const PbipEntryArraySchema = z.array(PbipEntrySchema);

  type PbipEntry = z.infer<typeof PbipEntrySchema>;
  type ProjectStatus = "idle" | "running" | "ok" | "error";

  const UpdateInfoSchema = z.object({
    has_update: z.boolean(),
    current_version: z.string(),
    latest_version: z.string(),
    release_name: z.string(),
    release_url: z.string(),
    release_notes: z.string(),
    published_at: z.string()
  });
  type UpdateInfo = z.infer<typeof UpdateInfoSchema>;

  const outputFormats: OutputFormat[] = ["md", "docx", "html"];
  // Labels reativas via $t("format.{key}") direto no template.

  const defaultFormats: Record<OutputFormat, boolean> = {
    md: true,
    docx: true,
    html: true
  };

  const defaultBranding: BrandingOptions = {
    // Vazio = sidecar Python escolhe o titulo padrao conforme idioma (Fase 2).
    // O placeholder do input mostra o titulo localizado como hint visual.
    documentTitle: "",
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
  let outputPath = "";
  let searchQuery = "";
  let projects: PbipEntry[] = [];
  let selections: Record<string, boolean> = {};
  let projectStatus: Record<string, ProjectStatus> = {};
  let projectErrors: Record<string, string> = {};
  let projectOutputs: Record<string, Record<string, string>> = {};
  let isScanning = false;
  let scanCompleted = false;
  let currentProjectName = "";
  let batchSummary: { ok: number; error: number; total: number } | null = null;
  let errorMessage = "";
  let isExporting = false;
  let showOptions = false;
  let theme: ThemeMode = "light";
  let selectedFormats: Record<OutputFormat, boolean> = { ...defaultFormats };
  let branding: BrandingOptions = { ...defaultBranding };
  let updateInfo: UpdateInfo | null = null;

  $: activeFormats = outputFormats.filter((format) => selectedFormats[format]);
  // PBIP projects sao os documentaveis; PBIX entram em uma lista separada
  // com instrucao de conversao manual no Power BI Desktop (alternativa D).
  $: pbipProjects = projects.filter((p) => p.kind === "pbip");
  $: pbixFiles = projects.filter((p) => p.kind === "pbix");
  $: selectedProjectsList = pbipProjects.filter((p) => selections[p.path]);
  $: hasProjects = pbipProjects.length > 0;
  $: hasPbixFiles = pbixFiles.length > 0;
  $: hasSelectedProjects = selectedProjectsList.length > 0;
  $: canExport = hasSelectedProjects && activeFormats.length > 0 && !isExporting && !isScanning;
  $: outputPathLabel =
    outputPath ||
    (selectedProjectsList.length > 1 && selectedPath
      ? $t("modal.output_batch_suffix", { path: selectedPath })
      : $t("modal.output_default"));
  $: anyOutputs = Object.values(projectOutputs).some(
    (o) => Object.keys(o).length > 0
  );
  $: normalizedQuery = searchQuery.trim().toLowerCase();
  $: filteredProjects = normalizedQuery
    ? pbipProjects.filter(
        (p) =>
          p.name.toLowerCase().includes(normalizedQuery) ||
          p.path.toLowerCase().includes(normalizedQuery)
      )
    : pbipProjects;
  $: hasActiveFilter = normalizedQuery.length > 0;

  const applyTheme = (mode: ThemeMode) => {
    theme = mode;
    document.documentElement.dataset.theme = mode;
    localStorage.setItem("bi-doc-maker-theme", mode);
  };

  const persistPreferences = () => {
    localStorage.setItem("bi-doc-maker-formats", JSON.stringify(selectedFormats));
    localStorage.setItem("bi-doc-maker-branding", JSON.stringify(branding));
    localStorage.setItem("bi-doc-maker-output", outputPath);
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
        // Migration: titles iguais aos defaults conhecidos (v0.7.x/v0.8.x) viram ""
        // para deixar o sidecar usar o titulo localizado conforme idioma ativo.
        const KNOWN_DEFAULTS = new Set([
          "",
          "Documentação Power BI",
          "Power BI Documentation",
        ]);
        const rawTitle = parsed.documentTitle ?? "";
        const docTitle = KNOWN_DEFAULTS.has(rawTitle.trim()) ? "" : rawTitle;
        branding = {
          documentTitle: docTitle,
          logoPath: parsed.logoPath ?? "",
          primaryColor: parsed.primaryColor ?? defaultBranding.primaryColor,
          secondaryColor: parsed.secondaryColor ?? defaultBranding.secondaryColor,
          lightColor: parsed.lightColor ?? defaultBranding.lightColor
        };
      } catch {
        branding = { ...defaultBranding };
      }
    }

    const storedOutput = localStorage.getItem("bi-doc-maker-output");
    if (storedOutput) {
      outputPath = storedOutput;
    }
  };

  const checkForUpdates = async () => {
    try {
      const currentVersion = await getVersion();
      const raw = await invoke("check_for_updates", { currentVersion });
      const parsed = UpdateInfoSchema.parse(raw);
      if (!parsed.has_update) return;

      const dismissed = localStorage.getItem("bi-doc-maker-dismissed-update");
      if (dismissed === parsed.latest_version) return;

      updateInfo = parsed;
    } catch {
      // Silenciosamente ignora falhas (offline, GitHub fora do ar, rate limit).
    }
  };

  const dismissUpdate = () => {
    if (updateInfo) {
      localStorage.setItem("bi-doc-maker-dismissed-update", updateInfo.latest_version);
      updateInfo = null;
    }
  };

  const openUpdateRelease = async () => {
    if (!updateInfo) return;
    try {
      await invoke("open_external_url", { url: updateInfo.release_url });
    } catch (error) {
      errorMessage = translate("err.open_release", { detail: String(error) });
    }
  };

  onMount(() => {
    loadPreferences();

    const storedTheme = localStorage.getItem("bi-doc-maker-theme");
    if (storedTheme === "light" || storedTheme === "dark") {
      applyTheme(storedTheme);
    }
    else {
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
      applyTheme(systemTheme);
    }

    // Verifica atualizacoes em background (nao bloqueia UI).
    checkForUpdates();
  });

  const toggleTheme = () => {
    applyTheme(theme === "dark" ? "light" : "dark");
  };

  const openExternal = async (url: string) => {
    try {
      await invoke("open_external_url", { url });
    } catch (error) {
      errorMessage = translate("err.open_link", { detail: String(error) });
    }
  };

  const resetScanState = () => {
    projects = [];
    selections = {};
    projectStatus = {};
    projectErrors = {};
    projectOutputs = {};
    scanCompleted = false;
    batchSummary = null;
    errorMessage = "";
    searchQuery = "";
  };

  const scanFolder = async (root: string) => {
    isScanning = true;
    resetScanState();
    try {
      const result = await invoke("scan_pbip_projects", { root });
      const parsed = PbipEntryArraySchema.parse(result);
      projects = parsed;
      // Apenas PBIPs sao selecionaveis para export; PBIX viram aviso informativo.
      const pbipOnly = parsed.filter((p) => p.kind === "pbip");
      selections = Object.fromEntries(pbipOnly.map((p) => [p.path, true]));
      projectStatus = Object.fromEntries(pbipOnly.map((p) => [p.path, "idle" as ProjectStatus]));
      scanCompleted = true;
      // So mostra erro "nenhum projeto" se NAO encontrou nem PBIP nem PBIX
      // (se tem PBIX, o usuario ve o bloco com instrucao de conversao).
      if (parsed.length === 0) {
        errorMessage = translate("err.no_projects");
      }
    } catch (error) {
      errorMessage = translate("err.scan_failed", { detail: String(error) });
    } finally {
      isScanning = false;
    }
  };

  const pickProjectFolder = async () => {
    const result = await openDialog({ directory: true, multiple: false });
    if (typeof result === "string") {
      selectedPath = result;
      await scanFolder(result);
    }
  };

  const rescanFolder = async () => {
    if (selectedPath) {
      await scanFolder(selectedPath);
    }
  };

  const toggleProject = (path: string) => {
    selections = { ...selections, [path]: !selections[path] };
  };

  const selectAllProjects = () => {
    const next = { ...selections };
    for (const p of filteredProjects) next[p.path] = true;
    selections = next;
  };

  const clearSelection = () => {
    const next = { ...selections };
    for (const p of filteredProjects) next[p.path] = false;
    selections = next;
  };

  const clearSearch = () => {
    searchQuery = "";
  };

  const handleKeydown = (event: KeyboardEvent) => {
    if (event.key === "Escape" && showOptions) {
      showOptions = false;
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

  const pickOutputFolder = async () => {
    const result = await openDialog({ directory: true, multiple: false });
    if (typeof result === "string") {
      outputPath = result;
      persistPreferences();
    }
  };

  const resetOutputFolder = () => {
    outputPath = "";
    persistPreferences();
  };

  const restoreDefaults = () => {
    selectedFormats = { ...defaultFormats };
    branding = { ...defaultBranding };
    outputPath = "";
    persistPreferences();
  };

  const formatError = (err: string) => {
    if (err.includes("O core Python nao retornou resposta") || err.includes("timed out")) {
      return translate("err.processing_timeout");
    }
    return String(err);
  };

  const exportDocumentation = async () => {
    if (selectedProjectsList.length === 0 || activeFormats.length === 0) {
      errorMessage = translate("err.select_project_format");
      return;
    }

    isExporting = true;
    errorMessage = "";
    batchSummary = null;
    projectErrors = {};
    projectOutputs = {};
    projectStatus = Object.fromEntries(
      projects.map((p) => [p.path, selections[p.path] ? "idle" : "idle"])
    );

    let okCount = 0;
    let errorCount = 0;
    let firstHtmlOutput = "";

    const isBatch = selectedProjectsList.length > 1;
    const sharedOutputDir = outputPath || (isBatch ? selectedPath : "");

    for (const project of selectedProjectsList) {
      currentProjectName = project.name;
      projectStatus = { ...projectStatus, [project.path]: "running" };

      try {
        const result: unknown = await invoke("export_project", {
          path: project.path,
          outputDir: sharedOutputDir || project.path,
          formats: activeFormats,
          branding,
          language: $localeForCore,
        });

        const parsedResult = CoreResultSchema.parse(result);
        if (!parsedResult.ok) {
          throw new Error(parsedResult.error ?? translate("err.generation_failed"));
        }

        projectStatus = { ...projectStatus, [project.path]: "ok" };
        projectOutputs = { ...projectOutputs, [project.path]: parsedResult.outputs };
        okCount += 1;
        if (!firstHtmlOutput && parsedResult.outputs.html) {
          firstHtmlOutput = parsedResult.outputs.html;
        }
      } catch (error) {
        projectStatus = { ...projectStatus, [project.path]: "error" };
        projectErrors = { ...projectErrors, [project.path]: formatError(String(error)) };
        errorCount += 1;
      }
    }

    currentProjectName = "";
    batchSummary = { ok: okCount, error: errorCount, total: selectedProjectsList.length };
    isExporting = false;

    if (selectedProjectsList.length === 1 && firstHtmlOutput) {
      try {
        await invoke("open_output_file", { path: firstHtmlOutput });
      } catch (error) {
        errorMessage = translate("err.open_html", { detail: String(error) });
      }
    }
  };

  const parentFolder = (path: string): string =>
    path.replace(/[\\/][^\\/]+$/, "");

  const cleanPath = (path: string): string =>
    path.replace(/^\\\\\?\\/, "");

  const relativeProjectPath = (projectPath: string): string => {
    const clean = cleanPath(projectPath);
    const root = cleanPath(selectedPath);
    if (!root) return clean;
    const lowerClean = clean.toLowerCase();
    const lowerRoot = root.toLowerCase();
    if (lowerClean === lowerRoot) return ".";
    const prefix = lowerRoot.endsWith("\\") ? lowerRoot : lowerRoot + "\\";
    if (lowerClean.startsWith(prefix)) {
      return clean.substring(prefix.length);
    }
    return clean;
  };

  const openOutputFolder = async () => {
    const allOutputs = Object.values(projectOutputs).flatMap((o) => Object.values(o));
    if (allOutputs.length > 0) {
      const folder = parentFolder(allOutputs[0]);
      if (folder) {
        await invoke("open_output_folder", { path: folder });
        return;
      }
    }
    const fallback = outputPath ? `${outputPath}\\Doc_BI` : selectedPath;
    if (fallback) {
      await invoke("open_output_folder", { path: fallback });
    }
  };

  const openProjectOutput = async (path: string) => {
    const outputs = projectOutputs[path];
    if (!outputs) return;
    const first = Object.values(outputs)[0];
    if (first) {
      const folder = parentFolder(first);
      if (folder) {
        await invoke("open_output_folder", { path: folder });
      }
    }
  };
</script>

<svelte:window on:keydown={handleKeydown} />

<main class="app-shell">
  <section class="workspace">
    <header class="topbar">
      <div class="brand" aria-label={$t("brand.aria_label")}>
        <span class="brand-logo" aria-hidden="true">
          <svg viewBox="0 0 64 64" fill="currentColor">
            <rect x="11" y="36" width="10" height="16" rx="2"/>
            <rect x="27" y="26" width="10" height="26" rx="2"/>
            <rect x="43" y="14" width="10" height="38" rx="2"/>
          </svg>
        </span>
        <strong>BI Doc Maker</strong>
      </div>

      <nav class="top-actions" aria-label={$t("topbar.nav_aria")}>
        <div class="lang-switcher" role="group" aria-label={$t("topbar.lang_aria")}>
          <button
            type="button"
            class="lang-flag"
            class:active={$locale === "pt-BR"}
            title={$t("topbar.lang_pt_title")}
            aria-label={$t("topbar.lang_pt_title")}
            aria-pressed={$locale === "pt-BR"}
            on:click={() => setLocale("pt-BR")}
          >
            <svg viewBox="0 0 14 10" aria-hidden="true">
              <rect width="14" height="10" fill="#009c3b"/>
              <polygon points="7,1 13,5 7,9 1,5" fill="#ffdf00"/>
              <circle cx="7" cy="5" r="2" fill="#002776"/>
            </svg>
          </button>
          <button
            type="button"
            class="lang-flag"
            class:active={$locale === "en-US"}
            title={$t("topbar.lang_en_title")}
            aria-label={$t("topbar.lang_en_title")}
            aria-pressed={$locale === "en-US"}
            on:click={() => setLocale("en-US")}
          >
            <svg viewBox="0 0 19 10" aria-hidden="true">
              <rect width="19" height="10" fill="#bf0a30"/>
              <rect y="1.43" width="19" height="1.43" fill="#fff"/>
              <rect y="4.28" width="19" height="1.43" fill="#fff"/>
              <rect y="7.14" width="19" height="1.43" fill="#fff"/>
              <rect width="8" height="5.71" fill="#002868"/>
            </svg>
          </button>
        </div>
        <button class="icon-button" type="button" title={$t("topbar.linkedin_title")} aria-label={$t("topbar.linkedin_aria")} on:click={() => openExternal(links.linkedin)}>
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.94 8.98H3.53V20h3.41V8.98ZM5.24 4a1.98 1.98 0 1 0 0 3.96 1.98 1.98 0 0 0 0-3.96ZM20.47 13.68c0-3.2-1.7-4.96-4.18-4.96-1.9 0-2.75 1.04-3.23 1.77V8.98H9.79V20h3.41v-5.46c0-1.44.27-2.84 2.06-2.84 1.76 0 1.79 1.65 1.79 2.93V20h3.42v-6.32Z"/></svg>
        </button>
        <button class="icon-button" type="button" title={$t("topbar.github_title")} aria-label={$t("topbar.github_aria")} on:click={() => openExternal(links.github)}>
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.1.79-.25.79-.56v-2.14c-3.2.69-3.87-1.38-3.87-1.38-.52-1.33-1.28-1.68-1.28-1.68-1.04-.72.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.76 2.7 1.25 3.36.96.1-.75.4-1.25.73-1.54-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.28 1.18-3.09-.12-.29-.51-1.46.11-3.04 0 0 .97-.31 3.17 1.18a10.95 10.95 0 0 1 5.76 0c2.2-1.49 3.16-1.18 3.16-1.18.63 1.58.24 2.75.12 3.04.74.81 1.18 1.83 1.18 3.09 0 4.42-2.69 5.4-5.25 5.69.41.36.78 1.06.78 2.14v3.15c0 .31.21.67.8.56A11.51 11.51 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5Z"/></svg>
        </button>
        <button class="icon-button" type="button" title={$t("topbar.support_title")} aria-label={$t("topbar.support_aria")} on:click={() => openExternal(links.support)}>
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21.35 10.55 20.03C5.4 15.36 2 12.27 2 8.5 2 5.41 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.08A5.98 5.98 0 0 1 16.5 3C19.58 3 22 5.41 22 8.5c0 3.77-3.4 6.86-8.55 11.54L12 21.35Z"/></svg>
        </button>
        <button class="icon-button" type="button" title={theme === "dark" ? $t("topbar.theme_light_title") : $t("topbar.theme_dark_title")} aria-label={theme === "dark" ? $t("topbar.theme_light_aria") : $t("topbar.theme_dark_aria")} on:click={toggleTheme}>
          {#if theme === "dark"}
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.76 4.84 5.34 3.42 3.92 4.84l1.42 1.42 1.42-1.42ZM1 13h3v-2H1v2Zm10-12v3h2V1h-2Zm9.08 3.84-1.42-1.42-1.42 1.42 1.42 1.42 1.42-1.42ZM17.24 19.16l1.42 1.42 1.42-1.42-1.42-1.42-1.42 1.42ZM20 11v2h3v-2h-3ZM4.92 19.16l1.42 1.42 1.42-1.42-1.42-1.42-1.42 1.42ZM11 20v3h2v-3h-2Zm1-14a6 6 0 1 0 0 12 6 6 0 0 0 0-12Z"/></svg>
          {:else}
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 14.7A8.5 8.5 0 0 1 9.3 3a8.5 8.5 0 1 0 11.7 11.7Z"/></svg>
          {/if}
        </button>
      </nav>
    </header>

    {#if updateInfo}
      <aside class="update-banner" role="status" aria-live="polite">
        <span class="update-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 3v12m0 0 4-4m-4 4-4-4"/>
            <path d="M5 21h14"/>
          </svg>
        </span>
        <div class="update-text">
          <strong>{$t("update.available", { version: updateInfo.latest_version })}</strong>
          <span>{$t("update.current_hint", { current: updateInfo.current_version })}</span>
        </div>
        <div class="update-actions">
          <button type="button" class="update-primary" on:click={openUpdateRelease}>
            {$t("update.see")}
          </button>
          <button type="button" class="update-dismiss" on:click={dismissUpdate} title={$t("update.dismiss_title")} aria-label={$t("update.dismiss_aria")}>
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          </button>
        </div>
      </aside>
    {/if}

    <div class="content">
      {#if !selectedPath}
        <div class="empty-state">
          <button
            class="folder-picker hero"
            type="button"
            on:click={pickProjectFolder}
            aria-label={$t("empty.cta_aria")}
          >
            <span class="folder-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24"><path d="M3 7.5A2.5 2.5 0 0 1 5.5 5h4.5l2 2.5h6.5A2.5 2.5 0 0 1 21 10v7.5A2.5 2.5 0 0 1 18.5 20h-13A2.5 2.5 0 0 1 3 17.5v-10Z"/></svg>
            </span>
            <span class="picker-copy">
              <strong>{$t("empty.cta_title")}</strong>
              <span>{$t("empty.cta_subtitle")}</span>
            </span>
          </button>
        </div>
      {:else}
        <button
          class="path-bar"
          type="button"
          on:click={pickProjectFolder}
          disabled={isExporting || isScanning}
          aria-label={$t("pathbar.change_aria")}
        >
          <span class="path-bar-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24"><path d="M3 7.5A2.5 2.5 0 0 1 5.5 5h4.5l2 2.5h6.5A2.5 2.5 0 0 1 21 10v7.5A2.5 2.5 0 0 1 18.5 20h-13A2.5 2.5 0 0 1 3 17.5v-10Z"/></svg>
          </span>
          <span class="path-bar-info">
            <small>{$t("pathbar.label")}</small>
            <strong title={cleanPath(selectedPath)}>{cleanPath(selectedPath)}</strong>
          </span>
          <span class="path-bar-change" aria-hidden="true">
            <svg viewBox="0 0 24 24"><path d="M12 4v8m0 0 4-4m-4 4-4-4M5 20h14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            {$t("pathbar.change")}
          </span>
        </button>

        {#if isScanning}
          <div class="state-card" aria-live="polite">
            <span class="spinner" aria-hidden="true"></span>
            <div>
              <strong>{$t("scanning.title")}</strong>
              <span>{$t("scanning.subtitle")}</span>
            </div>
          </div>
        {/if}

        {#if scanCompleted && hasProjects}
          <section class="project-panel">
            <header class="project-panel-header">
              <div class="project-count-block">
                <strong>
                  {#if hasActiveFilter}
                    {filteredProjects.length} {$locale === "pt-BR" ? "de" : "of"} {pbipProjects.length}
                  {:else}
                    {pbipProjects.length}
                  {/if}
                  {pbipProjects.length === 1 ? $t("panel.found_one") : $t("panel.found_many")}
                </strong>
                <small>{selectedProjectsList.length} {selectedProjectsList.length === 1 ? $t("panel.checked_one") : $t("panel.checked_many")}</small>
              </div>
              <div class="project-search" role="search">
                <span class="search-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24"><path d="m21 21-4.3-4.3M17 11a6 6 0 1 1-12 0 6 6 0 0 1 12 0Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </span>
                <input
                  type="search"
                  class="search-input"
                  placeholder={$t("panel.search_placeholder")}
                  bind:value={searchQuery}
                  disabled={isExporting}
                  aria-label={$t("panel.search_aria")}
                />
                {#if hasActiveFilter}
                  <button type="button" class="search-clear" on:click={clearSearch} title={$t("panel.search_clear_title")} aria-label={$t("panel.search_clear_aria")}>
                    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>
                  </button>
                {/if}
              </div>
              <div class="project-toolbar">
                {#if pbipProjects.length > 1}
                  <button type="button" on:click={selectAllProjects} disabled={isExporting || filteredProjects.length === 0}>{$t("panel.select_all")}</button>
                  <button type="button" on:click={clearSelection} disabled={isExporting || filteredProjects.length === 0}>{$t("panel.clear_selection")}</button>
                {/if}
                <button type="button" on:click={rescanFolder} disabled={isExporting} title={$t("panel.rescan_title")} aria-label={$t("panel.rescan_aria")}>
                  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12a8 8 0 0 1 14-5.3M20 4v5h-5M20 12a8 8 0 0 1-14 5.3M4 20v-5h5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </button>
              </div>
            </header>
            {#if filteredProjects.length === 0}
              <div class="project-list-empty">
                <strong>{$t("panel.empty_filtered", { query: searchQuery })}</strong>
                <button type="button" on:click={clearSearch}>{$t("panel.empty_filtered_clear")}</button>
              </div>
            {:else}
              <ul class="project-list">
                {#each filteredProjects as project (project.path)}
                  <li class="project-item" data-status={projectStatus[project.path] ?? "idle"}>
                    <label class="project-row">
                      <input
                        type="checkbox"
                        checked={selections[project.path] ?? false}
                        on:change={() => toggleProject(project.path)}
                        disabled={isExporting}
                      />
                      <span class="project-info">
                        <strong>{project.name}</strong>
                        <small title={cleanPath(project.path)}>{relativeProjectPath(project.path)}</small>
                      </span>
                    </label>
                    <span class="project-status" aria-live="polite">
                      {#if projectStatus[project.path] === "running"}
                        <span class="spinner small" aria-label={$t("project.processing_aria")}></span>
                      {:else if projectStatus[project.path] === "ok"}
                        <button class="status-pill status-ok" type="button" on:click={() => openProjectOutput(project.path)} title={$t("project.ok_pill_title")} aria-label={$t("project.ok_pill_aria")}>
                          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12 5 5L20 7" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                        </button>
                      {:else if projectStatus[project.path] === "error"}
                        <span class="status-pill status-error" title={projectErrors[project.path] ?? $t("project.error_pill_title")} aria-label={$t("project.error_pill_aria", { message: projectErrors[project.path] ?? "" })}>
                          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>
                        </span>
                      {/if}
                    </span>
                  </li>
                {/each}
              </ul>
            {/if}
          </section>
        {/if}

        {#if scanCompleted && hasPbixFiles}
          <section class="pbix-notice" aria-labelledby="pbix-notice-title">
            <header class="pbix-notice-header">
              <span class="pbix-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
              </span>
              <div>
                <strong id="pbix-notice-title">
                  {pbixFiles.length === 1
                    ? $t("pbix.title_one", { n: pbixFiles.length })
                    : $t("pbix.title_many", { n: pbixFiles.length })}
                </strong>
                <p>{$t("pbix.subtitle")}</p>
              </div>
            </header>

            <ol class="pbix-steps">
              <li>{$t("pbix.step_1")}</li>
              <li>{$t("pbix.step_2")}</li>
              <li>{$t("pbix.step_3")}</li>
              <li>{$t("pbix.step_4")}</li>
              <li>{$t("pbix.step_5")}</li>
            </ol>

            <ul class="pbix-list">
              {#each pbixFiles as f (f.path)}
                <li>
                  <strong>{f.name}</strong>
                  <small title={cleanPath(f.path)}>{relativeProjectPath(f.path)}</small>
                </li>
              {/each}
            </ul>

            <p class="pbix-footnote">{$t("pbix.requires_desktop")}</p>
          </section>
        {/if}

        {#if scanCompleted && !hasProjects && !hasPbixFiles && !errorMessage && !isScanning}
          <div class="state-card empty-result">
            <strong>{$t("result.empty_title")}</strong>
            <span>{$t("result.empty_subtitle")}</span>
          </div>
        {/if}
      {/if}
    </div>

    {#if errorMessage}
      <section class="notice error" role="alert">
        <span class="notice-icon" aria-hidden="true">
          <svg viewBox="0 0 24 24"><path d="M12 9v4m0 4h.01M10.3 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.7 3.86a2 2 0 0 0-3.4 0Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </span>
        <div>
          <strong>{$t("notice.error_title")}</strong>
          <span>{errorMessage}</span>
        </div>
      </section>
    {/if}

    {#if batchSummary}
      <section class="notice" class:success={batchSummary.error === 0} class:warning={batchSummary.error > 0} role="status">
        <span class="notice-icon" aria-hidden="true">
          {#if batchSummary.error === 0}
            <svg viewBox="0 0 24 24"><path d="m5 12 5 5L20 7" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
          {:else}
            <svg viewBox="0 0 24 24"><path d="M12 9v4m0 4h.01M10.3 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.7 3.86a2 2 0 0 0-3.4 0Z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          {/if}
        </span>
        <div>
          <strong>
            {batchSummary.total === 1
              ? $t("batch.summary_one", { ok: batchSummary.ok, total: batchSummary.total })
              : $t("batch.summary_many", { ok: batchSummary.ok, total: batchSummary.total })}
          </strong>
          <span>
            {#if batchSummary.error > 0}
              {$t("batch.partial_fail", { n: batchSummary.error })}
            {:else}
              {$t("batch.success")}
            {/if}
          </span>
        </div>
        {#if batchSummary.ok > 0}
          <button type="button" class="notice-action" on:click={openOutputFolder}>{$t("batch.open_folder")}</button>
        {/if}
      </section>
    {/if}

    {#if selectedPath && hasProjects && !isScanning}
      <footer class="action-bar">
        <button type="button" class="secondary action-button" on:click={() => (showOptions = true)} disabled={isExporting}>
          <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
            <line x1="4" y1="7" x2="10" y2="7"/>
            <line x1="14" y1="7" x2="20" y2="7"/>
            <circle cx="12" cy="7" r="2"/>
            <line x1="4" y1="17" x2="8" y2="17"/>
            <line x1="12" y1="17" x2="20" y2="17"/>
            <circle cx="10" cy="17" r="2"/>
          </svg>
          <span>{$t("action.more_options")}</span>
        </button>
        <button class="primary action-button" type="button" disabled={!canExport} on:click={exportDocumentation}>
          {#if isExporting}
            <span class="spinner small" aria-hidden="true"></span>
            <span>{$t("action.generating", { project: currentProjectName || $t("action.generating_idle") })}</span>
          {:else}
            <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8l-5-5Z"/>
              <polyline points="14 3 14 8 19 8"/>
              <line x1="12" y1="11" x2="12" y2="17"/>
              <polyline points="9 14 12 17 15 14"/>
            </svg>
            <span>{$t("action.generate", { n: selectedProjectsList.length })}</span>
          {/if}
        </button>
      </footer>
    {/if}
  </section>
</main>

{#if showOptions}
  <div class="modal-backdrop" role="presentation" on:click|self={() => (showOptions = false)}>
    <section class="options-modal" role="dialog" aria-modal="true" aria-labelledby="options-title">
      <header class="modal-header">
        <div class="modal-titles">
          <h2 id="options-title">{$t("modal.title")}</h2>
          <p class="modal-subtitle">{$t("modal.subtitle")}</p>
        </div>
        <button class="icon-button" type="button" title={$t("modal.close_title")} aria-label={$t("modal.close_aria")} on:click={() => (showOptions = false)}>
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        </button>
      </header>

      <section class="option-group">
        <header class="option-group-header">
          <h3>{$t("modal.formats_title")}</h3>
          <small>{$t("modal.formats_subtitle")}</small>
        </header>
        <div class="chip-group" role="group" aria-label={$t("modal.formats_group_aria")}>
          {#each outputFormats as format}
            <button
              type="button"
              class="chip"
              class:active={selectedFormats[format]}
              aria-pressed={selectedFormats[format]}
              on:click={() => { selectedFormats = { ...selectedFormats, [format]: !selectedFormats[format] }; persistPreferences(); }}
            >
              <span class="chip-tick" aria-hidden="true">
                {#if selectedFormats[format]}
                  <svg viewBox="0 0 24 24"><path d="m5 12 5 5L20 7" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                {/if}
              </span>
              <span class="chip-label">{$t(`format.${format}`)}</span>
            </button>
          {/each}
        </div>
      </section>

      <section class="option-group">
        <header class="option-group-header">
          <h3>{$t("modal.output_title")}</h3>
          <small>{$t("modal.output_subtitle")}</small>
        </header>
        <div class="input-row">
          <input class="input-readonly" readonly value={outputPathLabel} title={outputPathLabel} />
          <button type="button" on:click={pickOutputFolder}>{$t("modal.output_pick")}</button>
          <button type="button" on:click={resetOutputFolder} disabled={!outputPath}>{$t("modal.output_default_btn")}</button>
        </div>
      </section>

      <section class="option-group">
        <header class="option-group-header">
          <h3>{$t("modal.title_doc_heading")}</h3>
          <small>{$t("modal.title_doc_subtitle")}</small>
        </header>
        <input
          class="text-input"
          type="text"
          bind:value={branding.documentTitle}
          placeholder={$t("modal.title_doc_placeholder")}
          on:input={persistPreferences}
          aria-label={$t("modal.title_doc_aria")}
        />
      </section>

      <section class="option-group">
        <header class="option-group-header">
          <h3>{$t("modal.logo_heading")}</h3>
          <small>{$t("modal.logo_subtitle")}</small>
        </header>
        <div class="input-row">
          <input class="input-readonly" readonly value={branding.logoPath || $t("modal.logo_empty")} title={branding.logoPath || $t("modal.logo_empty")} />
          <button type="button" on:click={pickLogo}>{$t("modal.logo_pick")}</button>
          <button type="button" on:click={removeLogo} disabled={!branding.logoPath}>{$t("modal.logo_remove")}</button>
        </div>
      </section>

      <section class="option-group">
        <header class="option-group-header">
          <h3>{$t("modal.colors_heading")}</h3>
          <small>{$t("modal.colors_subtitle")}</small>
        </header>
        <div class="color-list">
          <label class="color-row">
            <input type="color" class="color-input" bind:value={branding.primaryColor} on:change={persistPreferences} aria-label={$t("modal.color_primary_aria")} />
            <span class="color-name">{$t("modal.color_primary")}</span>
            <code class="color-hex">{branding.primaryColor.toUpperCase()}</code>
          </label>
          <label class="color-row">
            <input type="color" class="color-input" bind:value={branding.secondaryColor} on:change={persistPreferences} aria-label={$t("modal.color_secondary_aria")} />
            <span class="color-name">{$t("modal.color_secondary")}</span>
            <code class="color-hex">{branding.secondaryColor.toUpperCase()}</code>
          </label>
          <label class="color-row">
            <input type="color" class="color-input" bind:value={branding.lightColor} on:change={persistPreferences} aria-label={$t("modal.color_light_aria")} />
            <span class="color-name">{$t("modal.color_light")}</span>
            <code class="color-hex">{branding.lightColor.toUpperCase()}</code>
          </label>
        </div>
      </section>

      <footer class="modal-footer">
        <button type="button" on:click={restoreDefaults}>{$t("modal.restore_defaults")}</button>
        <button class="primary" type="button" on:click={() => (showOptions = false)}>{$t("modal.finish")}</button>
      </footer>
    </section>
  </div>
{/if}
