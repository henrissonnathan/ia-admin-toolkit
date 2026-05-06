---
name: complex-table-protocol
description: Protocolo para Importação e Processamento de Tabelas Hierárquicas (Mestre-Detalhe)
---

# COMPLEX TABLE PROTOCOL (Stateful Parsing)

Este protocolo define a arquitetura e as regras de negócio para a extração e consolidação de dados em arquivos (Excel/CSV) que apresentam estruturas hierárquicas, especificamente o padrão **Mestre-Detalhe** (ex: Lotes e Itens).

## 1. O Problema da Tabela Hierárquica

Planilhas geradas por sistemas de cotação ou ERPs frequentemente exportam relatórios onde a informação de agrupamento (o "Lote" ou "Grupo") aparece como um título de seção (Linha Mestre), seguido por uma tabela detalhada com os itens que compõem aquele grupo (Linhas Filhas).

A importação ingênua (row-by-row sem estado) falha nesse cenário, pois as linhas filhas não repetem a informação do grupo ao qual pertencem, resultando na perda da relação hierárquica na tabela de destino.

## 2. Solução: Inteligência de Cabeçalho e Stateful Parsing

O `Formulario_referencial` resolve este problema em duas etapas:

### Fase 1: Detecção de Estrutura (`HeaderIntelligence.js`)

Antes da importação, o sistema analisa uma amostra do arquivo (ex: 50 linhas) utilizando a função `detectTableStructure`.

- **Heurística Mestre:** O sistema procura linhas isoladas (poucas células preenchidas, tipicamente <= 2) cuja primeira célula contenha palavras-chave indicativas de agrupamento (ex: `LOTE`, `GRUPO`).
- **Bifurcação:** Se um ou mais grupos forem encontrados, o sistema define o `tipoMapeamento` interno como `mae_filha` e aplica um limite mais alto para a tolerância de linhas vazias (para ignorar os vãos entre lotes).

### Fase 2: Stateful Parsing (`TableImporter.js -> _extractComplexData`)

Durante a etapa de transformação (`transformData`), se o tipo de mapeamento for `mae_filha`, o algoritmo de Parsing com Estado é acionado.

- **Rastreamento de Estado:** O sistema varre as linhas. Se detectar uma "Linha Mestre", ele atualiza o `currentStateMestre` (o valor do Lote/Grupo atual) na memória e passa para a próxima linha sem adicioná-la aos resultados finais.
- **Injeção de Contexto:** Ao processar "Linhas Filhas" (que contêm dados ricos como valor, quantidade, etc.), o sistema injeta o `currentStateMestre` na coluna mapeada como `grupo` daquela linha.

## 3. Heurística e Regras Estritas

- **Linhas Mestre Isoladas:** Uma linha é considerada mestre se possuir no máximo 2 células preenchidas e a primeira começar com `lote` ou `grupo` (após normalização).
- **Fallback de Mapeamento:** Se a configuração da tabela do sistema não possuir um papel `grupo`, o sistema fará um _fallback_ seguro `_consolidateMaeFilhaFallback`, baseando a consolidação no `valor_unitario` e buscando na memória a descrição "mais rica".
- **Limpeza de Rodapés:** Durante o parsing em hierarquia, a tolerância de linhas em branco aumenta para `10`, permitindo que o sistema pule espaçamentos longos entre Lotes, parando apenas no verdadeiro fim do arquivo ou ao encontrar _FOOTER_KEYWORDS_.

## 4. Governança e Aplicação

Toda vez que a lógica de importação ou detecção precisar de suporte a novos tipos de relatórios mestre-detalhe, as extensões devem seguir o modelo de Estado estabelecido aqui, nunca forçando o preenchimento retroativo caso o estado puder ser carregado sequencialmente de cima para baixo.
