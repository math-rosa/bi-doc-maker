// English (US) catalog. Mirrors pt-BR keys exactly. Use {placeholder} for interpolation.

export const messages: Record<string, string> = {
  // ----- Topbar / brand -----
  "brand.aria_label": "BI Doc Maker",
  "topbar.nav_aria": "Links and theme",
  "topbar.linkedin_title": "LinkedIn",
  "topbar.linkedin_aria": "Open LinkedIn",
  "topbar.github_title": "GitHub",
  "topbar.github_aria": "Open GitHub",
  "topbar.support_title": "Support the project",
  "topbar.support_aria": "Support the project",
  "topbar.theme_light_title": "Light mode",
  "topbar.theme_dark_title": "Dark mode",
  "topbar.theme_light_aria": "Switch to light mode",
  "topbar.theme_dark_aria": "Switch to dark mode",
  "topbar.lang_aria": "Select language",
  "topbar.lang_pt_title": "Português (Brasil)",
  "topbar.lang_en_title": "English (US)",

  // ----- Update banner -----
  "update.available": "Update available: v{version}",
  "update.current_hint": "You are on v{current}. Check the release page for what's new.",
  "update.see": "View update",
  "update.dismiss_title": "Dismiss this version",
  "update.dismiss_aria": "Dismiss this update",

  // ----- Empty state (select folder) -----
  "empty.cta_aria": "Select folder with PBIP projects",
  "empty.cta_title": "Select the folder with your PBIP projects",
  "empty.cta_subtitle": "We'll scan the subfolders and list the projects we find.",

  // ----- Path bar -----
  "pathbar.label": "Selected folder",
  "pathbar.change": "Change",
  "pathbar.change_aria": "Change selected folder",

  // ----- Scanning state -----
  "scanning.title": "Looking for projects...",
  "scanning.subtitle": "Scanning subfolders for .pbip files.",

  // ----- Project panel -----
  "panel.found_one": "project found",
  "panel.found_many": "projects found",
  "panel.checked_one": "selected",
  "panel.checked_many": "selected",
  "panel.search_placeholder": "Filter by name or path...",
  "panel.search_aria": "Filter project list",
  "panel.search_clear_title": "Clear filter",
  "panel.search_clear_aria": "Clear filter",
  "panel.select_all": "Select all",
  "panel.clear_selection": "Clear",
  "panel.rescan_title": "Rescan folder",
  "panel.rescan_aria": "Rescan folder",
  "panel.empty_filtered": 'No project matches "{query}"',
  "panel.empty_filtered_clear": "Clear filter",

  // ----- Project row status badges -----
  "project.processing_aria": "Processing",
  "project.ok_pill_title": "Open this project's folder",
  "project.ok_pill_aria": "Success, open folder",
  "project.error_pill_title": "Error",
  "project.error_pill_aria": "Error: {message}",

  // ----- Empty result (scan done but zero matches) -----
  "result.empty_title": "No PBIP project found",
  "result.empty_subtitle": "Check that the selected folder contains .pbip files or subfolders with Power BI models.",

  // ----- PBIX block (legacy files, need manual conversion) -----
  "pbix.title_one": "{n} .pbix file found — needs conversion",
  "pbix.title_many": "{n} .pbix files found — need conversion",
  "pbix.subtitle": "BI Doc Maker only documents projects in PBIP format (folder-based). To document these files, convert them first in Power BI Desktop:",
  "pbix.step_1": "Open the file in Power BI Desktop",
  "pbix.step_2": "File → Save As",
  "pbix.step_3": "In \"Save as type\", choose \"Power BI Project files (*.pbip)\"",
  "pbix.step_4": "Save in a folder — Desktop generates the converted PBIP project",
  "pbix.step_5": "Come back here and pick the folder again to rescan",
  "pbix.requires_desktop": "Requires Power BI Desktop with PBIP support (2024 release or newer).",

  // ----- Error notice -----
  "notice.error_title": "Error",

  // ----- Batch summary -----
  "batch.summary_one": "{ok}/{total} document generated",
  "batch.summary_many": "{ok}/{total} documents generated",
  "batch.success": "All done! Documentation saved.",
  "batch.partial_fail": "{n} failed. See details for each project in the list.",
  "batch.open_folder": "Open folder",

  // ----- Action bar -----
  "action.more_options": "More Options",
  "action.generating": "Generating {project}",
  "action.generating_idle": "...",
  "action.generate": "Generate Documentation ({n})",

  // ----- Options modal -----
  "modal.title": "More Options",
  "modal.subtitle": "Customize the documentation that will be generated.",
  "modal.close_title": "Close",
  "modal.close_aria": "Close options",

  "modal.formats_title": "Export formats",
  "modal.formats_subtitle": "Pick one or more formats.",
  "modal.formats_group_aria": "Export formats",
  "format.md": "Markdown",
  "format.docx": "Word",
  "format.html": "HTML / Save as PDF",

  "modal.output_title": "Output folder",
  "modal.output_subtitle": "In batch mode, all projects share this folder.",
  "modal.output_default": "Project folder",
  "modal.output_batch_suffix": "{path} (batch → selected folder)",
  "modal.output_pick": "Pick",
  "modal.output_default_btn": "Default",

  "modal.title_doc_heading": "Document title",
  "modal.title_doc_subtitle": "Shown on the cover of each document.",
  "modal.title_doc_placeholder": "Power BI Documentation",
  "modal.title_doc_aria": "Title displayed on the document",

  "modal.logo_heading": "Company logo",
  "modal.logo_subtitle": "PNG or JPG, displayed on the cover.",
  "modal.logo_empty": "No logo selected",
  "modal.logo_pick": "Pick",
  "modal.logo_remove": "Remove",

  "modal.colors_heading": "Documentation colors",
  "modal.colors_subtitle": "Define the visual scheme applied.",
  "modal.color_primary": "Primary",
  "modal.color_secondary": "Secondary",
  "modal.color_light": "Light background",
  "modal.color_primary_aria": "Primary color",
  "modal.color_secondary_aria": "Secondary color",
  "modal.color_light_aria": "Light background color",

  "modal.restore_defaults": "Restore defaults",
  "modal.finish": "Done",

  // ----- Error messages -----
  "err.processing_timeout": "Processing failed or took too long to respond.",
  "err.scan_failed": "Failed to scan the folder: {detail}",
  "err.no_projects": "No Power BI project (.pbip) found in this folder.",
  "err.select_project_format": "Pick at least one project and one format.",
  "err.generation_failed": "Failed to generate the documentation.",
  "err.open_link": "Could not open the link: {detail}",
  "err.open_release": "Could not open the release: {detail}",
  "err.open_html": "Documentation generated, but failed to open the HTML: {detail}",

  // ----- Branding defaults -----
  "branding.default_title": "Power BI Documentation",
};
