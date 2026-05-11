import re
import os

with open('documentador_pbip.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract dataclass definitions to a separate string
dataclass_pattern = re.compile(r'(@dataclass\nclass Info.*?:(?:\n(?:    .*|(?:\s*)))+)(?=\n@|\ndef|\nclass|\Z)', re.MULTILINE)
models = dataclass_pattern.findall(content)

imports_models = """from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
\n\n"""

with open('documentador_models.py', 'w', encoding='utf-8') as f:
    f.write(imports_models)
    for model in models:
        f.write(model.strip() + "\n\n")

# Remove models from original
new_content = dataclass_pattern.sub('', content)

# Add import at the top
import_str = "from documentador_models import InfoColuna, InfoColunaCalculada, InfoMedida, InfoHierarquia, InfoParticao, InfoTabela, InfoRelacionamento, InfoModelo, InfoVisual, InfoPagina\n"
new_content = new_content.replace('from dataclasses import dataclass, field\n', import_str)

with open('documentador_pbip.py', 'w', encoding='utf-8') as f:
    f.write(new_content)
