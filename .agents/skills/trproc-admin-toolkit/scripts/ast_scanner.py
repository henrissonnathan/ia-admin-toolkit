import re
import sys
import os

def scan_file(filepath):
    if not os.path.exists(filepath):
        print(f"Erro: Arquivo '{filepath}' não encontrado.")
        return

    print(f"--- MAPA DE FUNÇÕES: {filepath} ---")
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    is_js = filepath.endswith('.js')
    is_py = filepath.endswith('.py')
    
    for i, line in enumerate(lines):
        line_num = i + 1
        line_clean = line.strip()
        
        if is_js:
            # Pega funções normais: function nomeDaFuncao(args)
            if line_clean.startswith("function "):
                match = re.search(r'function\s+([a-zA-Z0-9_]+)\s*\(', line_clean)
                if match:
                    print(f"Linha {line_num:04d} | function {match.group(1)}()")
            # Pega arrow functions: const nomeDaFuncao = (args) =>
            elif " = (" in line_clean and "=>" in line_clean and line_clean.startswith(("const ", "let ", "var ")):
                match = re.search(r'(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*\(', line_clean)
                if match:
                    print(f"Linha {line_num:04d} | arrow_fn {match.group(1)}()")
            # Pega métodos de classe ou objetos: nomeDoMetodo(args) {
            elif re.match(r'^[a-zA-Z0-9_]+\s*\([^)]*\)\s*\{', line_clean) and not line_clean.startswith("if") and not line_clean.startswith("for") and not line_clean.startswith("while"):
                match = re.search(r'^([a-zA-Z0-9_]+)\s*\(', line_clean)
                if match:
                    print(f"Linha {line_num:04d} | method   {match.group(1)}()")

        elif is_py:
            if line_clean.startswith("def "):
                match = re.search(r'def\s+([a-zA-Z0-9_]+)\s*\(', line_clean)
                if match:
                    print(f"Linha {line_num:04d} | def {match.group(1)}()")
            elif line_clean.startswith("class "):
                match = re.search(r'class\s+([a-zA-Z0-9_]+)', line_clean)
                if match:
                    print(f"Linha {line_num:04d} | CLASS {match.group(1)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python ast_scanner.py <caminho_do_arquivo>")
    else:
        scan_file(sys.argv[1])
