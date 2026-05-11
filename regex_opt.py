import re

with open('documentador_pbip.py', 'r', encoding='utf-8') as f:
    text = f.read()

module_regexes = """
# Regexes Pre-compiladas para ganho de performance
RE_TABLE = re.compile(r"^table\s+['\\\"](.+?)['\\\"]$")
RE_COLUMN = re.compile(r"^column\s+['\\\"](.+?)['\\\"]\s*(?:=\s*(.+))?$")
RE_MEASURE = re.compile(r"^measure\s+['\\\"](.+?)['\\\"]\s*=\s*(.+)$")
"""

if '# Regexes Pre-compiladas' not in text:
    text = text.replace('import base64\n', 'import base64\n' + module_regexes + '\n')

text = text.replace(r"re.match(r'^table\s+[\'\"](.+?)[\'\"]$', linha)", "RE_TABLE.match(linha)")
text = text.replace(r"re.match(r'^column\s+[\'\"](.+?)[\'\"]\s*(?:=\s*(.+))?$', linha)", "RE_COLUMN.match(linha)")
text = text.replace(r"re.match(r'^measure\s+[\'\"](.+?)[\'\"]\s*=\s*(.+)$', linha)", "RE_MEASURE.match(linha)")

with open('documentador_pbip.py', 'w', encoding='utf-8') as f:
    f.write(text)
