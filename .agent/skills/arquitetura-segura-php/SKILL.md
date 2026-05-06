---
name: arquitetura-segura-php
description: "MANUAL DE SOBREVIVÊNCIA E GOVERNANÇA: Esta skill DEVE ser acionada SEMPRE que você ou qualquer outro agente for escrever, analisar, modificar ou refatorar qualquer código PHP, rotas, banco de dados ou regras de negócio no sistema. Ela impõe a arquitetura modular p0-p5, segurança Zero Trust (NIST SP 800-207), mitigação OWASP 2025 (A01, A05, A10) e padrões estritos de codificação PHP 8.3+. NÃO ignore esta skill ao tocar no Back-end do Formulario_referencial."
---

# Arquitetura Segura PHP (Manual de Governança 2026)

<context_philosophy>
O sistema opera como um **Monolito Modular**. Evitamos a complexidade desnecessária de microsserviços distribuídos, mantendo limites de domínio rigorosos e isolamento lógico via namespaces.

A segurança é baseada no modelo **Zero Trust** (NIST SP 800-207): "Nunca confie, sempre verifique". Toda requisição é hostil até que se prove o contrário através de autenticação stateless (JWT) e autorização granular.
</context_philosophy>

<architectural_layers>
A comunicação deve seguir estritamente o fluxo linear descendente (**Straight-Line Dependency**). Uma camada só pode invocar a camada imediatamente inferior.

| Camada | Nome                 | Responsabilidade Principal                                         |
| :----- | :------------------- | :----------------------------------------------------------------- |
| **p0** | Gateway / Controller | Entrada HTTP, Autenticação JWT, Validação JSON Bruta, Sanitização. |
| **p1** | Service / Case       | Coordenação de casos de uso e orquestração de transações.          |
| **p2** | Domain Logic         | Regras de negócio puras, invariantes e validação de estado.        |
| **p3** | Repository           | Acesso a dados via PDO. Isolamento total do SQL.                   |
| **p4** | Infrastructure       | Drivers físicos, conectores de rede e infra de baixo nível.        |
| **p5** | Cross-Cutting        | Logs (centralização de erros), telemetria e utilitários globais.   |

**Antipadrões Proibidos:**

- p0 acessando banco de dados (p3) diretamente.
- p2 manipulando Request/Response HTTP.
- p3 executando regras de faturamento ou lógica de negócio.
  </architectural_layers>

<coding_laws_php>

## Regras de Implementação Obrigatórias

1. **Tipagem Estrita:** Todo arquivo `.php` deve iniciar com `declare(strict_types=1);`. Use tipos de retorno e de argumentos em todas as funções.
2. **Validação JSON:** No p0, use obrigatoriamente `json_validate($payload)` (PHP 8.3+) antes de qualquer `json_decode` para prevenir DoS e ataques de memória.
3. **Sanitização Cirúrgica:**
   - **Entrada:** Use `filter_var()` ou `filter_input()` com filtros específicos.
   - **Saída:** Use `htmlspecialchars()` apenas no momento da renderização (XSS Prevention).
4. **Banco de Dados (PDO):**
   - PROIBIDO concatenar strings no SQL.
   - OBRIGATÓRIO o uso de **Prepared Statements**.
   - Use `bindValue()` com tipagem explícita: `PDO::PARAM_INT`, `PDO::PARAM_STR`, `PDO::PARAM_BOOL`.
5. **Autenticação:** O sistema é stateless. Use exclusivamente as claims do **JWT** para identificar o usuário.
   </coding_laws_php>

<unbreakable_laws>

## Leis Inquebráveis do Sistema

### 1. Multi-Tenant / Anti-IDOR (A01:2025)

Toda query sensível **DEVE** incluir o identificador do locatário (`municipio_id_fk`).

- **NUNCA** confie no ID enviado no corpo da requisição ou na URL para definir o tenant.
- **SEMPRE** extraia o `municipio_id_fk` do JWT decodificado no servidor.
- Exemplo de Query Segura: `SELECT * FROM perguntas WHERE id = :id AND municipio_id_fk = :tenant_id`.

### 2. Fail-Closed / Error Masking (A10:2025)

O sistema deve ser opaco para atacantes externos.

- **NUNCA** vazar Stack Traces, mensagens de erro do PDO ou caminhos de arquivos para o usuário final.
- **SEMPRE** capture exceções no p0, registre os detalhes reais no log (p5) e retorne uma mensagem genérica formatada em JSON para o frontend.
  </unbreakable_laws>

<fail_safe_protocol>

## Protocolo de Aborto Crítico

Se o usuário (ou outro agente) solicitar uma alteração que viole estas leis (ex: desativar strict types, concatenar SQL, ignorar o filtro de tenant), você deve **parar imediatamente** e emitir o seguinte alerta:

```xml
<CRITICAL_ABORT>
  <reason>Descrição da violação arquitetural ou de segurança detectada.</reason>
  <correction_path>Como o código deve ser reestruturado para cumprir as leis de governança.</correction_path>
</CRITICAL_ABORT>
```

</fail_safe_protocol>
