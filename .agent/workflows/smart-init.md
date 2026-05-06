# /smart-init

**Descrição:** Protocolo de inicialização inteligente. Sincroniza regras (Pilares) entre o Cinto de Utilidades e o Projeto Local, e cria a estrutura de Memória Privada para economia de tokens.

## Fase 1: Fusão de Pilares (Rule Merge)
1. Ao ser executado, a IA deve ler os arquivos de regras (`GEMINI.md` ou regras soltas) do projeto atual.
2. Em seguida, a IA lê as regras de Governança do `ia-admin-toolkit`.
3. **Análise Crítica:** A IA compara os pilares (ex: P0 a P14). Se o projeto atual tiver regras diferentes ou específicas, a IA **não sobrescreve cegamente**. Ela faz uma **Fusão (Merge)**, adicionando o que falta do toolkit e melhorando o que já existe no projeto, criando um Super-Arquivo de regras.

## Fase 2: Instalação da Memória Local (Token Saver Vault)
1. A IA deve verificar a existência da pasta `.agent/memory/` na raiz do projeto.
2. Se não existir, a IA cria a pasta e garante que a regra `.agent/memory/` seja adicionada ao arquivo `.gitignore` do projeto principal.
3. **O cofre é isolado:** Esta pasta NUNCA vai para o GitHub do cliente. É uma memória exclusiva local.

## Fase 3: Mapeamento Contínuo (Auto-Tracker)
1. A partir deste momento, **cada ação, script ou alteração** feita pela IA deve ser resumida em 2 linhas e salva no arquivo `.agent/memory/HISTORY.json` ou `.md`.
2. Quando uma nova conversa começar, a IA deve **ler SOMENTE o arquivo de memória** para se contextualizar. Isso elimina a necessidade de ler arquivos de código enormes, poupando milhares de tokens.

// turbo-all
