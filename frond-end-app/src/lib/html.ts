import type { AnalysisResult } from "./markdown";

const escapeHtml = (value: string): string =>
  value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");

export const buildHtml = (result: AnalysisResult): string => {
  const tables = result.tables.length
    ? result.tables.map((table) => `<li>${escapeHtml(table)}</li>`).join("")
    : "<li>(nenhuma tabela encontrada)</li>";

  const warnings = result.warnings.length
    ? `
      <h2>Avisos</h2>
      <ul>
        ${result.warnings
          .map((warning) => `<li>${escapeHtml(warning)}</li>`)
          .join("")}
      </ul>
    `
    : "";

  return `
    <section class="print-area">
      <h1>Documentacao do Projeto Power BI</h1>
      <p><strong>Projeto:</strong> ${escapeHtml(result.project_name)}</p>
      <p><strong>Layout:</strong> ${escapeHtml(result.layout)}</p>
      <h2>Visao Geral</h2>
      <ul>
        <li>Tabelas: ${result.table_count}</li>
        <li>Relacionamentos: ${result.relationship_count}</li>
        <li>Paginas: ${result.page_count}</li>
      </ul>
      <h2>Tabelas</h2>
      <ul>
        ${tables}
      </ul>
      ${warnings}
    </section>
  `;
};
