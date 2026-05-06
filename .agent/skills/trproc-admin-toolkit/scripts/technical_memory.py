import os
import json
import ast
import re

class TechnicalMemory:
    """
    Motor de Memória Técnica e Precisão (P17).
    Analisa o código e gera relatórios de 'Estado da Arte' para consumo da IA.
    """
    
    def __init__(self, root_dir="."):
        self.root_dir = root_dir
        self.memory_file = os.path.join(root_dir, "TECHNICAL_MEMORY.json")
        self.memory = self.load_memory()

    def load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"analyses": {}, "integrity_score": 0, "last_scan": ""}

    def analyze_file_precision(self, file_path):
        """Analisa a complexidade e densidade de lógica de um arquivo."""
        abs_path = os.path.join(self.root_dir, file_path)
        if not os.path.exists(abs_path):
            return None

        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()

        analysis = {
            "lines": len(content.splitlines()),
            "functions": [],
            "critical_patterns": [],
            "risk_score": 0
        }

        # Busca padrões críticos (ex: SQL bruto, falta de sanitização)
        if ".js" in file_path:
            # Procura por concatenação de strings em HTML (Risco XSS)
            if re.search(r'\.innerHTML\s*=\s*.*?\+', content):
                analysis["critical_patterns"].append("DANGEROUS_INNERHTML_CONCAT")
                analysis["risk_score"] += 10
            
            # Procura por AJAX/Fetch sem tratamento de erro
            if re.search(r'fetch\(.*?\)\.then\(', content) and not ".catch(" in content:
                analysis["critical_patterns"].append("UNPROTECTED_FETCH")
                analysis["risk_score"] += 5

        if ".py" in file_path:
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        analysis["functions"].append(node.name)
            except:
                analysis["critical_patterns"].append("SYNTAX_ERROR_PARSING")

        self.memory["analyses"][file_path] = analysis
        self.save_memory()
        return analysis

    def save_memory(self):
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2)

if __name__ == "__main__":
    tm = TechnicalMemory()
    print("Iniciando Escaneamento de Precisão...")
    # Analisa arquivos chave
    tm.analyze_file_precision("static/js/formulario.js")
    tm.analyze_file_precision("routes/admin_estudio.py")
    print("TECHNICAL_MEMORY.json atualizado com sucesso.")
