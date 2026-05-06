# Mapa da Arquitetura Atual (Raio-X do Sistema)

## Árvore de Pastas Principais Analisadas

```text
c:\servidor\htdocs\Formulario_referencial\
├── acoes\
│   ├── api\                # Backend para geração, listagem e revogação de chaves de API
│   ├── ia\                 # Backend de integração com Inteligência Artificial e configurações
│   └── objetos_resumidos\  # Backend do CRUD e regras de negócio para Objetos Resumidos
└── public_html\
    └── js\
        ├── admin_integracao_api\ # Frontend (JS) para a interface de Gerenciamento de API
        ├── formulario\
        │   ├── ia\         # Frontend modularizado para coleta e envio de dados para a IA
        │   └── items\
        │       └── table\  # Scripts de manipulação e extração de dados da Tabela de Itens Dinâmica
        ├── gerenciar_objetos_resumidos\
        │                   # Frontend (DataTables, Modais, AJAX) para gestão dos Objetos
        └── IA\             # Frontend do painel Admin para configurar regras e prompts da IA
```

## Fluxo de Dados e Responsabilidades dos Módulos

### 1. Módulo de Inteligência Artificial (Formulário Dinâmico)

- **Frontend (`js/formulario/ia/`):**
  - **`ia-control.js`:** Atua como o controlador principal da interface. Captura eventos de clique nos botões de IA (`.btn-gerar-ia`), gerencia o estado visual (spinners, botões desabilitados), lida com a resposta do backend e injeta os dados nos inputs ou caixas de seleção.
  - **`ia-data-collector.js`:** Extrai dados do DOM de forma agnóstica. Coleta o contexto global (outras perguntas preenchidas no form), opções do campo atual e itens da tabela ativa (`#tabela-itens`), preparando o payload estruturado.
- **Backend (`acoes/ia/gerar_resposta.php`):**
  - Recebe o Payload JSON. Implementa validação CSRF, Rate Limiting (por sessão) e um sistema de Fila (Queue) usando o banco de dados (`ia_queue`) para evitar concorrência e processos zumbis. Envia a solicitação para o serviço de IA configurado e retorna o texto gerado ou arrays de índices/valores.

### 2. Módulo de Objetos Resumidos

- **Frontend (`js/gerenciar_objetos_resumidos/main.js`):**
  - Inicializa o DataTables para listar os objetos. Intercepta envios de formulário de criação/edição via Modal e envia via `FormData` e `fetch` para o backend. Implementa navegação por abas (status "ativos", "inativos", "sugestoes") alterando a URL da chamada AJAX em tempo de execução.
- **Backend (`acoes/objetos_resumidos/salvar.php` & `buscar.php`):**
  - Gerencia inserção, atualização, ativação e deleção. Possui regras de autorização distintas: Administradores gerenciam status e visibilidade global, enquanto Clientes apenas submetem sugestões atreladas ao seu `municipio_id_fk`.

### 3. Tabela Dinâmica de Itens

- **Frontend (`js/formulario/items/table/getTableDataForSubmission.js`):**
  - Itera sobre as linhas do DOM da `#tabela-itens` (usando jQuery). Extrai valores (unidade, grupo, quantidade, valor unitário, descrição, observação), realiza sanitização (remoção de formatação de moeda R$, conversão para float) e filtra linhas inválidas ou incompletas antes de preparar o array final para a submissão do formulário.

### 4. Módulo de Gerenciamento de API

- **Frontend (`paginas/gerenciar_api.php` e `js/admin_integracao_api/main.js`):**
  - Interface administrativa para criar novas chaves (Cliente ou Admin). Permite ao administrador definir permissões de acesso granulares (por endpoint) e exibe uma tabela de chaves ativas geradas via AJAX. Possui também um guia estático de uso da API RESTful (Bearer Token).
- **Backend (`acoes/api/` - `gerar_chave.php`, `listar_chaves.php`, `excluir_chave.php`):**
  - Responsável por criptografar/armazenar e listar as chaves no banco de dados.
  - _Nota Arquitetural:_ Atualmente a gestão foca-se na emissão e revogação das chaves com escopos de endpoint. A estruturação comercial (planos pagos, limites rígidos de _rate limit_ global por chave e monetização) aparenta estar em fase de concepção/integração, pois o modelo atual é focado no controle de acessos interno.

### 5. Módulo de Configuração Admin IA

- **Frontend (`paginas/IA.php` e `js/IA/`):**
  - Painel onde o administrador seleciona perguntas dinâmicas e parametriza como a IA deve se comportar. Define prompts personalizados, fontes de dados adicionais, respostas fictícias para simulação, seleção de colunas da tabela dinâmica de itens e criação de "Blacklist" de modelos.
- **Backend (`acoes/ia/salvar_config_global.php` e `salvar_pergunta_ia_config.php`):**
  - Armazena as configurações na base de dados (`ia_config` e `ia_perguntas_config`). As chaves de API (Gratuita/Paga) são criptografadas (via função `encrypt_data`) antes de ir para o banco. Permite também configurar o "Fallback" caso um modelo de IA falhe, salvando configurações estruturadas e relacionais (`ia_contexto_pergunta_id_fk`) usando codificação JSON em colunas específicas.

## Gargalos Atuais e Áreas Incompletas

1. **Gargalo de Performance (DataTables Client-Side):**
   - No `js/gerenciar_objetos_resumidos/main.js`, a inicialização do DataTables tem `serverSide: false` com um comentário apontando que o backend não suporta isso ainda. Isso significa que, em bancos de dados grandes, o AJAX carregará milhares de registros na memória do navegador de uma só vez, causando lentidão severa na interface.

2. **Code Smell / Gargalo de Banco de Dados (`salvar.php`):**
   - O arquivo `acoes/objetos_resumidos/salvar.php` executa rotinas de DDL (`SHOW COLUMNS` e `ALTER TABLE`) toda vez que é invocado para verificar/criar a coluna `municipio_id_fk`. Isso consome recursos do banco de dados desnecessariamente em um endpoint de operação de CRUD diário e deve ser movido para scripts de migração/instalação fixos.

3. **Inconsistência de Stack (Vanilla JS vs jQuery):**
   - Enquanto módulos mais novos como os de IA (`ia-control.js`, `ia-data-collector.js`) utilizam Vanilla JS (ES6 Modules) de forma performática e modular, módulos da Tabela de Itens (como `getTableDataForSubmission.js`) ainda dependem fortemente de seletores globais jQuery (`$(row).find()`). Essa mistura aumenta o peso do bundle e a propensão a bugs de concorrência no DOM.

4. **Gerenciamento de Fila de IA:**
   - O `gerar_resposta.php` utiliza tabelas SQL (`ia_queue`) para lock e rate-limiting (incluindo deleção de processos zumbis via `DELETE FROM ... WHERE ...`). Em alto volume de acesso simultâneo, isso causará _table locks_ e contenção no banco relacional. Seria ideal mover para Redis ou Memcached se houver escala.
