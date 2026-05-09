"""
CLI do core Python para uso como sidecar do Tauri.

Contrato importante: stdout sempre deve conter apenas um JSON por execucao.
Logs de progresso do DocumentadorPBIP sao redirecionados para stderr.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import traceback
from contextlib import redirect_stdout
from pathlib import Path
from typing import Dict, List

from documentador_pbip import DocumentadorPBIP


FORMATOS_SUPORTADOS = {"md", "docx", "html"}


class CapturaLogs:
    """Espelha stdout legado em stderr e guarda linhas para avisos."""

    def __init__(self) -> None:
        self._partes: List[str] = []

    def write(self, texto: str) -> int:
        self._partes.append(texto)
        sys.stderr.write(texto)
        return len(texto)

    def flush(self) -> None:
        sys.stderr.flush()

    @property
    def texto(self) -> str:
        return "".join(self._partes)

    def avisos(self) -> List[str]:
        avisos: List[str] = []
        for linha in self.texto.splitlines():
            linha_limpa = linha.strip()
            if "[AVISO]" in linha_limpa or "[ERRO]" in linha_limpa:
                avisos.append(linha_limpa)
        return list(dict.fromkeys(avisos))


def _configurar_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass


def _imprimir_json(payload: Dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _normalizar_formatos(valor: str) -> List[str]:
    formatos = [item.strip().lower() for item in valor.split(",") if item.strip()]
    invalidos = [item for item in formatos if item not in FORMATOS_SUPORTADOS]
    if invalidos:
        raise ValueError(f"Formato(s) invalido(s): {', '.join(invalidos)}")
    if not formatos:
        raise ValueError("Informe pelo menos um formato de exportacao.")
    return formatos


def _normalizar_branding(valor: str | None) -> Dict:
    if not valor:
        return {}

    try:
        branding = json.loads(valor)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON de branding invalido: {exc}") from exc

    if not isinstance(branding, dict):
        raise ValueError("JSON de branding deve ser um objeto.")

    for chave in ("primaryColor", "secondaryColor", "lightColor"):
        cor = str(branding.get(chave) or "").strip()
        if cor and not re.fullmatch(r"#[0-9a-fA-F]{6}", cor):
            raise ValueError(f"Cor invalida em {chave}: use o formato #RRGGBB.")

    logo = str(branding.get("logoPath") or "").strip()
    if logo:
        logo_path = Path(logo).expanduser()
        if not logo_path.is_file():
            raise ValueError(f"Logo nao encontrado: {logo}")
        if logo_path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            raise ValueError("Logo deve ser uma imagem .png, .jpg ou .jpeg.")

    return branding


def _analisar(caminho_projeto: str, logs: CapturaLogs) -> DocumentadorPBIP:
    with redirect_stdout(logs):
        doc = DocumentadorPBIP(caminho_projeto)
        doc.extrair_informacoes()
    return doc


def comando_analyze(args: argparse.Namespace, logs: CapturaLogs) -> Dict:
    doc = _analisar(args.project, logs)
    return doc.gerar_resumo_estruturado(warnings=logs.avisos())


def comando_export(args: argparse.Namespace, logs: CapturaLogs) -> Dict:
    formatos = _normalizar_formatos(args.formats)
    branding = _normalizar_branding(args.branding_json)
    output_dir = Path(args.output_dir) / "Doc_BI"
    output_dir.mkdir(parents=True, exist_ok=True)

    doc = _analisar(args.project, logs)
    outputs: Dict[str, str] = {}

    with redirect_stdout(logs):
        doc.aplicar_branding(branding)

        for formato in formatos:
            caminho_saida = output_dir / f"{doc.nome_projeto}_documentacao.{formato}"
            if formato == "md":
                gerado = doc.salvar_documentacao(str(caminho_saida))
            elif formato == "docx":
                gerado = doc.salvar_documentacao_docx(str(caminho_saida))
            elif formato == "html":
                gerado = doc.salvar_documentacao_html(str(caminho_saida), auto_print=True)
            else:
                raise ValueError(f"Formato nao suportado: {formato}")

            if not gerado:
                raise RuntimeError(f"Falha ao gerar arquivo {formato}.")
            outputs[formato] = str(Path(gerado).resolve())

    return doc.gerar_resumo_estruturado(outputs=outputs, warnings=logs.avisos())


def _criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="documentador-core")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Analisa um projeto Power BI.")
    analyze.add_argument("--project", required=True, help="Pasta do projeto .pbip.")
    analyze.add_argument("--json", action="store_true", help="Mantido para contrato com o sidecar.")

    export = subparsers.add_parser("export", help="Exporta a documentacao do projeto.")
    export.add_argument("--project", required=True, help="Pasta do projeto .pbip.")
    export.add_argument("--output-dir", required=True, help="Pasta onde os arquivos serao salvos.")
    export.add_argument("--formats", required=True, help="Formatos separados por virgula: md,docx,html.")
    export.add_argument("--branding-json", help="Configuracao visual em JSON.")
    export.add_argument("--json", action="store_true", help="Mantido para contrato com o sidecar.")

    return parser


def main() -> int:
    _configurar_stdio()

    logs = CapturaLogs()
    parser = _criar_parser()

    try:
        args = parser.parse_args()
        if args.command == "analyze":
            payload = comando_analyze(args, logs)
        elif args.command == "export":
            payload = comando_export(args, logs)
        else:
            raise ValueError(f"Comando desconhecido: {args.command}")

        _imprimir_json(payload)
        return 0
    except SystemExit as exc:
        codigo = int(exc.code) if isinstance(exc.code, int) else 2
        _imprimir_json({
            "ok": False,
            "error": f"Argumentos invalidos (codigo {codigo}).",
            "warnings": logs.avisos(),
            "outputs": {},
        })
        return codigo
    except Exception as exc:
        traceback.print_exc(file=sys.stderr)
        _imprimir_json({
            "ok": False,
            "error": str(exc),
            "warnings": logs.avisos(),
            "outputs": {},
        })
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
