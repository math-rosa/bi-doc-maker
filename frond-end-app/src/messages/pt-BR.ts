// Catalogo pt-BR (idioma de referencia). Use placeholders {nome} quando precisar
// interpolar valores. O Svelte store em i18n.ts faz substituicao via String.replaceAll.

export const messages: Record<string, string> = {
  // ----- Topbar / brand -----
  "brand.aria_label": "BI Doc Maker",
  "topbar.nav_aria": "Links e tema",
  "topbar.linkedin_title": "LinkedIn",
  "topbar.linkedin_aria": "Abrir LinkedIn",
  "topbar.github_title": "GitHub",
  "topbar.github_aria": "Abrir GitHub",
  "topbar.support_title": "Apoiar o projeto",
  "topbar.support_aria": "Apoiar o projeto",
  "topbar.theme_light_title": "Modo claro",
  "topbar.theme_dark_title": "Modo escuro",
  "topbar.theme_light_aria": "Ativar modo claro",
  "topbar.theme_dark_aria": "Ativar modo escuro",
  "topbar.lang_aria": "Selecionar idioma",
  "topbar.lang_pt_title": "Português (Brasil)",
  "topbar.lang_en_title": "English (US)",

  // ----- Update banner -----
  "update.available": "Atualização disponível: v{version}",
  "update.current_hint": "Você está na v{current}. Veja as novidades e baixe na página da release.",
  "update.see": "Ver atualização",
  "update.dismiss_title": "Ignorar esta versão",
  "update.dismiss_aria": "Ignorar esta atualização",

  // ----- Empty state (selecionar pasta) -----
  "empty.cta_aria": "Selecionar pasta com projetos PBIP",
  "empty.cta_title": "Selecione a pasta com seus projetos PBIP",
  "empty.cta_subtitle": "Vamos varrer as subpastas e listar os projetos encontrados.",

  // ----- Path bar -----
  "pathbar.label": "Pasta selecionada",
  "pathbar.change": "Trocar",
  "pathbar.change_aria": "Trocar pasta selecionada",

  // ----- Scanning state -----
  "scanning.title": "Procurando projetos...",
  "scanning.subtitle": "Vasculhando subpastas em busca de arquivos .pbip.",

  // ----- Project panel -----
  "panel.found_one": "projeto encontrado",
  "panel.found_many": "projetos encontrados",
  "panel.checked_one": "marcado",
  "panel.checked_many": "marcados",
  "panel.search_placeholder": "Filtrar por nome ou caminho...",
  "panel.search_aria": "Filtrar lista de projetos",
  "panel.search_clear_title": "Limpar filtro",
  "panel.search_clear_aria": "Limpar filtro",
  "panel.select_all": "Marcar todos",
  "panel.clear_selection": "Limpar",
  "panel.rescan_title": "Refazer varredura",
  "panel.rescan_aria": "Re-escanear pasta",
  "panel.empty_filtered": 'Nenhum projeto bate com "{query}"',
  "panel.empty_filtered_clear": "Limpar filtro",

  // ----- Project row status badges -----
  "project.processing_aria": "Processando",
  "project.ok_pill_title": "Abrir pasta deste projeto",
  "project.ok_pill_aria": "Sucesso, abrir pasta",
  "project.error_pill_title": "Erro",
  "project.error_pill_aria": "Erro: {message}",

  // ----- Empty result (varredura completa mas zero) -----
  "result.empty_title": "Nenhum projeto PBIP encontrado",
  "result.empty_subtitle": "Verifique se a pasta selecionada contém arquivos .pbip ou subpastas com modelos Power BI.",

  // ----- Error notice -----
  "notice.error_title": "Erro",

  // ----- Batch summary -----
  "batch.summary_one": "{ok}/{total} documentação gerada",
  "batch.summary_many": "{ok}/{total} documentações geradas",
  "batch.success": "Tudo certo! Documentação salva.",
  "batch.partial_fail": "{n} falharam. Veja os detalhes em cada projeto na lista.",
  "batch.open_folder": "Abrir pasta",

  // ----- Action bar -----
  "action.more_options": "Mais Opções",
  "action.generating": "Gerando {project}",
  "action.generating_idle": "...",
  "action.generate": "Gerar Documentação ({n})",

  // ----- Options modal -----
  "modal.title": "Mais Opções",
  "modal.subtitle": "Personalize a documentação que será gerada.",
  "modal.close_title": "Fechar",
  "modal.close_aria": "Fechar opções",

  "modal.formats_title": "Formatos de exportação",
  "modal.formats_subtitle": "Selecione um ou mais formatos.",
  "modal.formats_group_aria": "Formatos de exportação",
  "format.md": "Markdown",
  "format.docx": "Word",
  "format.html": "HTML / Salvar PDF",

  "modal.output_title": "Pasta de saída",
  "modal.output_subtitle": "No modo lote, todos os projetos compartilham essa pasta.",
  "modal.output_default": "Pasta do projeto",
  "modal.output_batch_suffix": "{path} (lote → pasta selecionada)",
  "modal.output_pick": "Selecionar",
  "modal.output_default_btn": "Padrão",

  "modal.title_doc_heading": "Título da documentação",
  "modal.title_doc_subtitle": "Aparece na capa de cada documento.",
  "modal.title_doc_placeholder": "Documentação Power BI",
  "modal.title_doc_aria": "Título exibido no documento",

  "modal.logo_heading": "Logo da empresa",
  "modal.logo_subtitle": "PNG ou JPG, exibido na capa.",
  "modal.logo_empty": "Nenhum logo selecionado",
  "modal.logo_pick": "Selecionar",
  "modal.logo_remove": "Remover",

  "modal.colors_heading": "Cores da documentação",
  "modal.colors_subtitle": "Definem o esquema visual aplicado.",
  "modal.color_primary": "Primária",
  "modal.color_secondary": "Secundária",
  "modal.color_light": "Fundo claro",
  "modal.color_primary_aria": "Cor primária",
  "modal.color_secondary_aria": "Cor secundária",
  "modal.color_light_aria": "Cor de fundo claro",

  "modal.restore_defaults": "Restaurar padrões",
  "modal.finish": "Concluir",

  // ----- Error messages (formatError + try/catch fallbacks) -----
  "err.processing_timeout": "O processamento falhou ou demorou demais para responder.",
  "err.scan_failed": "Falha ao escanear a pasta: {detail}",
  "err.no_projects": "Nenhum projeto Power BI (.pbip) encontrado nessa pasta.",
  "err.select_project_format": "Selecione ao menos um projeto e um formato.",
  "err.generation_failed": "Falha ao gerar a documentação.",
  "err.open_link": "Não foi possível abrir o link: {detail}",
  "err.open_release": "Não foi possível abrir a release: {detail}",
  "err.open_html": "Documentação gerada, mas falhou ao abrir o HTML: {detail}",

  // ----- Branding defaults -----
  "branding.default_title": "Documentação Power BI",
};
