# Task: Organização e Mapeamento da Estrutura do TRPROC

## Objetivo
Analisar a raiz do projeto `TRPROC` e seus subdiretórios para criar um mapa profissional indicando a quais módulos pertencem os arquivos, sua localização exata e se estão no diretório correto. Em seguida, realizar a limpeza e realocação de arquivos avulsos.

## Arquivos Envolvidos
- Raiz do projeto (`c:\Robos\TRPROC\`)
- Arquivos de scripts temporários, logs, backups, e rascunhos.

## Status das Etapas
- [x] Listar diretório raiz
- [x] Analisar e agrupar diretórios por módulo (MVC Python / Legado PHP)
- [x] Identificar arquivos na raiz (Debug, Scratch, Logs, Backups)
- [x] Gerar Mapa Profissional da Arquitetura e Estrutura
- [x] Sugerir realocação de arquivos de debug/scratch para pastas apropriadas
- [x] Executar a faxina da raiz, movendo:
  - Scripts de teste e debug para `scripts/debug/`
  - Scripts de banco de dados para `scripts/database/`
  - Scripts de migração para `scripts/migration/`
  - Scripts utilitários para `scripts/utils/`
  - Logs pesados para `logs/`
  - Backups `.sql` e `.json` para `backups/`
  - Dumps de logs para `scratch/dumps/`
  - Arquivos Rascunhos para `scratch/`
  - Patches para `.agents/patches/`

## Impedimentos
Nenhum. Tarefa concluída com sucesso.
