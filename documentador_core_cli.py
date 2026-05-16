"""
CLI do core Python para uso como sidecar do Tauri.

Contrato importante: stdout sempre deve conter apenas um JSON por execucao.
Logs de progresso do DocumentadorPBIP sao redirecionados para stderr.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import traceback
from contextlib import redirect_stdout
from pathlib import Path
from typing import Dict, List

from documentador_pbip import DocumentadorPBIP
import i18n

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr)
logger = logging.getLogger(__name__)


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
    # Garante UTF-8 nos streams principais.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception as exc:
            sys.stderr.write(f"[AVISO] Falha ao reconfigurar {stream.name} para utf-8: {exc}\n")

    # Reforco para subprocessos futuros (nao afeta este, mas documenta intencao).
    import os as _os
    _os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    _os.environ.setdefault("PYTHONUTF8", "1")


def _fix_mojibake(texto: str) -> str:
    """Recupera texto que sofreu double-encoding UTF-8 -> cp1252 -> UTF-8.

    Cenario: o sidecar recebeu via argv um JSON ou caminho cujos bytes
    UTF-8 foram interpretados como cp1252 antes de virar str Python.
    Sintoma: "Documentação" aparece como "DocumentaÃ§Ã£o" (presença
    repetida de 'Ã' seguido de outro caractere alto).

    Se nao houver sinais de mojibake, retorna o texto original.
    """
    if not isinstance(texto, str) or not texto:
        return texto

    # Sinal heuristico: presença de 'Ã' (U+00C3) — raro em portugues real
    # — e que tipicamente acompanha mojibake.
    if "Ã" not in texto and "Â" not in texto:
        return texto

    try:
        # Re-codifica como latin-1 (recupera os bytes UTF-8 originais)
        # e decodifica como UTF-8 (re-interpreta corretamente).
        recuperado = texto.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return texto

    # So aplica se reduziu efetivamente o numero de 'Ã' (sinal de melhoria).
    if recuperado.count("Ã") < texto.count("Ã"):
        return recuperado
    return texto


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


def _analisar(caminho_projeto: str) -> DocumentadorPBIP:
    doc = DocumentadorPBIP(caminho_projeto)
    doc.extrair_informacoes()
    return doc


def comando_analyze(args: argparse.Namespace, logs: CapturaLogs) -> Dict:
    with redirect_stdout(logs):
        i18n.set_locale(getattr(args, "lang", "pt") or "pt")
        project_fixed = _fix_mojibake(args.project)
        doc = _analisar(project_fixed)
        return doc.gerar_resumo_estruturado(warnings=logs.avisos())


def comando_export(args: argparse.Namespace, logs: CapturaLogs) -> Dict:
    with redirect_stdout(logs):
        i18n.set_locale(getattr(args, "lang", "pt") or "pt")
        formatos = _normalizar_formatos(args.formats)
        # Recupera mojibake potencial em paths e branding antes de usar.
        project_fixed = _fix_mojibake(args.project)
        output_dir_raw = _fix_mojibake(args.output_dir)
        output_dir = Path(output_dir_raw) / "Doc_BI"
        output_dir.mkdir(parents=True, exist_ok=True)

        doc = _analisar(project_fixed)
        branding_json_fixed = _fix_mojibake(args.branding_json) if args.branding_json else None
        branding = json.loads(branding_json_fixed) if branding_json_fixed else None
        if isinstance(branding, dict):
            # Aplica fix_mojibake em todos os valores de string do branding.
            branding = {
                k: _fix_mojibake(v) if isinstance(v, str) else v
                for k, v in branding.items()
            }
        doc.aplicar_branding(branding)
        outputs: Dict[str, str] = {}

        filename_suffix = i18n.t("filename.suffix")
        for formato in formatos:
            caminho_saida = output_dir / f"{doc.nome_projeto}{filename_suffix}.{formato}"
            if formato == "md":
                gerado = doc.salvar_documentacao(str(caminho_saida))
            elif formato == "docx":
                gerado = doc.salvar_documentacao_docx(str(caminho_saida))
            elif formato == "html":
                gerado = doc.salvar_documentacao_html(str(caminho_saida), auto_print=False)
            else:
                raise ValueError(f"Formato nao suportado: {formato}")

            if not gerado:
                raise RuntimeError(f"Falha ao gerar arquivo {formato}.")
            outputs[formato] = str(Path(gerado).resolve())

        return doc.gerar_resumo_estruturado(outputs=outputs, warnings=logs.avisos())


def _criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="documentador-core")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Idioma da documentacao gerada (e tambem do nome do arquivo).
    # Aceita pt, pt_BR, pt-BR, en, en_US, en-US (case-insensitive). Default: pt.
    LANG_HELP = "Idioma da documentacao (pt|en). Default: pt."

    analyze = subparsers.add_parser("analyze", help="Analisa um projeto Power BI.")
    analyze.add_argument("--project", required=True, help="Pasta do projeto .pbip.")
    analyze.add_argument("--lang", default="pt", help=LANG_HELP)
    analyze.add_argument("--json", action="store_true", help="Mantido para contrato com o sidecar.")

    export = subparsers.add_parser("export", help="Exporta a documentacao do projeto.")
    export.add_argument("--project", required=True, help="Pasta do projeto .pbip.")
    export.add_argument("--output-dir", required=True, help="Pasta onde os arquivos serao salvos.")
    export.add_argument("--formats", required=True, help="Formatos separados por virgula: md,docx,html.")
    export.add_argument("--branding-json", help="JSON opcional com logoPath, primaryColor, secondaryColor e lightColor.")
    export.add_argument("--lang", default="pt", help=LANG_HELP)
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
