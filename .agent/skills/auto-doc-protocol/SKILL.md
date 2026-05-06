---
name: auto-doc-protocol
description: Protocolo de Auto-Documentação Contínua (AUTO-DOC) para o projeto Formulario_referencial.
---

# Protocolo de Auto-Documentação Contínua (AUTO-DOC)

Este protocolo é OBRIGATÓRIO para garantir que a arquitetura do sistema seja compreensível e evolua junto com o código.

## Regras de Execução

1. **Criação de README_LOCAL.md**: Ao explorar uma nova pasta ou modificar ficheiros em uma pasta existente, verifica se existe um ficheiro `README_LOCAL.md`. Se não existir, deves criá-lo.
2. **Conteúdo Resumido**: O `README_LOCAL.md` deve conter uma explicação EXTREMAMENTE RESUMIDA (máximo 3 a 4 linhas) sobre o propósito e a responsabilidade daquela pasta.
3. **Atualização Dinâmica**: Se a responsabilidade de uma pasta mudar ou se novos módulos forem adicionados, o `README_LOCAL.md` deve ser atualizado para refletir o estado atual.
4. **Padrão de Linguagem**: A documentação deve ser em Português Brasileiro (pt-BR), conforme a preferência do usuário.

## Exemplo de Estrutura

```markdown
# [Nome da Pasta]

Breve descrição da responsabilidade desta pasta (3-4 linhas).
Ex: Esta pasta contém os controladores JavaScript responsáveis pela lógica de visibilidade condicional e validação dinâmica do formulário principal.
```
