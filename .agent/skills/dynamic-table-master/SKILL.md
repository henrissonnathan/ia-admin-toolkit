---
name: dynamic-table-master
description: Módulo Mestre de Governança para Tabelas Dinâmicas (SaaS Multi-Tenant). Esta skill impõe a arquitetura de IDs Estáveis, a separação modular p0-p5 e a integração obrigatória com o motor de mapeamento legado. Utilize-a para qualquer alteração em estruturas relacionais de tabelas ou motores de renderização de itens.
---

# Dynamic Table Master: Protocolo de Soberania de Dados (2026)

Esta skill define a lei estrutural para o gerenciamento de tabelas dinâmicas no projeto `Formulario_referencial`. Ela proíbe abordagens baseadas em "memória de slugs" e estabelece o **ID Numérico Estável** como o único centro de verdade.

## 1. Arquitetura Modular (Hierarquia p0 - p5)

Toda funcionalidade de tabela dinâmica deve ser decomposta conforme as camadas:

- **p0 (Orquestrador/Edge)**: Intercepta a requisição. Valida o `pergunta_id` e o `municipio_id_fk` (via JWT). Invoca `json_validate()` para o payload da estrutura de colunas.
- **p1 (Coordenação)**: Orquestra o UPSERT da estrutura. Se for uma tabela com colunas migradas, aciona o `LegacyDataMapper` para sincronizar estados.
- **p2 (Domínio)**: Garante as invariantes de negócio (ex: "Uma tabela deve ter pelo menos uma coluna", "Fórmulas não podem ter referências circulares").
- **p3 (Persistência)**: Implementa o **UPSERT Resiliente** no `colunas_tabela`.
  - **Proibição**: O uso de `DELETE FROM colunas_tabela WHERE pergunta_id = ?` é terminantemente proibido para atualizações, pois quebra a integridade de dados antigos e fórmulas.
  - **Obrigação**: Use `INSERT INTO ... ON DUPLICATE KEY UPDATE` ou `UPDATE ... WHERE id = :coluna_id`.
- **p4 (Infraestrutura)**: Drivers PDO e gestão de transações atômicas.

## 2. O Protocolo "Stable-Identity" (Imutabilidade de IDs)

Ao lidar com colunas:

1. **O ID é Sagrado**: O campo `id` da tabela `colunas_tabela` é o vinculador de dados. O `slug_coluna` é apenas uma etiqueta volátil.
2. **Renomeação Transparente**: Se um usuário renomear uma coluna de "Qtd" para "Quantidade", o sistema **DEVE** atualizar apenas o `slug_coluna` e o `nome_coluna`. Os dados gravados no banco para aquela coluna (ID 328, por exemplo) permanecem intactos.
3. **Cálculos Estáveis**: Fórmulas de cálculo devem ser persistidas usando IDs envoltos em chaves `{ID}`. Ex: `{328} * {329}`. O frontend traduz para Slugs para visualização, mas a verdade é numérica.

## 3. Autodescoberta via DB (DB-First)

A IA e o Frontend **NUNCA** devem assumir que conhecem a estrutura de uma tabela a partir de arquivos estáticos ou JSONs legados.

- **Protocolo**: Antes de qualquer renderização ou salvamento, o sistema deve invocar `buscar_colunas_tabela.php?pergunta_id=X`.
- **Inteligência**: O `DynamicItemsTableController.js` deve carregar seu estado dinamicamente a partir desta API.

## 4. Integração com Legacy Data Mapper

Para preencher formulários antigos ou importar dados externos:

1. **Deteção de Formato**: Se o payload de dados chegar com chaves alfabéticas (Slugs), o `DataHydrator` aciona o mapeamento.
2. **Dicionário de Tradução**: Traduz `{"qtd_itens": "328"}` baseado no mapeamento salvo para o município/pergunta.
3. **Padrão de Falha Seguro**: Se não houver mapeamento e o ID não for encontrado, o dado deve ser isolado como "Órfão" ou o sistema deve emitir um alerta de inconsistência, mas NUNCA apagar o dado original.

## 5. Gatilho de Verificação (Self-Correction)

Sempre que a IA for modificar uma query SQL que envolva tabelas dinâmicas, ela deve verificar:

- [ ] A query utiliza `municipio_id_fk` no `WHERE`? (Multi-tenancy)
- [ ] A query utiliza Prepared Statements com tipagem PDO? (AppSec)
- [ ] A query preserva os IDs das colunas em vez de dar truncate/reload? (Integridade)

---

> [!CAUTION]
> A violação do princípio de **IDs Estáveis** em favor de Slugs causará falha crítica de hidratação e será rejeitada pelo protocolo de segurança.
