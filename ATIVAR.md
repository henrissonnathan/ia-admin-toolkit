# 🚀 Mensagem de Ativação do Toolkit

Cole **UMA** destas mensagens no início de qualquer chat novo com a IA para ativar todas as regras automaticamente.

---

## Versão Completa (Recomendada para primeiro uso)

```
Leia estritamente o arquivo ./.agent/AI_CORE.min.txt.
Estas são suas regras obrigatórias para esta sessão.
Depois execute: py ./.agent/scripts/health_check.py --project-path "."
Mostre o resultado resumido do health check.
A partir de agora, siga as regras do AI_CORE.min.txt em TODAS as suas respostas.
```

## Versão Curta (Para chats rápidos)

```
Leia o arquivo ./.agent/AI_CORE.min.txt e siga estritamente. Ative o Protocolo Nexus. (Se for um chat de continuação, leia o HISTORY.min.log e CONTEXT_MAP.min.txt para restaurar nosso contexto).
```

## Versão para Continuar (Novo Chat no mesmo projeto)

```text
Regras: ./.agent/AI_CORE.min.txt
Comando: Execute a regra 16 (RESUME) lendo o HISTORY.min.log e CONTEXT_MAP.min.txt para recuperar o contexto de onde paramos.
```

## Versão para Outro PC (Caminho genérico)

```
Leia o AI_CORE.min.txt do repositório ia-admin-toolkit e siga estritamente todas as regras.
Rode o health_check.py para verificar o estado do sistema.
```

---

## O que acontece quando a IA recebe esta mensagem?

1. ✅ Ela lê as 14 regras (~100 tokens)
2. ✅ Ela roda o health check e mostra o diagnóstico
3. ✅ Ela passa a seguir TODAS as regras: Plano Primeiro, Risco, Anti-Renomeação, Economia
4. ✅ Ela responde de forma curta e econômica
5. ✅ Ela consulta o Cofre de Erros antes de consertar qualquer coisa
6. ✅ Ela salva ideias no Cofre sem executá-las

---

## ⌨️ Comandos Rápidos (Durante o Chat)
Depois que o Toolkit estiver ativo, você pode digitar estes atalhos a qualquer momento:

* **`L.cmd`** ou **`L.ajuda`** ➔ Mostra a lista de atalhos.
* **`L.lista`** ➔ A IA lista todas as ideias pendentes que ela guardou no Cofre.
* **`L.aprovar [ID]`** ➔ Manda a IA executar a ideia especificada (ex: *L.aprovar ID-002*).
* **`L.combo [ID-1, ID-2]`** ➔ Aprova e planeja múltiplas ideias numa tacada só.
* **`L.limpo`** ➔ A IA faz a faxina e apaga erros velhos/inválidos do Cofre de Erros.
* **`L.mapa`** ➔ Força a IA a escanear a arquitetura e atualizar o mapa de contexto minificado.
* **`L.evoluir [skill]`** ➔ A IA auto-atualiza a documentação da skill com novos padrões.
* **`L.zip`** ➔ Compacta o histórico (Ocorre automaticamente se o arquivo ficar muito grande).
