---
name: database-performance
description: Protocolo de alta performance SQL (DB-MAX) para garantir que o sistema suporte grandes volumes de dados (1.000 a 1.000.000+ de registros). Ative esta skill sempre que ler ou modificar arquivos PHP em acoes/ ou lógicas de banco de dados em public_html/js/.
---

# SKILL: PROTOCOLO DE ALTA PERFORMANCE SQL (DB-MAX)

**Gatilho de Ativação:** Sempre que leres ou modificares ficheiros PHP em `acoes/` ou lógicas de banco de dados em `public_html/js/`.

**Regras de Ouro de Performance:**

1. **PROIBIÇÃO DE QUERIES EM LOOP:** É estritamente proibido realizar `INSERT` ou `UPDATE` dentro de um `foreach` ou `while`.
   - _Padrão Obrigatório:_ Usa `Bulk Inserts` com `INSERT ... ON DUPLICATE KEY UPDATE` em lotes (chunks) de 1.000 itens.

2. **DATABASE STREAMING:** Para leituras massivas (importação/exportação), nunca carregues o resultado do banco num array gigante.
   - _Padrão Obrigatório:_ Usa `Generators` do PHP (`yield`) e desativa o buffer de query (`MYSQL_ATTR_USE_BUFFERED_QUERY => false`).

3. **LISTAGENS INTELIGENTES (SSP):** Nenhuma tabela com potencial de crescimento pode carregar dados no cliente.
   - _Padrão Obrigatório:_ Toda listagem deve usar `serverSide: true` (DataTables) com `LIMIT` e `OFFSET` direto no SQL.

4. **CONEXÃO RELÂMPAGO:** Garante que o host de conexão seja sempre `127.0.0.1` em vez de `localhost` para evitar latência de DNS IPv6.

5. **TRANSACIONALIDADE:** Operações que envolvam mais de 2 tabelas ou pacotes de dados devem estar dentro de `beginTransaction()` e `commit()`.
