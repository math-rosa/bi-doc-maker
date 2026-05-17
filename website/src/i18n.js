// I18n para o site (puro JS, sem framework). Mesma estrategia do app:
// - Catalogo pt-BR + en-US (objetos planos)
// - Persiste em localStorage
// - data-i18n attrs marcam elementos a traduzir
// - data-i18n-html para HTML aceito (uso em texto com <strong>)
// - data-i18n-title / data-i18n-aria-label para atributos
// - data-i18n-meta no <meta name=description>

const MESSAGES = {
  "pt-BR": {
    "meta.title": "BI Doc Maker | Documentação Profissional de Power BI",
    "meta.description": "BI Doc Maker documenta projetos Power BI PBIP com DOCX, Markdown e HTML, processando tudo localmente.",

    "nav.features": "Recursos",
    "nav.how_it_works": "Como Funciona",
    "nav.github": "Ver no GitHub",
    "nav.lang_aria": "Selecionar idioma",

    "hero.badge": "Processamento local e privado",
    "hero.title_main": "Documentação profissional de Power BI.",
    "hero.title_emphasis": "Sem esforço manual.",
    "hero.subtitle": "Transforme horas de documentação manual em um fluxo guiado e repetível. Gere DOCX, Markdown e HTML imprimível com modelagem, DAX, Power Query, relacionamentos e dicionário de termos, sem enviar metadados para a nuvem.",
    "hero.download": "Download para Windows",
    "hero.access_github": "Acessar GitHub",
    "hero.mockup_title": "Documentacao_PBIP.docx",
    "hero.mockup_iframe_title": "Exemplo de documentação em PDF",
    "hero.mockup_fallback": 'Seu navegador não suporta PDF embutido. <a href="documentacao-power-bi-corporate-spend.pdf" target="_blank" rel="noopener noreferrer">Abra o PDF</a>.',

    "features.title": "Por que usar o BI Doc Maker?",
    "features.subtitle": "Diferenciais técnicos projetados para empresas que exigem excelência, rastreabilidade e segurança.",
    "features.local_title": "Local e Privado",
    "features.local_desc": "Não utiliza IA externa nem APIs para analisar o PBIP. Metadados, regras de negócio e modelo semântico permanecem na sua máquina.",
    "features.auto_title": "Documentação Automática",
    "features.auto_desc": "Mapeia tabelas, colunas, relacionamentos, medidas DAX, Power Query, calculation groups, perspectivas, RLS/OLS e parâmetros M — direto dos arquivos TMDL do PBIP.",
    "features.quality_title": "Qualidade Executiva",
    "features.quality_desc": "Gere DOCX com visual premium, Markdown técnico e HTML imprimível. Inclui Mermaid, leitura DAX, regras Power Query e dicionário de dados.",

    "how.title": "Como Funciona",
    "how.subtitle": "Um fluxo simples que respeita a estrutura oficial do Power BI.",
    "how.step1_title": "Salve como PBIP",
    "how.step1_desc": "No Power BI Desktop, salve seu relatório no formato de projeto (.pbip) para expor a estrutura de metadados.",
    "how.step2_title": "Gere a Documentação",
    "how.step2_desc": "Aponte o BI Doc Maker para a pasta do projeto, escolha os formatos e personalize título, logo e cores.",
    "how.step3_title": "Arquivos Prontos",
    "how.step3_desc": "A documentação é salva em Doc_BI. O HTML pode ser aberto no navegador para salvar como PDF.",

    "footer.desc": "A solução local e open-source para profissionais de dados que valorizam tempo, clareza e privacidade.",
    "footer.project_heading": "Projeto",
    "footer.repo": "Repositório GitHub",
    "footer.bug": "Reportar Bug",
    "footer.releases": "Releases",
    "footer.contact_heading": "Contato e Apoio",
    "footer.linkedin": "LinkedIn do Criador",
    "footer.support": "Apoie o Projeto",
    "footer.copyright": "© 2026 BI Doc Maker. Licenciado sob MIT.",

    "modal.title": "Gostou do Projeto?",
    "modal.body": "O <strong>BI Doc Maker</strong> foi criado para facilitar a vida de quem trabalha com Power BI. Se ele te ajudou, considere apoiar o desenvolvimento para que possamos continuar melhorando!",
    "modal.releases": "Ver releases",
    "modal.support": "Quero Apoiar o Projeto",
  },

  "en-US": {
    "meta.title": "BI Doc Maker | Professional Power BI Documentation",
    "meta.description": "BI Doc Maker documents Power BI PBIP projects to DOCX, Markdown and HTML, processing everything locally.",

    "nav.features": "Features",
    "nav.how_it_works": "How It Works",
    "nav.github": "View on GitHub",
    "nav.lang_aria": "Select language",

    "hero.badge": "Local and private processing",
    "hero.title_main": "Professional Power BI documentation.",
    "hero.title_emphasis": "Without manual effort.",
    "hero.subtitle": "Turn hours of manual documentation into a guided, repeatable flow. Generate DOCX, Markdown and printable HTML with modeling, DAX, Power Query, relationships and a term dictionary — without sending metadata to the cloud.",
    "hero.download": "Download for Windows",
    "hero.access_github": "Open GitHub",
    "hero.mockup_title": "Documentation_PBIP.docx",
    "hero.mockup_iframe_title": "PDF documentation sample",
    "hero.mockup_fallback": 'Your browser does not support embedded PDF. <a href="documentacao-power-bi-corporate-spend.pdf" target="_blank" rel="noopener noreferrer">Open the PDF</a>.',

    "features.title": "Why use BI Doc Maker?",
    "features.subtitle": "Technical differentiators built for companies that require excellence, traceability and security.",
    "features.local_title": "Local and Private",
    "features.local_desc": "Does not use external AI nor APIs to analyze the PBIP. Metadata, business rules and the semantic model stay on your machine.",
    "features.auto_title": "Automatic Documentation",
    "features.auto_desc": "Maps tables, columns, relationships, DAX measures, Power Query, calculation groups, perspectives, RLS/OLS and M parameters — straight from the PBIP TMDL files.",
    "features.quality_title": "Executive Quality",
    "features.quality_desc": "Generate premium DOCX, technical Markdown and printable HTML. Includes Mermaid, DAX reading, Power Query rules and a data dictionary.",

    "how.title": "How It Works",
    "how.subtitle": "A simple flow that respects the official Power BI structure.",
    "how.step1_title": "Save as PBIP",
    "how.step1_desc": "In Power BI Desktop, save your report in project (.pbip) format to expose the metadata structure.",
    "how.step2_title": "Generate the Documentation",
    "how.step2_desc": "Point BI Doc Maker to the project folder, pick formats and customize title, logo and colors.",
    "how.step3_title": "Files Ready",
    "how.step3_desc": "Documentation is saved to Doc_BI. The HTML can be opened in the browser and saved as PDF.",

    "footer.desc": "The local, open-source solution for data professionals who value time, clarity and privacy.",
    "footer.project_heading": "Project",
    "footer.repo": "GitHub Repository",
    "footer.bug": "Report a Bug",
    "footer.releases": "Releases",
    "footer.contact_heading": "Contact and Support",
    "footer.linkedin": "Creator's LinkedIn",
    "footer.support": "Support the Project",
    "footer.copyright": "© 2026 BI Doc Maker. Licensed under MIT.",

    "modal.title": "Liked the Project?",
    "modal.body": "<strong>BI Doc Maker</strong> was built to make life easier for anyone working with Power BI. If it helped you, consider supporting development so we can keep improving!",
    "modal.releases": "View releases",
    "modal.support": "I Want to Support the Project",
  },
};

const STORAGE_KEY = "bi-doc-maker-site-lang";

function detectInitialLocale() {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === "pt-BR" || stored === "en-US") return stored;
  const sys = (navigator.language || "").toLowerCase();
  return sys.startsWith("en") ? "en-US" : "pt-BR";
}

function t(key, locale) {
  const catalog = MESSAGES[locale] || MESSAGES["pt-BR"];
  return catalog[key] ?? MESSAGES["pt-BR"][key] ?? `[?${key}]`;
}

function applyLocale(locale) {
  // Atualiza atributos do <html>
  document.documentElement.setAttribute("lang", locale);

  // Texto de elementos com data-i18n
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    el.textContent = t(key, locale);
  });
  // HTML rico (cuidado: so usar com chaves conhecidas, nao input do usuario)
  document.querySelectorAll("[data-i18n-html]").forEach((el) => {
    const key = el.getAttribute("data-i18n-html");
    el.innerHTML = t(key, locale);
  });
  // title atributo
  document.querySelectorAll("[data-i18n-title]").forEach((el) => {
    const key = el.getAttribute("data-i18n-title");
    el.setAttribute("title", t(key, locale));
  });
  // aria-label atributo
  document.querySelectorAll("[data-i18n-aria-label]").forEach((el) => {
    const key = el.getAttribute("data-i18n-aria-label");
    el.setAttribute("aria-label", t(key, locale));
  });
  // <meta name="description">
  document.querySelectorAll("[data-i18n-meta]").forEach((el) => {
    const key = el.getAttribute("data-i18n-meta");
    el.setAttribute("content", t(key, locale));
  });

  // Estado visual dos botoes de bandeira
  document.querySelectorAll(".lang-flag").forEach((btn) => {
    const isActive = btn.getAttribute("data-lang") === locale;
    btn.classList.toggle("active", isActive);
    btn.setAttribute("aria-pressed", isActive ? "true" : "false");
  });
}

export function setupI18n() {
  let current = detectInitialLocale();
  applyLocale(current);

  document.querySelectorAll(".lang-flag").forEach((btn) => {
    btn.addEventListener("click", () => {
      const next = btn.getAttribute("data-lang");
      if (next === current) return;
      current = next;
      localStorage.setItem(STORAGE_KEY, current);
      applyLocale(current);
    });
  });
}
