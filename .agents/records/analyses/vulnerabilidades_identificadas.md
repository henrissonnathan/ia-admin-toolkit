# Relatório de Vulnerabilidades e Stress Test - Tabelas Dinâmicas

**Skill Ativada:** PROTOCOLO DE INTEGRIDADE TOTAL
**Localização:** `.agents/records/analyses/vulnerabilidades_identificadas.md`

Este documento contém o resultado do Stress Test de QA e Segurança realizado no fluxo de Tabelas Dinâmicas do sistema. As falhas estão ordenadas por risco e incluem as correções sugeridas/aplicadas.

## 1. Auditoria de Sanitização e Segurança (Backend)

- **Risco Crítico (Corrigido): XSS Stored via JSON Payload**
  - **Falha:** O backend no arquivo `salvar.php` recebia os dados em formato de array, filtrava os vazios, mas em seguida fazia um `json_encode` direto dos valores e salvava via PDO. Se o usuário injetasse um `<script>alert(1)</script>` no texto de uma descrição, o HTML era salvo puro no banco.
  - **Correção DB-MAX:** Adicionada rotina de sanitização forçada na variável `$itensValidos` utilizando `htmlspecialchars(strip_tags($value), ENT_QUOTES, 'UTF-8')` recursivamente em todos os nós do array antes do `json_encode()`.
- **Risco Médio: Sanitização Estrita de Tipos no Banco**
  - **Falha:** O sistema confia no valor flutuante enviado pelo frontend (`replace(",", ".")`) para os campos monetários, mas o payload aceita string ("Gratis").
  - **Comportamento Atual:** O banco de dados (se for DECIMAL ou JSON sem cast em query relacional) vai ignorar ou causar um erro silencioso na geração posterior de relatórios, não quebrando a inserção em si (pois é salvo como JSON text na tabela `respostas_dinamicas`), mas podendo quebrar lógicas matemáticas do backend que não fazem cast explícito depois.
- **Risco Baixo: SQL Injection**
  - **Auditoria:** O sistema **ESTÁ SEGURO** e não sofre dessa vulnerabilidade. O uso de Prepared Statements PDO (`$stmtResposta->execute([$registroIdInterno, $perguntaId, $respostaJson])`) previne completamente injeções no banco.

## 2. Teste de Resiliência da Interface (UI)

- **Risco Baixo: Race Conditions (Duplicação de Requests)**
  - **Auditoria:** O sistema **ESTÁ SEGURO**. O arquivo `handleFormSubmit.js` aplica imediatamente `btnEnviar.prop("disabled", true)` com loader assim que disparada a intenção de salvar. Além disso, existe um `AbortController` com timeout de 30 segundos. Se o utilizador clicar rápido demais, o botão já estará bloqueado.
- **Risco Baixo/Médio: Cálculos de Precisão (Ponto Flutuante)**
  - **Falha:** O Javascript possui bugs clássicos com flutuantes (ex: `0.1 + 0.2`).
  - **Auditoria:** Foi verificado no frontend que a lógica do `row-renderer.js` e os cálculos da calculadora fazem a aproximação correta usando precisão explícita baseada nas `casas_decimais` da configuração, além do uso de `.toFixed(precisao)`. Não foram detectadas inconsistências crassas na formatação.

## 3. Validação de Casos de Borda (Edge Cases)

- **Salvar Tabela com 0 Linhas (Empty State):**
  - **Comportamento:** O frontend filtra linhas vazias. Se o array resultante for `[]`, o backend (no `salvar.php`) lida perfeitamente: salva `json_encode([])` forçando uma resposta vazia, e não dá crash nem deixa resquícios (linhas fantasmas antigas reaparecerem).
- **Salvar Linha com Apenas Espaços em Branco:**
  - **Comportamento:** O backend varre o array verificando `trim($val) !== ''`. Linhas preenchidas apenas com espaços são descartadas e não poluem o banco de dados.
- **Importar Excel com Colunas Trocadas:**
  - **Comportamento:** O script `setupFileImportListeners.js` possui um sistema de mapeamento heurístico (string matching). Se não encontrar 70% de similaridade no "Best Match", não importa o valor e ignora. Se a estrutura for fundamentalmente diferente, o usuário tem de ajustar no modal de importação.
- **Queda de Conexão no Meio do Envio JSON:**
  - **Comportamento:** Há um `AbortController` configurado no `fetch` da requisição com timeout de 30.000ms. Se o Request não receber resposta de sucesso da base de dados, a UI dispara um catch e reabre a possibilidade de edição, evitando perda total da sessão, e sugere ao usuário que pode "Salvar Rascunho" se a internet estiver instável.
