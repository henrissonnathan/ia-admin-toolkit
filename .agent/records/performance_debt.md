# RELATÓRIO DE DÍVIDA TÉCNICA DE PERFORMANCE (DB-MAX)

Este documento lista as violações encontradas durante a auditoria inicial da Skill **DB-MAX** e as recomendações de refatoração para garantir a escalabilidade do sistema.

## 1. Consultas em Loop (Violação da Regra 1)

### [CRÍTICO] `acoes/gerenciar_regras/buscar_regras.php`

- **Problema:** O arquivo realiza uma consulta à tabela `condicoes_de_regra` dentro de um `foreach` que percorre as regras.
- **Impacto:** Se uma pergunta tiver 50 regras, serão feitas 51 consultas ao banco (1 para as regras + 50 para as condições).
- **Refatoração Necessária:** Utilizar um `JOIN` ou uma cláusula `IN` para buscar todas as condições de todas as regras em uma única query e agrupar no PHP.

---

## 2. Ausência de Transacionalidade (Violação da Regra 5)

### [MÉDIO] `acoes/objetos_resumidos/salvar.php`

- **Problema:** Realiza operações de alteração de esquema (`ALTER TABLE`) e inserção/atualização de dados sem um bloco `beginTransaction()` / `commit()`.
- **Impacto:** Em caso de erro na metade do processo, o banco pode ficar em um estado inconsistente ou com alterações de esquema aplicadas mas sem os dados correspondentes.
- **Refatoração Necessária:** Envolver a lógica de salvamento em uma transação PDO.

---

## 3. Configuração de Conexão (Violação da Regra 4)

### [BAIXO] `configs/conexao.php`

- **Problema:** A conversão de `localhost` para `127.0.0.1` está condicionada apenas ao sistema operacional Windows.
- **Impacto:** Latência de resolução de DNS IPv6 em sistemas Linux mal configurados.
- **Refatoração Necessária:** Tornar a substituição de `localhost` por `127.0.0.1` universal no arquivo de conexão.

---

## 4. Listagens Massivas (Violação da Regra 3)

### [ALERTA] Verificação Geral de DataTables

- **Problema:** Diversas listagens no sistema (como em `gerenciar_perguntas/` e `relatorios/`) precisam ser auditadas para garantir o uso de `serverSide: true`.
- **Impacto:** Carregamento de milhares de registros diretamente no DOM do navegador, causando travamentos (browser freeze).
- **Refatoração Necessária:** Implementar processamento no lado do servidor com `LIMIT` e `OFFSET` em todas as tabelas de dados.

---

**Status da Auditoria:** Inicial Concluída.
**Data:** 2026-04-23
