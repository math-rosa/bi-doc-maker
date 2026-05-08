export type AnalysisResult = {
  project_name: string;
  layout: string;
  table_count: number;
  relationship_count: number;
  page_count: number;
  tables: string[];
  warnings: string[];
};

export const buildMarkdown = (result: AnalysisResult): string => {
  const lines: string[] = [];
  lines.push("# Documentacao do Projeto Power BI");
  lines.push("");
  lines.push(`**Projeto**: ${result.project_name}`);
  lines.push(`**Layout**: ${result.layout}`);
  lines.push("");
  lines.push("## Visao Geral");
  lines.push("");
  lines.push(`- Tabelas: ${result.table_count}`);
  lines.push(`- Relacionamentos: ${result.relationship_count}`);
  lines.push(`- Paginas: ${result.page_count}`);
  lines.push("");
  lines.push("## Tabelas");
  lines.push("");
  if (result.tables.length === 0) {
    lines.push("- (nenhuma tabela encontrada)");
  } else {
    for (const table of result.tables) {
      lines.push(`- ${table}`);
    }
  }
  lines.push("");
  if (result.warnings.length > 0) {
    lines.push("## Avisos");
    lines.push("");
    for (const warning of result.warnings) {
      lines.push(`- ${warning}`);
    }
  }
  lines.push("");
  return lines.join("\n");
};
