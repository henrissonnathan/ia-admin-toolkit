# 🛡️ IA Admin Toolkit

**Cinto de Utilidades para Desenvolvimento com IA** — Governança, Economia de Tokens, Auto-Cura e Diagnóstico.

Este repositório é o **centro de controle** para projetos que utilizam IA (Claude, GPT, Gemini) como assistente de desenvolvimento. Ele garante que a IA trabalhe de forma **segura, econômica e previsível**, sem inventar código, sem apagar coisas e sem gastar tokens desnecessários.

---

## ⚡ Início Rápido (1 minuto)

### 1. Clone o repositório
```bash
git clone https://github.com/henrissonnathan/ia-admin-toolkit.git
```

### 2. Ative no seu chat de IA
Copie e cole esta mensagem no início de qualquer chat com a IA:

```
Leia o arquivo ./.agent/AI_CORE.min.txt e siga estritamente todas as regras. 
Depois rode: py ./.agent/scripts/health_check.py
Reporte o resultado.
```

### Alternativa: Agente Autônomo (Zero-Setup)
Se a IA possuir terminal e Git (como o Antigravity), você não precisa clonar manualmente. Apenas cole:

```text
Ative suas regras de segurança. Para isso:
1. Clone o repositório 'https://github.com/henrissonnathan/ia-admin-toolkit.git' para uma pasta temp.
2. Mescle (merge) a pasta `.agent` baixada com a pasta `.agent` (ou `.agents`) do meu projeto atual. NUNCA delete ou sobrescreva arquivos que já existem no meu projeto, apenas adicione os novos do toolkit.
3. Apague a pasta temp.
4. Leia ./.agent/AI_CORE.min.txt e aplique as regras estritamente.
5. Execute `py ./.agent/scripts/health_check.py --project-path "."` para validar.
```

**Pronto.** A IA agora está configurada com todas as regras de segurança e economia.

---

## 📦 O que este toolkit faz?

| Funcionalidade | Descrição |
|----------------|-----------|
| **Plano Primeiro** | A IA nunca modifica código sem apresentar um plano e esperar sua autorização |
| **Avaliação de Risco** | Antes de tocar num arquivo, a IA avalia se é Risco Baixo ou Alto |
| **Cofre de Erros** | Todos os erros resolvidos ficam catalogados para a IA nunca repetir o mesmo erro |
| **Cofre de Ideias** | A IA guarda ideias sem executá-las. Você decide o que fazer |
| **Economia de Tokens** | Regras minificadas que a IA lê em ~100 tokens (vs ~1500 no formato normal) |
| **Auto-Resume** | Ao iniciar novo chat, a IA lê o histórico e o mapa de contexto para lembrar onde parou |
| **Lazy Loading** | A IA lê apenas o `.min.txt` da skill necessária, nunca o diretório inteiro |
| **Formato Dual** | Todo arquivo existe em 2 versões: `.human.md` (para você) e `.min.txt` (para a IA) |
| **Health Check** | Script Python que verifica se tudo está configurado corretamente |
| **Anti-Renomeação** | A IA não pode renomear variáveis ou funções sem sua permissão |
| **Proteção de Código** | A IA não pode apagar código antigo sem autorização expressa |
| **Memória Segura** | Múltiplos chats podem rodar ao mesmo tempo sem corromper dados |

---

## 🗂️ Estrutura do Projeto

```
ia-admin-toolkit/
├── README.md                          ← Você está aqui
├── TRPROC_LAUNCHER.pyw                ← Launcher administrativo (GUI)
│
├── .agent/                            ← Cérebro da IA
│   ├── AI_CORE.min.txt                ← 🤖 Regras para IA (ultra-compacto, ~100 tokens)
│   ├── AI_CORE.human.md               ← 👤 Tradução das regras para humanos
│   │
│   ├── scripts/                       ← Ferramentas executáveis
│   │   └── health_check.py            ← Verificação + Boot Sequence visual
│   │
│   ├── skills/                        ← 22 skills de governança
│   │   ├── skill-heal/                ← 🏥 Auto-Cura (Cofre de Erros, Ideias, Risco)
│   │   │   ├── SKILL.md               ← 👤 Versão humana
│   │   │   └── SKILL.min.txt          ← 🤖 Versão IA
│   │   ├── trproc-context-master/     ← 🗺️ Mapeamento de Contexto
│   │   └── ... (20 skills adicionais)
│   │
│   ├── workflows/                     ← 14 workflows automatizados
│   │   ├── smart-init.md              ← Inicialização automática
│   │   ├── optimize-tokens.md         ← Modo economia
│   │   └── update-toolkit.md          ← Sincronização com GitHub
│   │
│   ├── templates/                     ← Templates de memória (copiados pelo smart-init)
│   │   ├── ERROR_VAULT.md             ← Modelo do cofre de erros
│   │   ├── IDEIAS_SUGERIDAS.md        ← Modelo do cofre de ideias
│   │   ├── HISTORY.min.log            ← Modelo do log de histórico
│   │   └── CONTEXT_MAP.min.txt        ← Modelo do mapa de contexto
│   │
│   ├── memory/                        ← Memória local (gerada pelo health_check)
│   ├── agents/                        ← 20 agentes especialistas
│   ├── rules/                         ← GEMINI.md (regras globais)
│   ├── records/                       ← Análises e tarefas passadas
│   └── patches/                       ← Patches de reversão
│
├── routes/                            ← Rotas Flask (tester)
└── templates/                         ← Templates HTML (dashboard tester)
```

---

## 🔑 Arquivos-Chave (Leia Primeiro)

| Arquivo | Quem Lê | Propósito |
|---------|---------|-----------|
| `AI_CORE.min.txt` | 🤖 IA | As 14 regras que controlam o comportamento da IA. Ultra-compacto. |
| `AI_CORE.human.md` | 👤 Você | Tradução de cada regra para linguagem humana. |
| `skill-heal/SKILL.md` | 👤 Você | Documentação completa do sistema de Auto-Cura. |
| `skill-heal/SKILL.min.txt` | 🤖 IA | Versão compacta que a IA lê gastando mínimo de tokens. |
| `health_check.py` | 👤🤖 Ambos | Script de diagnóstico. Gera relatório dual. |

---

## 📚 Catálogo de Skills (22 no total)

Cada skill tem **2 versões**: `SKILL.md` (👤 para você ler) e `SKILL.min.txt` (🤖 para a IA ler gastando mínimo de tokens).

### 🏗️ Arquitetura & Governança
| Skill | O que faz |
|-------|-----------|
| `arquitetura-formulaio` | Governança p0-p5, Zero Trust, Stable-Identity |
| `arquitetura-formulario-referencial` | Orquestrador de Auto-Cura + Leis Técnicas |
| `arquitetura-segura-php` | Segurança PHP 8.3+, OWASP 2025, PDO tipado |
| `master-architect-orchestrator` | Roteador central: decide qual skill ativar |
| `master-governance-orchestrator` | Guardião da arquitetura + protocolo de cura |

### 📋 Formulários & Tabelas Dinâmicas
| Skill | O que faz |
|-------|-----------|
| `dynamic-table-master` | IDs Estáveis para colunas dinâmicas |
| `dynamic-table-governance` | Engine único para todos os tipos de tabela |
| `dynamic-form-orchestrator` | Ciclo de vida completo do formulário |
| `form-logic-master` | Motor de regras: esconder/mostrar campos |
| `complex-table-protocol` | Importação Excel mestre-detalhe (Lotes/Itens) |
| `new-form-architecture` | Mapeamento Index→Role→ID (importação) |
| `cadastros-informativos` | CRUD de cadastros dinâmicos municipais |
| `legacy-data-mapper` | Ponte slugs legados → IDs estáveis |

### 🛡️ Segurança & Qualidade
| Skill | O que faz |
|-------|-----------|
| `skill-heal` | 🏥 Auto-Cura: Cofre de Erros, Ideias, Risco |
| `system-integrity-tester` | Pentest + Performance + CRUD global |
| `database-performance` | SQL de alta performance (bulk, streaming, SSP) |
| `anti-loop-protocol` | Impede a IA de repetir a mesma ação em loop |

### 📝 Rastreamento & Documentação
| Skill | O que faz |
|-------|-----------|
| `nexus-memory-protocol` | 🧠 Gerencia o Cofre de Erros (purge), Ideias (IDs) e Contexto (shorthand) |
| `agent-tracker` | Rastreia progresso e impede tarefas repetidas |
| `task-analysis-governor` | Histórico de análises por arquivo |
| `auto-doc-protocol` | Cria README_LOCAL.md automático em cada pasta |
| `trproc-context-master` | Mapa de contexto técnico do projeto |

### 🔧 Ferramentas
| Skill | O que faz |
|-------|-----------|
| `trproc-admin-toolkit` | Scripts de diagnóstico (CRUD, AST, Schema) |
| `skill-creator` | Criar e testar novas skills |

---

## 🔄 Como funciona o Sistema Dual-Format?

```
SKILL.md (👤 Humano)              SKILL.min.txt (🤖 IA)
┌─────────────────────┐           ┌─────────────────────┐
│ 232 linhas          │           │ 8 linhas            │
│ Tabelas, exemplos   │    →→→    │ Shorthand compacto  │
│ Explicações claras  │           │ ~50 tokens          │
│ ~1500 tokens        │           │ Mesma informação    │
└─────────────────────┘           └─────────────────────┘
```

**Regra:** A IA sempre lê o `.min.txt` primeiro. Só lê o `.md` se precisar de detalhes específicos.

---

## 🏥 Health Check (Diagnóstico)

Rode a qualquer momento para verificar a saúde do sistema:

```bash
py .agent/scripts/health_check.py
```

Para verificar um projeto específico:
```bash
py .agent/scripts/health_check.py --project-path "C:\caminho\do\projeto"
```

O script gera:
- **Terminal:** Boot sequence visual com ✅ ⚠️ ❌
- **`.agent/memory/HEALTH_REPORT.human.md`** — Relatório legível
- **`.agent/memory/HEALTH_REPORT.min.txt`** — Relatório minificado para IA

---

## 💰 Economia de Tokens

Este toolkit foi projetado para reduzir o gasto de tokens em até **90%**:

| Sem Toolkit | Com Toolkit |
|-------------|-------------|
| IA lê regras completas (~1500 tokens) | IA lê `AI_CORE.min.txt` (~100 tokens) |
| IA explica tudo em texto longo | IA responde em shorthand (`PLN:1.[f]:act`) |
| IA relê arquivos inteiros a cada chat | IA lê mapa de contexto e vai direto ao ponto |
| Erros se repetem entre chats | Cofre de Erros evita retrabalho |

---

## 📜 Licença

Uso interno. Repositório público para sincronização entre máquinas de desenvolvimento.
