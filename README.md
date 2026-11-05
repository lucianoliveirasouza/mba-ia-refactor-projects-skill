# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.

---

# Entrega do Desafio — Skill `refactor-arch`

> As seções abaixo foram **acrescentadas** ao enunciado original (que permanece inalterado acima) e documentam a solução entregue.

Foi construída uma skill do **Claude Code** (`.claude/skills/refactor-arch/`) que, em 3 fases sequenciais, **analisa** a stack de um projeto backend, **audita** anti-patterns com severidade e localização exata e, após confirmação humana, **refatora** o projeto para MVC **validando** que a aplicação continua de pé. A mesma skill (sem nenhuma alteração) foi executada nos 3 projetos legados do repositório — dois em Python/Flask e um em Node.js/Express.

| Entregável | Local |
|---|---|
| Skill completa | `code-smells-project/.claude/skills/refactor-arch/` (cópias idênticas em `ecommerce-api-legacy/` e `task-manager-api/`) |
| Código refatorado | `code-smells-project/`, `ecommerce-api-legacy/`, `task-manager-api/` |
| Relatórios de auditoria (saída da Fase 2) | `reports/audit-project-1.md`, `reports/audit-project-2.md`, `reports/audit-project-3.md` |
| Logs completos das execuções | `reports/logs/project-{1,2,3}-phase-{1-2,3}.log` |

---

## A) Análise Manual

Antes de escrever a skill, li integralmente o código dos 3 projetos. Abaixo, os problemas que considerei de maior impacto (severidade segundo a escala do desafio). Esses achados viraram os sinais de detecção do catálogo da skill.

### Projeto 1 — `code-smells-project` (Python/Flask, E-commerce)

| # | Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | CRITICAL | **SQL Injection** — praticamente todas as queries são montadas por concatenação, inclusive o login (`"... WHERE email = '" + email + "' AND senha = '" + senha + "'"`) | `models.py:28, 47-50, 109-111, 289-297` | Permite bypass de login com `' OR '1'='1` e leitura/alteração arbitrária do banco. |
| 2 | CRITICAL | **Endpoint de SQL arbitrário e reset do banco sem autenticação** (`POST /admin/query` executa o SQL do body; `POST /admin/reset-db` apaga tudo) | `app.py:47-78` | Qualquer cliente anônimo destrói ou extrai o banco inteiro. |
| 3 | CRITICAL | **Segredos hardcoded e vazados** — `SECRET_KEY` literal, devolvida também no `/health`; `debug=True` com `host=0.0.0.0` | `app.py:7-8, 88`, `controllers.py:289` | Chave de sessão exposta publicamente e debugger Werkzeug (RCE) acessível na rede. |
| 4 | CRITICAL | **Senhas em texto puro e expostas na API** — seed grava `admin123`; `GET /usuarios` devolve o campo `senha` | `database.py:75-83`, `models.py:83, 99` | Um GET público vaza as credenciais de todos os usuários. |
| 5 | HIGH | **Conexão SQLite global mutável** (`global db_connection`, `check_same_thread=False`) | `database.py:4-11` | Estado compartilhado entre threads; escritas parciais de uma requisição podem ser commitadas por outra. |
| 6 | HIGH | **Regra de negócio no lugar errado** — o "model" calcula faixas de desconto e estoque; o "controller" valida, notifica e faz SQL | `models.py:133-169, 256-262`, `controllers.py:24-62` | Nomes MVC com responsabilidades misturadas: impossível testar regras isoladamente. |
| 7 | MEDIUM | **Queries N+1** na listagem de pedidos (1 query por pedido + 1 por item) | `models.py:187-193, 219-225` | Custo cresce com pedidos × itens. |
| 8 | MEDIUM | **Error handling duplicado** — `except Exception as e: return jsonify({"erro": str(e)}), 500` em todos os handlers | `controllers.py` (16 ocorrências) | Vaza detalhes internos ao cliente e duplica código. |
| 9 | LOW | **Magic numbers** — faixas de desconto `10000/5000/1000` e `0.1/0.05/0.02`, listas de status/categorias inline | `models.py:257-262`, `controllers.py:52, 242` | Regras de negócio escondidas em literais. |
| 10 | LOW | **`print` como logging** e para "simular" e-mail/SMS | `controllers.py:208-210` e outros | Sem níveis, sem controle em produção. |

### Projeto 2 — `ecommerce-api-legacy` (Node.js/Express, LMS com checkout)

| # | Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | CRITICAL | **Credenciais de produção hardcoded** (`dbPass`, `paymentGatewayKey: "pk_live_..."`) | `src/utils.js:1-7` | Quem lê o repositório obtém a chave de pagamento live. |
| 2 | CRITICAL | **Número do cartão e chave do gateway em log** (`console.log(\`Processando cartão ${cc} na chave ${...}\`)`) | `src/AppManager.js:45` | Vazamento de PAN (PCI-DSS) e da chave em qualquer agregador de logs. |
| 3 | CRITICAL | **God Class `AppManager`** — cria o banco, o schema, o seed, registra as rotas e processa pagamento | `src/AppManager.js:4-139` | Viola completamente a separação de responsabilidades. |
| 4 | CRITICAL | **"Criptografia" caseira de senha** (`badCrypto`: base64 truncado, sem salt) e senha padrão `123456` | `src/utils.js:17-23`, `src/AppManager.js:68` | Hash reversível/colidível; contas criadas com senha previsível. |
| 5 | HIGH | **Callback hell sem tratamento de erro** — até 6 níveis, contadores manuais, `err` ignorado | `src/AppManager.js:37-77, 83-128` | Exceções em callbacks derrubam o processo; requisições podem nunca responder. |
| 6 | HIGH | **Checkout sem transação** e `DELETE` de usuário deixando matrículas/pagamentos órfãos (a própria resposta admite "dados sujos") | `src/AppManager.js:50-61, 131-137` | Inconsistência de dados financeiros. |
| 7 | MEDIUM | **N+1 no relatório financeiro** (1 + cursos + 2 × matrículas queries) | `src/AppManager.js:89-106` | Degrada linearmente com o volume. |
| 8 | MEDIUM | **Validação de entrada ausente** — `card` numérico faz `cc.startsWith` lançar TypeError e derrubar o servidor | `src/AppManager.js:29-35, 46` | DoS trivial por payload malformado. |
| 9 | LOW | **Nomenclatura ruim** — `u`, `e`, `p`, `cid`, `cc`, `self`, `badCrypto`, `AppManager` | `src/AppManager.js:29-33` | Nomes não revelam intenção. |
| 10 | LOW | **Código morto / estado global inútil** — `globalCache` só escrito, `totalRevenue` nunca usado | `src/utils.js:9-15, 25` | Vazamento de memória e falsa funcionalidade. |

### Projeto 3 — `task-manager-api` (Python/Flask, Task Manager com camadas parciais)

| # | Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | CRITICAL | **Senhas com MD5 sem salt** | `models/user.py:27-32` | MD5 é quebrável por rainbow tables em segundos. |
| 2 | CRITICAL | **Hash de senha devolvido nas respostas** (`to_dict()` inclui `password`, usado em `POST /users`, `GET /users/<id>` e no `/login`) | `models/user.py:16-25` | Vaza o hash de todos os usuários. |
| 3 | CRITICAL | **Credenciais hardcoded** — `SECRET_KEY`, senha SMTP `senha123` no `NotificationService` | `app.py:13`, `services/notification_service.py:7-10` | Segredos no repositório. |
| 4 | HIGH | **Rotas gordas** — estatísticas, regra de "atrasada" e validações inteiras dentro das rotas; `services/` e `utils/` quase não usados | `routes/report_routes.py:12-101`, `routes/task_routes.py:11-63` | A separação em pastas existe, mas a responsabilidade não. |
| 5 | HIGH | **Token de autenticação falso** (`'fake-jwt-token-' + id`) e qualquer um pode se cadastrar como `admin` | `routes/user_routes.py:52, 210` | Escalonamento de privilégio trivial. |
| 6 | MEDIUM | **N+1** — `User.query.get`/`Category.query.get` por task; contagens por status em N queries | `routes/task_routes.py:41-57`, `routes/report_routes.py:15-28, 53-68` | Muitas queries por requisição. |
| 7 | MEDIUM | **APIs deprecated** — `datetime.utcnow()` (Python ≥ 3.12) e `Model.query.get()` (SQLAlchemy 2.0 legacy) | `models/*.py`, `routes/*.py` | Avisos hoje, quebra em versões futuras. |
| 8 | MEDIUM | **Duplicação** — a regra "overdue" reimplementada em 5 lugares apesar de existir `Task.is_overdue()`; serialização campo a campo repetida | `routes/task_routes.py:30-39, 71-80`, `routes/user_routes.py:171-180` | Mudança de regra exige editar vários arquivos. |
| 9 | LOW | **Imports não usados** (`import os, sys, json, time`, `hashlib`, `re`…) | `app.py:7`, `routes/task_routes.py:7`, `utils/helpers.py:3-7` | Ruído. |
| 10 | LOW | **Condicionais verbosas** (`if ...: return True else: return False`) e magic numbers (prioridade `1..5`, tamanho mínimo `3`, senha `4`) | `models/task.py:38-60`, `models/user.py:34-38` | Legibilidade. |

---

## B) Construção da Skill

### Estrutura

```
.claude/skills/refactor-arch/
├── SKILL.md                          # o "prompt": workflow das 3 fases, regras e formatos de saída
└── references/
    ├── project-analysis.md           # Área 1 — heurísticas de detecção de linguagem/framework/banco/arquitetura
    ├── anti-patterns-catalog.md      # Área 2 — 22 anti-patterns com sinais de detecção e severidade (inclui APIs deprecated)
    ├── audit-report-template.md      # Área 3 — formato padronizado do relatório da Fase 2
    ├── mvc-guidelines.md             # Área 4 — camadas, responsabilidades, direção de dependências, estruturas alvo por stack
    └── refactoring-playbook.md       # Área 5 — 16 padrões de transformação com código antes/depois
```

### Decisões de design

- **SKILL.md como orquestrador, referências como conhecimento.** O `SKILL.md` só define *o que fazer e em que ordem* (fases, gates, formatos de saída); todo o conhecimento de domínio fica nos arquivos de referência, carregados **sob demanda no início de cada fase** (progressive disclosure), o que mantém o contexto enxuto.
- **Gate rígido entre auditoria e refatoração.** A Fase 2 é estritamente somente leitura — **nem o relatório é gravado** antes da resposta `[y/n]`; após a resposta ele é salvo e, se `y`, começa a Fase 3. O caminho do relatório pode ser passado como argumento (`/refactor-arch ../reports/audit-project-1.md`).
- **Evidência obrigatória.** Todo finding precisa de `arquivo:linha` conferido lendo o arquivo; ocorrências da mesma causa são agrupadas em um finding com várias localizações.
- **Validação por baseline.** Antes de editar qualquer arquivo, a Fase 3 sobe a aplicação **original**, chama todos os endpoints do inventário da Fase 1 e guarda status + chaves das respostas. Depois da refatoração repete as chamadas e compara. Isso transforma "os endpoints continuam respondendo" num teste objetivo.
- **Contrato preservado.** Rotas, métodos, nomes de campos, porta e comando de execução são mantidos; a única exceção aceita é correção de segurança (ex.: não devolver hash de senha, exigir token em rota admin), sempre listada na seção *Contract Changes* do resumo final.
- **Sem commits pela skill.** O humano decide o que commitar.

### Anti-patterns do catálogo (e por quê)

| Severidade | Anti-patterns | Motivação |
|---|---|---|
| CRITICAL | AP-01 Segredos hardcoded · AP-02 SQL Injection · AP-03 God Class · AP-04 Endpoint perigoso sem proteção · AP-05 Exposição de dados sensíveis · AP-06 Senha insegura | Os exemplos da própria definição de CRITICAL do desafio, todos presentes nos projetos (SQL livre, `pk_live` em código, cartão em log, MD5). |
| HIGH | AP-07 Fat Controller · AP-08 Estado global · AP-09 Acoplamento sem DI · AP-10 Callback hell · AP-11 Escrita sem transação · AP-12 Config insegura de runtime | Violações de MVC/SOLID que travam teste e manutenção; AP-10 é essencial para cobrir Node. |
| MEDIUM | AP-13 N+1 · AP-14 Validação ausente/duplicada · AP-15 Error handling espalhado · AP-16 Duplicação · **AP-17 APIs deprecated** | Problemas de padronização/performance; AP-17 traz uma tabela *deprecated → moderno* para Python, Flask, SQLAlchemy, Node e Express. |
| LOW | AP-18 Magic numbers · AP-19 Nomenclatura · AP-20 `print` como log · AP-21 Código morto · AP-22 Condicionais verbosas | Legibilidade. |

Cada entrada traz **sinais textuais** (regex para Grep, ex.: `execute\(.*["'] *\+`), **sinais estruturais** (ex.: "query dentro de `for` sobre o resultado de outra query"), **falsos positivos** a descartar (ex.: `.like(f'%{q}%')` do SQLAlchemy é parametrizado) e o **padrão do playbook** que corrige.

### Como a skill ficou agnóstica de tecnologia

- **Detecta, não assume:** a Fase 1 usa tabelas de evidência (manifesto + sinais no código) para Python, Node/TS, Java, Go, Ruby, PHP e C#, e frameworks Flask, Django, FastAPI, Express, NestJS, Fastify, Spring, Gin, Rails, Laravel.
- **Sinais de detecção por conceito**, com variantes por linguagem (ex.: SQL Injection cobre concatenação Python, f-string, template literal JS).
- **Estruturas alvo por stack e por nível de organização:** Flask monolítico (`src/` com camadas), Flask com camadas parciais (evoluir as pastas existentes, criando `controllers/`) e Express (`src/` com `routes/controllers/models/middlewares`).
- **Playbook com exemplos nas duas stacks** e instrução explícita de adaptar ao idioma dos nomes do projeto (ex.: `produto_model.py`).
- **Validação genérica**: o comando de execução e o seed vêm do README/manifesto; a validação usa `curl` sobre o inventário de endpoints, independente do framework.

### Desafios encontrados e como foram resolvidos

| Desafio | Solução |
|---|---|
| "Pedir confirmação antes de modificar qualquer arquivo" conflitava com "salvar o relatório da Fase 2" | A Fase 2 só imprime; o relatório é gravado como primeira ação **após** a resposta do usuário (qualquer que seja). |
| Garantir que "os endpoints continuam respondendo" fosse verificável e não só declarado | Baseline do comportamento original capturada antes de qualquer edição e comparada depois (status + chaves de primeiro nível). |
| Correções de segurança necessariamente mudam respostas (ex.: tirar `senha` do JSON) | Regra explícita de "contrato preservado, exceto segurança", com seção *Contract Changes* obrigatória no resumo final. |
| Rotas destrutivas (`/admin/query`, `DELETE /users`) precisam ser protegidas, mas removê-las quebraria o contrato | Playbook PB-09: manter a rota respondendo, protegida por token de ambiente (401/403 sem credencial). |
| Projeto parcialmente organizado (task-manager) poderia ser "recriado do zero" | Seção específica no guideline: evoluir pastas existentes, extrair regra das rotas para `controllers/`, reaproveitar models/services. |
| `datetime.utcnow()` → `datetime.now(timezone.utc)` quebra comparações com datetimes *naive* gravados no SQLite | Playbook PB-13 recomenda `datetime.now(timezone.utc).replace(tzinfo=None)` para manter compatibilidade. |
| Execução headless (`claude -p`) e a pausa da Fase 2 | Primeira chamada executa Fases 1–2 e para no `[y/n]`; a resposta é enviada com `claude -p --continue "y"`, retomando a mesma sessão. |
| Na primeira execução, a Fase 3 reescreveu frases originais dos READMEs dos projetos ao atualizar instruções | Regra do `SKILL.md` ajustada: README só pode ser alterado **por acréscimo** (seção nova), nunca reescrevendo o conteúdo existente; os READMEs foram restaurados mantendo o texto original. |
| O validador genérico do `skill-creator` rejeitava o campo `argument-hint` | Campo removido do frontmatter (só `name` e `description`), tornando a skill portável; o argumento continua disponível via `$ARGUMENTS`. |

---

## C) Resultados

### Resumo das auditorias (Fase 2)

| Projeto | Stack detectada | CRITICAL | HIGH | MEDIUM | LOW | Total | Relatório |
|---|---|---|---|---|---|---|---|
| 1 — code-smells-project | Python + Flask 3.1.1 | 7 | 4 | 4 | 6 | **21** | [audit-project-1.md](reports/audit-project-1.md) |
| 2 — ecommerce-api-legacy | Node.js + Express 4.22.1 | 5 | 5 | 5 | 4 | **19** | [audit-project-2.md](reports/audit-project-2.md) |
| 3 — task-manager-api | Python + Flask 3.0.0 | 5 | 5 | 6 | 5 | **21** | [audit-project-3.md](reports/audit-project-3.md) |

Critérios de aceite: Fase 1 detectou a stack nos 3/3 · ≥ 5 findings nos 3/3 · ≥ 1 CRITICAL/HIGH nos 3/3 · aplicação funcionando após a refatoração nos 3/3 (detalhes abaixo).

### Antes × depois

#### Projeto 1 — code-smells-project

```
ANTES                                   DEPOIS
code-smells-project/                    code-smells-project/
├── app.py        (rotas + admin SQL)   ├── app.py                    entry point fino (python app.py)
├── controllers.py (292 linhas)         ├── .env.example
├── models.py      (314 linhas)         └── src/
├── database.py    (conexão global)         ├── app.py                composition root: create_app()
└── requirements.txt                        ├── config/settings.py    config via env
                                            ├── constants.py · errors.py
                                            ├── database/             connection (flask.g) · schema (FKs) · seed (hash)
                                            ├── models/               produto · usuario · pedido · sistema (SQL parametrizado)
                                            ├── controllers/          produto · usuario · pedido · relatorio · sistema
                                            ├── services/             notification_service
                                            ├── views/                *_routes.py (Blueprints) + validators
                                            └── middlewares/          error_handler · auth (X-Admin-Token)
```

#### Projeto 2 — ecommerce-api-legacy

```
ANTES                                   DEPOIS
src/                                    src/
├── app.js                              ├── app.js                    composition root (createApp + listen)
├── AppManager.js (God Class)           ├── config/index.js           process.env (+ .env opcional)
└── utils.js (config + cache + hash)    ├── constants/ · errors/AppError.js
                                        ├── database/connection.js    wrapper Promise, transaction(), schema c/ FKs, seed
                                        ├── models/                   user · course · enrollment · payment · auditLog
                                        ├── services/paymentService.js
                                        ├── controllers/              checkout · report · user
                                        ├── validators/               checkout · common
                                        ├── routes/                   checkoutRoutes · adminRoutes · userRoutes
                                        ├── middlewares/              asyncHandler · errorHandler · auth
                                        └── utils/                    logger · password (scrypt)
```

#### Projeto 3 — task-manager-api

Projeto já tinha pastas de camadas — a skill **evoluiu** a estrutura existente em vez de recriá-la:

```
ANTES                                   DEPOIS
task-manager-api/                       task-manager-api/
├── app.py   (config hardcoded,         ├── app.py                    composition root: create_app() (python app.py)
│             create_all no import)     ├── .env.example
├── database.py                         ├── config/settings.py        NOVO — config via env
├── seed.py                             ├── database.py               instância SQLAlchemy
├── models/   (MD5, password no         ├── models/                   entidades ORM + acesso a dados (sem password no to_dict)
│              to_dict)                 ├── controllers/              NOVO — task · user · category · report (regras de negócio)
├── routes/   (regra de negócio,        ├── routes/                   só HTTP: main · task · user · category · report + serializers
│              N+1, validação inline)   ├── validators/               NOVO — common · task · user · category
├── services/ (SMTP hardcoded,          ├── middlewares/              NOVO — error_handler · auth (token assinado)
│              não usado)               ├── services/                 notification_service com config injetada
└── utils/    (helpers mortos)          ├── utils/                    constants · errors · helpers puros
                                        └── seed.py                   usa create_app() e grava hashes seguros
```

### Checklist de validação

Legenda: ✅ atendido. Cada item foi conferido no código e/ou na execução registrada em `reports/logs/`.

| Item | P1 | P2 | P3 |
|---|---|---|---|
| **Fase 1** — Linguagem detectada corretamente | ✅ Python | ✅ JavaScript/Node | ✅ Python |
| Framework detectado corretamente | ✅ Flask 3.1.1 | ✅ Express 4.22.1 | ✅ Flask 3.0.0 |
| Domínio descrito corretamente | ✅ E-commerce | ✅ LMS com checkout | ✅ Task Manager |
| Nº de arquivos condiz com a realidade | ✅ 4 | ✅ 3 | ✅ 12 |
| **Fase 2** — Relatório segue o template | ✅ | ✅ | ✅ |
| Cada finding com arquivo e linhas exatos | ✅ | ✅ | ✅ |
| Ordenados CRITICAL → LOW | ✅ | ✅ | ✅ |
| Mínimo de 5 findings | ✅ 21 | ✅ 19 | ✅ 21 |
| APIs deprecated incluídas | ✅ `DEBUG` config | ✅ sqlite3 callbacks, `.verbose()` | ✅ `utcnow()`, `Query.get()` |
| Pausa e pede confirmação antes da Fase 3 | ✅ | ✅ | ✅ |
| **Fase 3** — Estrutura segue MVC | ✅ | ✅ | ✅ |
| Config extraída (sem hardcoded) | ✅ `src/config/settings.py` | ✅ `src/config/index.js` | ✅ `config/settings.py` |
| Models abstraem dados | ✅ | ✅ | ✅ |
| Views/Routes separadas | ✅ `src/views/` | ✅ `src/routes/` | ✅ `routes/` |
| Controllers concentram o fluxo | ✅ | ✅ | ✅ `controllers/` |
| Error handling centralizado | ✅ `middlewares/error_handler.py` | ✅ `middlewares/errorHandler.js` | ✅ `middlewares/error_handler.py` |
| Entry point claro | ✅ `app.py` → `create_app()` | ✅ `src/app.js` (`npm start`) | ✅ `app.py` → `create_app()` |
| Aplicação inicia sem erros | ✅ | ✅ | ✅ |
| Endpoints originais respondem | ✅ 19/19 | ✅ 3/3 | ✅ 22/22 |

### Evidências (logs das aplicações rodando após a refatoração)

Além da validação feita pela própria skill (registrada nos logs da Fase 3), cada projeto foi revalidado de forma independente, com banco recriado do zero.

**Projeto 1** — `python app.py` + smoke test dos 19 endpoints:

```
GET /                                 200
GET /health                           200
GET /produtos                         200
GET /produtos/busca?q=mouse           200
GET /produtos/1                       200
POST /produtos                        201
PUT /produtos/11                      200
DELETE /produtos/11                   200
GET /usuarios                         200
GET /usuarios/1                       200
POST /usuarios                        201
POST /login (seed admin123)           200
POST /pedidos                         201
GET /pedidos                          200
GET /pedidos/usuario/2                200
PUT /pedidos/1/status                 200
GET /relatorios/vendas                200
POST /admin/query (sem token)         403   ← protegido (antes executava SQL anônimo)
POST /admin/reset-db (com token)      200
"senha" em GET /usuarios? 0 ocorrências
Tracebacks no log do servidor: 0
```

**Projeto 2** — `npm start` + requisições do `api.http`:

```
1 checkout ok:   {"msg":"Sucesso","enrollment_id":2} [200]
2 checkout neg:  Pagamento recusado [400]
3 report sem tk: Não autorizado [401]          ← protegido (antes aberto)
4 report c/ tk:  [{"course":"Clean Architecture","revenue":997,"students":[{"student":"Leonan","paid":997}]},{"course":"Docker","revenue":497,"students":[{"student":"Guilherme","paid":497}]}] [200]
5 delete c/ tk:  Usuário deletado [200]
6 curso inexist: Curso não encontrado [404]
--- server log:
[INFO] LMS API rodando na porta 3000
[INFO] Processando pagamento de 497 com cartão **** 4444   ← cartão mascarado, chave não aparece
[INFO] Checkout concluído: matrícula 2 no curso "Docker"
```

**Projeto 3** — `python seed.py && python app.py` (validado com `PORT=5055`, ver nota abaixo) + smoke test dos 22 endpoints:

```
GET /health                             200
GET /                                   200
GET /tasks                              200
GET /tasks/1                            200
POST /tasks                             201
PUT /tasks/11                           200
GET /tasks/search?q=teste               200
GET /tasks/stats                        200
DELETE /tasks/11                        200
GET /users                              200
GET /users/1                            200
POST /users                             201
PUT /users/4                            200
GET /users/1/tasks                      200
POST /login (seed)                      200
DELETE /users/4 (sem token)             401   ← protegido (antes qualquer um apagava)
DELETE /users/4 (token admin)           200
GET /reports/summary                    200
GET /reports/user/1                     200
GET /categories                         200
POST /categories                        201
PUT /categories/5                       200
DELETE /categories/5                    200
"password" em GET /users/1? 0 ocorrências
Warnings (deprecated) / tracebacks no log do servidor: 0
```

> Nota: durante a validação do projeto 3 a porta 5000 estava ocupada por um servidor de teste do projeto 1 que ficou órfão no ambiente. Como a porta agora vem de configuração, a validação usou `PORT=5055` sem alterar código; a porta padrão continua 5000.

### Mudanças intencionais de contrato (segurança)

| Projeto | Mudança |
|---|---|
| 1 | `senha` removida de `/usuarios`; `secret_key`/`db_path`/`debug` removidos do `/health`; `/admin/*` exigem `X-Admin-Token` (e `/admin/query` também `ENABLE_ADMIN_QUERY=true`); login com SQL injection agora retorna 401; entradas inválidas retornam 400 em vez de 500; respostas de erro ganharam `"sucesso": false`. |
| 2 | `GET /api/admin/financial-report` e `DELETE /api/users/:id` exigem `X-Admin-Token`; DELETE de id inexistente → 404; usuário novo sem `pwd` → 400 (antes criava com senha `123456`); payload malformado → 400 em vez de derrubar o processo. |
| 3 | `password` (hash) removido de todas as respostas de usuário; `token` do `/login` passou a ser assinado (itsdangerous + `SECRET_KEY`) no lugar de `fake-jwt-token-<id>`; `DELETE /users/<id>` e atribuição/alteração de role privilegiada exigem `Authorization: Bearer <token de admin>` (401/403); CORS padrão restrito a `localhost:3000` (`CORS_ORIGINS=*` restaura); entradas inválidas → 400 JSON em vez de 500; `tasks.db` antigo (MD5) precisa ser recriado com `python seed.py`. |

### Observações sobre o comportamento em stacks diferentes

- **Monolito Python (P1):** a skill identificou corretamente o caso de "pseudo-camadas" (arquivos chamados `models.py`/`controllers.py` com responsabilidades misturadas) e criou um pacote `src/` completo, mantendo `python app.py` como comando de execução através de um entry point fino. Também tratou migração de senhas legadas em texto puro num `loja.db` já existente.
- **Node/Express (P2):** o ponto central foi o *callback hell* — a skill promisificou o driver `sqlite3`, introduziu `asyncHandler` (Express 4 não captura rejeições de handlers `async`) e transações explícitas. Preservou os nomes externos abreviados do contrato (`usr`, `eml`, `pwd`, `c_id`, `card`) mapeando-os para nomes claros na borda.
- **Flask com camadas parciais (P3):** a skill classificou o projeto como "camadas parciais — rotas gordas" e, em vez de reescrevê-lo, manteve `models/`, `routes/`, `services/` e `utils/`, criando apenas o que faltava (`controllers/`, `validators/`, `middlewares/`, `config/`). Encontrou problemas mesmo com a organização existente (MD5, hash exposto, token falso, N+1, APIs deprecated `utcnow`/`Query.get`) e manteve `python seed.py` funcionando com a nova factory.
- Nos três casos a skill pausou corretamente após a Fase 2 sem tocar em arquivos, e em nenhum caso alterou porta ou comando de execução.

---

## D) Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) instalado e autenticado (`claude --version`; usado: 2.1.318)
- Python 3.10+ (testado em 3.14) e Node.js 20.12+ (testado em 24)

### Executar a skill em cada projeto

A skill fica em `.claude/skills/refactor-arch/` dentro de cada projeto, então basta abrir o Claude Code na pasta do projeto:

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch ../reports/audit-project-1.md"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch ../reports/audit-project-2.md"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch ../reports/audit-project-3.md"
```

O argumento (caminho do relatório) é opcional; sem ele o relatório vai para `<raiz-do-repo>/reports/audit-<nome-do-projeto>.md`. A skill imprime a Fase 1, a Fase 2 e **para** em `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]` — responda `y` para refatorar.

Modo não interativo (como foi executado para esta entrega):

```bash
cd code-smells-project
claude -p "/refactor-arch ../reports/audit-project-1.md" --permission-mode acceptEdits \
  --allowedTools "Bash,Read,Write,Edit,Glob,Grep" > ../reports/logs/project-1-phase-1-2.log
claude -p --continue "y" --permission-mode acceptEdits \
  --allowedTools "Bash,Read,Write,Edit,Glob,Grep" > ../reports/logs/project-1-phase-3.log
```

### Como validar que a refatoração funcionou

**Projeto 1 — code-smells-project** (porta 5000)
```bash
cd code-smells-project
pip install -r requirements.txt
ADMIN_TOKEN=dev-token python app.py
curl localhost:5000/produtos
curl -X POST localhost:5000/login -H "Content-Type: application/json" -d '{"email":"admin@loja.com","senha":"admin123"}'
curl -X POST localhost:5000/admin/reset-db -H "X-Admin-Token: dev-token"
```

**Projeto 2 — ecommerce-api-legacy** (porta 3000)
```bash
cd ecommerce-api-legacy
npm install
ADMIN_TOKEN=dev-token npm start
# use as requisições de api.http (rotas admin com header X-Admin-Token: dev-token)
```

**Projeto 3 — task-manager-api** (porta 5000)
```bash
cd task-manager-api
pip install -r requirements.txt
python seed.py        # obrigatório antes do primeiro boot (grava senhas com hash)
python app.py
curl localhost:5000/tasks
TOKEN=$(curl -s -X POST localhost:5000/login -H "Content-Type: application/json" \
  -d '{"email":"joao@email.com","password":"1234"}' | python -c "import sys,json;print(json.load(sys.stdin)['token'])")
curl -X DELETE localhost:5000/users/3 -H "Authorization: Bearer $TOKEN"
```

Variáveis de ambiente de cada projeto estão documentadas no respectivo `.env.example`. As portas padrão (5000/3000) foram mantidas; para rodar os dois projetos Flask ao mesmo tempo use `PORT=5001`.
