# Tarefa: Auditoria de Exportação de CSV (Respostas Faltantes)

## Objetivo
Auditar a funcionalidade de exportação de CSV para identificar e corrigir o motivo de as respostas não serem incluídas no arquivo gerado.

## Estado Atual
- Rota identificada: `/processo/<int:id>/exportar_csv` em `routes/api_dossie.py`.
- Problema reportado: CSV gerado sem as respostas do formulário.
- Contexto: Pode haver relação com processos migrados ou mudanças na arquitetura de perguntas dinâmicas.

## Arquivos Envolvidos
- `routes/api_dossie.py` (Backend de exportação)
- `templates/dossie_eletronico.html` (Frontend disparador)
- Tabelas de banco de dados: `respostas_dinamicas`, `perguntas_dinamicas`, `processos_migrados`.

## Etapas
1. [ ] Analisar a lógica de `exportar_csv` em `api_dossie.py`.
2. [ ] Verificar se as consultas SQL estão buscando as respostas corretamente.
3. [ ] Validar a compatibilidade com processos migrados (uso do `legacy-data-mapper` se necessário).
4. [ ] Testar a geração do CSV com dados de exemplo.
5. [ ] Garantir que o botão de download apareça em todos os casos (Pilar de visibilidade).

## Análises Técnicas
- (Aguardando análise inicial de `api_dossie.py`)
