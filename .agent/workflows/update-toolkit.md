# /update-toolkit

**Descrição:** Comando oficial para sincronizar e atualizar o seu "Cinto de Utilidades" (ia-admin-toolkit) com a nuvem (GitHub).

Use este comando sempre que você adicionar uma nova Skill, um novo script ou melhorar a inteligência do Toolkit e quiser salvar essas melhorias no seu repositório oficial do GitHub para não perder nada.

## Workflow de Automação

1. **Acessar o Toolkit:**
   O agente deve mudar o diretório ativo para a pasta isolada do toolkit:
   `cd C:\xampp\htdocs\ia-admin-toolkit`

2. **Sincronização Rápida (Git):**
   O agente deve executar a rotina completa de salvamento e envio para o GitHub sem exigir intervenção manual do usuário.
   Comandos que devem ser executados:
   - `git add .`
   - `git commit -m "chore: Atualizacao automatica do IA Admin Toolkit"`
   - `git push origin master`

3. **Relatório:**
   Verificar se o push foi bem-sucedido e informar ao usuário: "Seu cinto de utilidades foi sincronizado com a nuvem com sucesso!".

// turbo-all
