---
name: cadastros-informativos
description: "Governança e padrões do módulo de Cadastros Informativos do FORMULARIO_REFERENCIAL. Acione esta skill OBRIGATORIAMENTE sempre que for criar, modificar, corrigir ou refatorar qualquer arquivo PHP, JS ou SQL relacionado a cadastros informativos, campos dinâmicos de cadastro, opções de campo, dados salvos por entidade/município, e formulários de preenchimento de informações. Inclui: CRUD de modelos de cadastro, gerenciamento de campos, renderização de formulários dinâmicos, salvamento de dados, exportação Excel, e regras condicionais. Use PROATIVAMENTE mesmo quando o usuário mencionar apenas 'cadastro', 'informativo', 'campos do cadastro', 'formulário de informações' ou 'dados municipais'."
---

# Cadastros Informativos — Skill de Governança

> **Autoridade:** Esta skill governa TODO o módulo de Cadastros Informativos do sistema Formulário Referencial.
> Qualquer alteração em arquivos deste módulo DEVE respeitar as regras aqui documentadas.

---

## 1. Visão Geral da Arquitetura

O módulo de Cadastros Informativos é um sistema de **formulários dinâmicos** que permite ao Admin criar modelos de cadastro com campos configuráveis, que são preenchidos pelos municípios (clientes).

### Fluxo de Dados

```
[Admin cria modelo] → [Admin adiciona campos] → [Município preenche dados] → [Admin visualiza/exporta]
```

### Camadas do Módulo

| Camada | Função | Arquivos |
|--------|--------|----------|
| **Gerenciamento (Admin)** | CRUD de modelos e campos | `acoes/gerenciar_cadastros_info/`, `acoes/gerenciar_campos_cadastro_info/` |
| **Preenchimento (Cliente/Admin)** | Formulário dinâmico + salvamento | `acoes/cadastro_informativo/`, `public_html/js/cadastro-info/` |
| **Páginas** | Views PHP renderizadas pelo servidor | `paginas/gerenciar_cadastros_info.php`, `paginas/cadastro_informativo.php`, `paginas/listar_cadastros_informativos.php` |

---

## 2. Estrutura do Banco de Dados

### Tabelas Principais

```
cadastros_informativos          → Modelos de cadastro (nome, visibilidade, status)
cadastros_informativos_campos   → Campos de cada modelo (label, tipo, ordem, status)
cadastros_informativos_opcoes   → Opções para campos do tipo select/box
cadastros_informativos_dados    → Dados preenchidos (id_cadastro, id_campo, id_entidade_alvo, valor)
```

### Tabelas Auxiliares (podem não existir no BD local)

```
regras_condicionais_cad_info    → Regras de visibilidade condicional entre campos
condicoes_de_regra_cad_info     → Condições de cada regra
```

> [!WARNING]
> As tabelas auxiliares de regras existem no servidor de produção mas podem NÃO existir no BD local de desenvolvimento. TODO código que referencia essas tabelas DEVE usar `try/catch` com fallback para array vazio.

### Chave Única de Dados

A tabela `cadastros_informativos_dados` usa a combinação `(id_cadastro_info, id_entidade_alvo, id_campo)` como chave composta, permitindo `ON DUPLICATE KEY UPDATE` para upsert.

---

## 3. Tipos de Campo Suportados

| Tipo (tipo_campo) | Descrição | Renderização JS |
|-------------------|-----------|-----------------|
| `texto` | Input text simples | `<input type="text">` |
| `numero` | Input numérico | `<input type="number">` |
| `area_texto` | Textarea multilinha | `<textarea>` |
| `data` | Seletor de data | `<input type="date">` |
| `caixa_selecao_unica` | Dropdown select | `<select>` |
| `caixa_box_unica` | Radio visual (boxes clicáveis) | `div.opcao-box[role="radio"]` |
| `caixa_box_multipla` | Checkbox visual (multi-select boxes) | `div.opcao-box[role="checkbox"]` |
| `caixa_selecao_multipla` | Multi-select (hidden inputs) | `div.opcoes-box-container.multi-select` |
| `card_dinamico` | Sub-formulário com campos aninhados | Campos gerados via `config_campos_card` (JSON) |

### Regra de Serialização

- **Campos simples**: valor como string
- **Campos multi-select**: `JSON array` (ex: `["valor1","valor2"]`)
- **Campos card_dinamico**: `JSON object` (ex: `{"sub_campo_id": "valor"}`)

---

## 4. Endpoints da API (Backend PHP)

### 4.1 Gerenciamento de Modelos (`acoes/gerenciar_cadastros_info/`)

| Arquivo | Método | Função |
|---------|--------|--------|
| `listar.php` | GET | Lista modelos de cadastro |
| `salvar.php` | POST | Cria/atualiza modelo |
| `buscar.php` | GET | Busca modelo por ID |
| `excluir.php` | POST | Exclui modelo (soft delete) |

### 4.2 Gerenciamento de Campos (`acoes/gerenciar_campos_cadastro_info/`)

| Arquivo | Método | Função |
|---------|--------|--------|
| `listar.php` | GET | Lista campos de um modelo |
| `salvar.php` | POST | Cria/atualiza campo |
| `buscar.php` | GET | Busca campo por ID |
| `excluir.php` | POST | Exclui campo |
| `reordenar.php` | POST | Reordena campos (drag & drop) |
| `duplicar.php` | POST | Duplica campo |

### 4.3 Preenchimento e Consulta (`acoes/cadastro_informativo/`)

| Arquivo | Método | Função |
|---------|--------|--------|
| `carregar_estrutura.php` | GET | Retorna campos + opções + dados salvos + regras |
| `carregar_formulario.php` | GET | Retorna campos simplificado (sem regras) |
| `salvar_dados.php` | POST | Salva respostas do formulário |
| `listar_municipios.php` | GET | Lista municípios para o seletor Admin |
| `listar_alvos.php` | GET | Lista entidades alvo |
| `exportar_excel.php` | GET | Exporta dados para Excel |

---

## 5. Frontend Modular (`public_html/js/cadastro-info/`)

### Arquitetura de Módulos JS

```
cadastro-info/
├── main.js     → Controlador central (DOMContentLoaded, inicialização)
├── ui.js       → Renderização de campos (renderizarFormulario, criarElementoCampo)
└── events.js   → Event handlers (submit, option boxes, export)
```

### Dependência Crítica

```javascript
import { apiCall } from "../utils/api.js";
```

O módulo depende do utilitário central `api.js` para todas as chamadas HTTP. O `apiCall` pode enviar dados como JSON ou FormData — o backend DEVE aceitar ambos os formatos.

---

## 6. Leis Técnicas Invioláveis

### LEI 1: Padrão de Resposta JSON

**TODO endpoint PHP** deste módulo DEVE retornar:

```json
// Sucesso
{ "status": "s", "message": "...", "data": {...} }

// Erro
{ "status": "n", "message": "Descrição do erro" }
```

O JS verifica `response.success === true || response.status === 's'` (dupla compatibilidade). Endpoints novos DEVEM usar `"status": "s"`.

### LEI 2: Blindagem de Output

Todo endpoint DEVE iniciar com:

```php
@ini_set('display_errors', 0);
ob_start();
// ... lógica ...
if (ob_get_length()) ob_end_clean();
header('Content-Type: application/json; charset=utf-8');
echo json_encode($response);
exit;
```

Isso garante que warnings/notices do PHP não corrompam o JSON.

### LEI 3: Fallback de Input

Todo endpoint POST DEVE aceitar tanto `$_POST` quanto `php://input` (JSON body):

```php
$dados = $_POST;
if (empty($dados)) {
    $jsonInput = json_decode(file_get_contents('php://input'), true);
    if (is_array($jsonInput)) $dados = $jsonInput;
}
```

### LEI 4: Resiliência de Tabelas Auxiliares

Queries em tabelas que podem não existir no BD local (`regras_condicionais_cad_info`, `condicoes_de_regra_cad_info`) DEVEM estar dentro de `try/catch (PDOException)` com fallback para array vazio.

### LEI 5: Handler Padronizado

Usar SEMPRE o formato array de arrays para `inicializar_handler`:

```php
// ✅ CORRETO
$handler = inicializar_handler([['status' => 'admin', 'nivel' => 1]], 'GET', false);

// ❌ ERRADO (formato antigo)
$handler = inicializar_handler(['admin'], 'GET', false);
```

### LEI 6: Sem Arquivos Duplicados

A pasta `acoes/gerenciar_cadastros_info/` usa APENAS:
- `salvar.php` (NÃO `salvar_cadastro.php`)
- `listar.php` (NÃO `listar_cadastros.php`)
- `buscar.php` (NÃO `buscar_cadastro.php`)
- `excluir.php` (NÃO `excluir_cadastro.php`)

Nunca recriar os sufixados `_cadastro.php`.

---

## 7. Checklist de Alteração

Antes de modificar qualquer arquivo deste módulo:

- [ ] Verifiquei qual endpoint o JS chama (conferir `main.js` e `events.js`)
- [ ] A resposta JSON usa `"status": "s"` / `"status": "n"`
- [ ] O endpoint tem `ob_start()` + `ob_end_clean()` antes do `echo json_encode`
- [ ] O endpoint POST aceita tanto `$_POST` quanto `php://input`
- [ ] Queries em tabelas auxiliares estão em `try/catch`
- [ ] O `inicializar_handler` usa formato `[['status' => '...', 'nivel' => N]]`
- [ ] Não criei arquivo duplicado com sufixo `_cadastro`

---

## 8. Erros Conhecidos e Soluções

| Erro | Causa | Solução |
|------|-------|---------|
| "Dados não salvos" silenciosamente | apiCall envia JSON, `$_POST` fica vazio | Implementar fallback `php://input` (LEI 3) |
| Crash 500 ao carregar formulário | Tabela `regras_condicionais_cad_info` inexistente no BD local | Envolver em `try/catch` (LEI 4) |
| "Permissão negada" inesperada | Handler com formato de array incompatível | Usar formato padronizado (LEI 5) |
| JS mostra "Erro ao salvar" mesmo salvando | Backend retorna `success: true` mas JS espera `status: 's'` | Padronizar resposta (LEI 1) |
