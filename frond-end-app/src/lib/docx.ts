import {
  Document,
  HeadingLevel,
  Packer,
  Paragraph,
  TextRun
} from "docx";
import type { AnalysisResult } from "./markdown";

export const buildDocx = async (result: AnalysisResult): Promise<Uint8Array> => {
  const doc = new Document({
    sections: [
      {
        children: [
          new Paragraph({
            text: "Documentacao do Projeto Power BI",
            heading: HeadingLevel.HEADING_1
          }),
          new Paragraph({
            children: [
              new TextRun({ text: "Projeto: ", bold: true }),
              new TextRun(result.project_name)
            ]
          }),
          new Paragraph({
            children: [
              new TextRun({ text: "Layout: ", bold: true }),
              new TextRun(result.layout)
            ]
          }),
          new Paragraph({ text: "" }),
          new Paragraph({ text: "Visao Geral", heading: HeadingLevel.HEADING_2 }),
          new Paragraph(`Tabelas: ${result.table_count}`),
          new Paragraph(`Relacionamentos: ${result.relationship_count}`),
          new Paragraph(`Paginas: ${result.page_count}`),
          new Paragraph({ text: "" }),
          new Paragraph({ text: "Tabelas", heading: HeadingLevel.HEADING_2 }),
          ...(result.tables.length > 0
            ? result.tables.map((table) => new Paragraph(`- ${table}`))
            : [new Paragraph("- (nenhuma tabela encontrada)")]),
          ...(result.warnings.length > 0
            ? [
                new Paragraph({ text: "" }),
                new Paragraph({ text: "Avisos", heading: HeadingLevel.HEADING_2 }),
                ...result.warnings.map((warning) => new Paragraph(`- ${warning}`))
              ]
            : [])
        ]
      }
    ]
  });

  const blob = await Packer.toBlob(doc);
  const buffer = await blob.arrayBuffer();
  return new Uint8Array(buffer);
};
