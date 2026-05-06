---
name: master-form-skill
description: "Protocolo arquitetônico de vinculação e sincronização estrita de formulários (Excel -> Admin -> Form)."
---

# PROTOCOLO DE SINCRONIZAÇÃO ESTRITA (Admin <-> Formulário)

Este documento define a arquitetura definitiva para a importação de planilhas e a geração de tabelas dinâmicas no projeto `Formulario_referencial`.

## Princípio Fundamental: Ignorar Nomes, Confiar em Papéis (Roles)

Historicamente, as rotinas de importação dependiam fortemente do mapeamento exato dos nomes das colunas contidas nas planilhas de Excel. Esta abordagem provou-se frágil devido às constantes variações de nomenclatura geradas pelos utilizadores (ex: "Produto", "Desc. Lote", "Objeto" para a mesma coisa).

A nova arquitetura **abole o uso de nomes de colunas** como elo de ligação entre o ficheiro importado e a inserção no banco de dados.

O fluxo obedece à seguinte hierarquia estrita de vínculo:

### 1. Detecção Inteligente de Papéis (HeaderIntelligence)

A classe `HeaderIntelligence.js` examina a planilha e atribui **Papéis (Roles)** aos índices das colunas, e não nomes.
Exemplo de Saída:
`{ 0: 'item', 3: 'descricao', 4: 'quantidade' }`

### 2. Vínculo Estrito (Admin Mapping)

O sistema ignora os nomes dos cabeçalhos do Excel (`rowObj['Produto']`). Em vez disso, ele consulta diretamente o Banco de Dados através do objeto `colunas` injetado pelo backend (Gerenciador de Mapeamentos / Admin).

Para cada papel detetado no Passo 1, o sistema procura qual **ID de Campo** detém aquele papel.
Exemplo de Vínculo:

- O Papel `'descricao'` pertence ao Campo ID `3`.
- O Papel `'quantidade'` pertence ao Campo ID `15`.

### 3. Injeção de Precisão (DOM)

Com o mapeamento estrito concluído (`Índice Excel -> Papel -> ID Campo`), a injeção ocorre exclusivamente via seletores de ID:
`tr.querySelector('[data-column-id="3"]')`

### 4. Quebra de Isolamento (Gatilhos / Triggering)

A mera alteração de valor via `.value = val` é insuficiente para componentes reativos.
A arquitetura exige a simulação compósita de interação do utilizador para reativar o `TableCalculator` e as regras de visibilidade:

```javascript
$(input).val(valorLimpo).trigger("input").trigger("change").trigger("keyup");
```

## Diretrizes de Limpeza (Sanitização)

1. **Dizimação da Linha Fantasma**: O método `clearTable(true)` deve ser obrigatoriamente chamado antes de iniciar qualquer injeção, erradicando a linha `ID 0` inicial.
2. **Sanitização Universal Monetária**: Papéis numéricos/monetários (`valor_unitario`, `quantidade`, `valor_total`) são submetidos a uma sanitização bruta que extrai apenas dígitos, vírgulas e pontos, conformando-os ao formato decimal exigido para cálculos algébricos pelo motor do formulário.

---

**AVISO CRÍTICO PARA TODOS OS AGENTES**:
Nunca restaures a lógica baseada em `headName` (nomes de cabeçalho). O mapeamento é, e sempre será, Índice -> Papel -> ID.
