#!/usr/bin/env python3
"""
TRPROC IA-ADMIN-TOOLKIT: Health Check & Boot Sequence
=====================================================
Verifica toda a estrutura do toolkit, valida skills,
testa regras e mostra status visual de inicializacao.

Uso: py health_check.py [--project-path C:/caminho/do/projeto]
"""
import os
import sys
import io
import time
import glob
import json
from datetime import datetime

# Forcar UTF-8 no Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Configuração ──────────────────────────────────────────────
# scripts/ esta dentro de .agent/, entao subimos 2 niveis: scripts -> .agent -> toolkit_root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AGENT_DIR = os.path.dirname(SCRIPT_DIR)           # .agent/
TOOLKIT_ROOT = os.path.dirname(AGENT_DIR)          # ia-admin-toolkit/
SKILLS_DIR = os.path.join(AGENT_DIR, "skills")
TEMPLATES_DIR = os.path.join(AGENT_DIR, "templates")
MEMORY_DIR = os.path.join(AGENT_DIR, "memory")

# Símbolos visuais
S_OK = "✅"
S_WARN = "⚠️"
S_ERR = "❌"
S_INFO = "ℹ️"
S_BOOT = "⚡"
S_SKIP = "⏭️"

# ── Motor de Tradução de Erros ────────────────────────────────
ERROR_TRANSLATIONS = {
    "MISSING_MIN": {
        "human": "A skill '{name}' não possui arquivo SKILL.min.txt (versão compacta para IA).",
        "ai":    "[MISS]:{name}/SKILL.min.txt. req(create_min).",
        "level": "WARN",
        "fix":   "Rode /smart-init ou peça à IA para gerar o .min.txt desta skill."
    },
    "MISSING_MD": {
        "human": "A skill '{name}' não possui arquivo SKILL.md (versão humana).",
        "ai":    "[MISS]:{name}/SKILL.md. CRITICAL.",
        "level": "ERR",
        "fix":   "Esta skill está incompleta. Crie o SKILL.md com a documentação."
    },
    "MISSING_MEMORY": {
        "human": "A pasta de memória (.agent/memory/) não existe neste projeto.",
        "ai":    "[MISS]:.agent/memory/. req(/smart-init).",
        "level": "WARN",
        "fix":   "Rode /smart-init para criar a estrutura de memória."
    },
    "MISSING_TEMPLATE": {
        "human": "Template '{name}' não encontrado em .agent/templates/.",
        "ai":    "[MISS]:templates/{name}. req(create).",
        "level": "WARN",
        "fix":   "Atualize o toolkit com /update-toolkit."
    },
    "CORE_OUTDATED": {
        "human": "AI_CORE.min.txt está desatualizado (versão < v2).",
        "ai":    "[OLD]:AI_CORE.min.txt<v2. req(update).",
        "level": "ERR",
        "fix":   "Atualize o AI_CORE.min.txt para a versão v2."
    },
    "CORE_MISSING": {
        "human": "AI_CORE.min.txt não encontrado! As regras da IA não estão ativas.",
        "ai":    "[MISS]:AI_CORE.min.txt. CRITICAL. req(/smart-init).",
        "level": "ERR",
        "fix":   "Clone o toolkit novamente ou rode /update-toolkit."
    },
    "GITIGNORE_MISSING": {
        "human": "A pasta .agent/memory/ não está no .gitignore. Dados privados podem vazar!",
        "ai":    "[SEC]:.agent/memory/ !in .gitignore. CRITICAL.",
        "level": "ERR",
        "fix":   "Adicione '.agent/memory/' ao .gitignore do projeto."
    }
}

def translate_error(error_code, **kwargs):
    """Motor de tradução: retorna erro em formato humano + IA."""
    tmpl = ERROR_TRANSLATIONS.get(error_code, {})
    return {
        "human": tmpl.get("human", error_code).format(**kwargs),
        "ai":    tmpl.get("ai", error_code).format(**kwargs),
        "level": tmpl.get("level", "INFO"),
        "fix":   tmpl.get("fix", ""),
        "code":  error_code
    }

# ── Funções de Verificação ────────────────────────────────────
def check_skills():
    """Verifica se todas as skills possuem formato dual (.md + .min.txt)."""
    results = []
    if not os.path.isdir(SKILLS_DIR):
        return [translate_error("MISSING_MD", name="(skills dir)")]

    for skill_name in sorted(os.listdir(SKILLS_DIR)):
        skill_path = os.path.join(SKILLS_DIR, skill_name)
        if not os.path.isdir(skill_path):
            continue

        has_md = os.path.isfile(os.path.join(skill_path, "SKILL.md"))
        has_min = os.path.isfile(os.path.join(skill_path, "SKILL.min.txt"))

        if not has_md:
            results.append(translate_error("MISSING_MD", name=skill_name))
        elif not has_min:
            results.append(translate_error("MISSING_MIN", name=skill_name))
        else:
            results.append({
                "human": f"Skill '{skill_name}' possui formato dual completo.",
                "ai": f"[OK]:{skill_name}(md+min).",
                "level": "OK",
                "fix": "",
                "code": "SKILL_OK"
            })
    return results

def check_core():
    """Verifica AI_CORE.min.txt e sua versão."""
    core_path = os.path.join(AGENT_DIR, "AI_CORE.min.txt")
    if not os.path.isfile(core_path):
        return [translate_error("CORE_MISSING")]

    with open(core_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "v2" not in content and "v3" not in content:
        return [translate_error("CORE_OUTDATED")]

    rule_count = len([l for l in content.strip().split("\n") if l.strip() and not l.startswith("[")])
    return [{
        "human": f"AI_CORE.min.txt (v2) carregado com {rule_count} regras ativas.",
        "ai": f"[OK]:AI_CORE.min.txt(v2,{rule_count}rules).",
        "level": "OK",
        "fix": "",
        "code": "CORE_OK"
    }]

def check_templates():
    """Verifica se os templates de memória existem."""
    required = ["ERROR_VAULT.md", "IDEIAS_SUGERIDAS.md", "HISTORY.min.log", "CONTEXT_MAP.min.txt"]
    results = []
    for tmpl in required:
        path = os.path.join(TEMPLATES_DIR, tmpl)
        if os.path.isfile(path):
            results.append({
                "human": f"Template '{tmpl}' presente.",
                "ai": f"[OK]:tmpl/{tmpl}.",
                "level": "OK", "fix": "", "code": "TMPL_OK"
            })
        else:
            results.append(translate_error("MISSING_TEMPLATE", name=tmpl))
    return results

def check_memory(project_path=None):
    """Verifica se a pasta de memória existe no projeto alvo."""
    if not project_path:
        return [{
            "human": "Nenhum projeto alvo especificado. Verificação de memória pulada.",
            "ai": "[SKIP]:no_project_path.",
            "level": "SKIP", "fix": "", "code": "MEM_SKIP"
        }]

    mem_path = os.path.join(project_path, ".agent", "memory")
    results = []
    if not os.path.isdir(mem_path):
        results.append(translate_error("MISSING_MEMORY"))
    else:
        files = os.listdir(mem_path)
        results.append({
            "human": f"Memória do projeto encontrada ({len(files)} arquivo(s)).",
            "ai": f"[OK]:memory({len(files)}files).",
            "level": "OK", "fix": "", "code": "MEM_OK"
        })

    # Verificar .gitignore
    gitignore = os.path.join(project_path, ".gitignore")
    if os.path.isfile(gitignore):
        with open(gitignore, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if ".agent/memory" not in content and ".agent/" not in content:
            results.append(translate_error("GITIGNORE_MISSING"))
    return results

# ── Exibição Visual (Boot Sequence) ──────────────────────────
def print_boot_header():
    """Exibe cabeçalho de inicialização."""
    print()
    print("=" * 60)
    print(f"  {S_BOOT} TRPROC IA-ADMIN-TOOLKIT — Health Check v2")
    print(f"  {S_INFO} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

def print_section(title, results):
    """Exibe uma seção de resultados com ícones visuais."""
    icon_map = {"OK": S_OK, "WARN": S_WARN, "ERR": S_ERR, "INFO": S_INFO, "SKIP": S_SKIP}
    counts = {"OK": 0, "WARN": 0, "ERR": 0}

    print(f"  ── {title} {'─' * (45 - len(title))}")
    for r in results:
        level = r["level"]
        icon = icon_map.get(level, S_INFO)
        counts[level] = counts.get(level, 0) + 1

        # Humano vê a mensagem legível
        print(f"  {icon} {r['human']}")
        if r["fix"] and level in ("ERR", "WARN"):
            print(f"     └─ Correção: {r['fix']}")

    print()
    return counts

def generate_ai_report(all_results):
    """Gera relatório minificado para a IA ler."""
    lines = [f"[HEALTH:v2:{datetime.now().strftime('%Y%m%d_%H%M')}]"]
    for section, results in all_results.items():
        items = "|".join(r["ai"] for r in results)
        lines.append(f"{section}:{items}")
    return "\n".join(lines)

def generate_human_report(all_results, counts_total):
    """Gera relatório legível para humano."""
    lines = [
        f"# Health Check Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"| Status | Qtd |",
        f"|--------|-----|",
        f"| {S_OK} OK | {counts_total.get('OK', 0)} |",
        f"| {S_WARN} Avisos | {counts_total.get('WARN', 0)} |",
        f"| {S_ERR} Erros | {counts_total.get('ERR', 0)} |",
        ""
    ]
    for section, results in all_results.items():
        lines.append(f"## {section}")
        for r in results:
            icon = {
                "OK": S_OK, "WARN": S_WARN, "ERR": S_ERR
            }.get(r["level"], S_INFO)
            lines.append(f"- {icon} {r['human']}")
            if r["fix"] and r["level"] in ("ERR", "WARN"):
                lines.append(f"  - Correção: {r['fix']}")
        lines.append("")
    return "\n".join(lines)

# ── Main ──────────────────────────────────────────────────────
def main():
    project_path = None
    if "--project-path" in sys.argv:
        idx = sys.argv.index("--project-path")
        if idx + 1 < len(sys.argv):
            project_path = sys.argv[idx + 1]

    print_boot_header()

    all_results = {}
    counts_total = {"OK": 0, "WARN": 0, "ERR": 0}

    # Fase 1: AI_CORE
    print(f"  {S_BOOT} Fase 1: Verificando AI_CORE...")
    all_results["AI_CORE"] = check_core()
    c = print_section("AI_CORE (Regras da IA)", all_results["AI_CORE"])
    for k, v in c.items(): counts_total[k] = counts_total.get(k, 0) + v

    # Fase 2: Skills
    print(f"  {S_BOOT} Fase 2: Verificando Skills (formato dual)...")
    all_results["SKILLS"] = check_skills()
    c = print_section("Skills (SKILL.md + SKILL.min.txt)", all_results["SKILLS"])
    for k, v in c.items(): counts_total[k] = counts_total.get(k, 0) + v

    # Fase 3: Templates
    print(f"  {S_BOOT} Fase 3: Verificando Templates...")
    all_results["TEMPLATES"] = check_templates()
    c = print_section("Templates de Memória", all_results["TEMPLATES"])
    for k, v in c.items(): counts_total[k] = counts_total.get(k, 0) + v

    # Fase 4: Memória do Projeto
    if project_path:
        print(f"  {S_BOOT} Fase 4: Verificando Memória do Projeto...")
        all_results["MEMORY"] = check_memory(project_path)
        c = print_section("Memória do Projeto", all_results["MEMORY"])
        for k, v in c.items(): counts_total[k] = counts_total.get(k, 0) + v

    # ── Resumo Final ──────────────────────────────────────────
    print("=" * 60)
    total = sum(counts_total.values())
    ok_pct = int((counts_total.get("OK", 0) / max(total, 1)) * 100)

    if counts_total.get("ERR", 0) > 0:
        status_icon = S_ERR
        status_text = "FALHAS DETECTADAS"
    elif counts_total.get("WARN", 0) > 0:
        status_icon = S_WARN
        status_text = "AVISOS PENDENTES"
    else:
        status_icon = S_OK
        status_text = "SISTEMA SAUDÁVEL"

    print(f"  {status_icon} {status_text} — {ok_pct}% OK ({counts_total.get('OK',0)}/{total})")
    print(f"  {S_OK} {counts_total.get('OK',0)}  {S_WARN} {counts_total.get('WARN',0)}  {S_ERR} {counts_total.get('ERR',0)}")
    print("=" * 60)

    # ── Salvar Relatórios (Dual Format) ───────────────────────
    os.makedirs(MEMORY_DIR, exist_ok=True)

    # Relatório para IA (minificado)
    ai_report = generate_ai_report(all_results)
    ai_path = os.path.join(MEMORY_DIR, "HEALTH_REPORT.min.txt")
    with open(ai_path, "w", encoding="utf-8") as f:
        f.write(ai_report)

    # Relatório para Humano (legível)
    human_report = generate_human_report(all_results, counts_total)
    human_path = os.path.join(MEMORY_DIR, "HEALTH_REPORT.human.md")
    with open(human_path, "w", encoding="utf-8") as f:
        f.write(human_report)

    print(f"\n  {S_INFO} Relatórios salvos:")
    print(f"     Humano: {human_path}")
    print(f"     IA:     {ai_path}")
    print()

    # Retorna código de saída baseado em erros
    sys.exit(1 if counts_total.get("ERR", 0) > 0 else 0)

if __name__ == "__main__":
    main()
