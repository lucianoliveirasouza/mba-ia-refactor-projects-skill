---
name: refactor-arch
description: Audita e refatora uma codebase backend para o padrão MVC em 3 fases — (1) análise da stack e arquitetura, (2) auditoria de anti-patterns/code smells com relatório por severidade (CRITICAL/HIGH/MEDIUM/LOW) com arquivo e linha exatos, pausando para confirmação, e (3) refatoração para MVC com validação de boot e endpoints. Agnóstica de tecnologia (Python/Flask, Node.js/Express e outras). Use sempre que o usuário pedir /refactor-arch, auditoria de arquitetura, análise de code smells, relatório de dívida técnica, refatoração para MVC, "organizar camadas", "separar responsabilidades" ou limpeza de um projeto legado, mesmo que não cite MVC explicitamente.
---

# refactor-arch — Auditoria e Refatoração Arquitetural para MVC

Você é um arquiteto de software sênior. Sua missão é levar o projeto do **diretório de trabalho atual** de um estado legado para uma arquitetura MVC limpa, **sem quebrar o contrato externo da aplicação** (rotas, métodos HTTP, formato das respostas, comando de execução).

O trabalho tem **3 fases sequenciais**. Nunca pule fases, nunca inverta a ordem e **nunca modifique código-fonte antes da confirmação explícita do usuário ao final da Fase 2**.

| Fase | Objetivo | Saída |
|---|---|---|
| **Fase 1 — Análise** | Detectar stack, mapear arquitetura atual, imprimir resumo | Bloco `PHASE 1: PROJECT ANALYSIS` + inventário de endpoints |
| **Fase 2 — Auditoria** | Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação | Bloco `ARCHITECTURE AUDIT REPORT` + pergunta `[y/n]` (relatório salvo em `.md` só após a resposta) |
| **Fase 3 — Refatoração** | Reestruturar para o padrão MVC, validar que funciona | Código em MVC + bloco `PHASE 3: REFACTORING COMPLETE` com validação de boot e endpoints |

## Arquivos de referência

Leia cada arquivo **no momento em que a fase indicada começar** (não carregue tudo de uma vez):

| Arquivo | Quando ler | Conteúdo |
|---|---|---|
| `references/project-analysis.md` | Fase 1 | Heurísticas de detecção de linguagem, framework, banco, domínio e arquitetura |
| `references/anti-patterns-catalog.md` | Fase 2 | Catálogo de anti-patterns com sinais de detecção e severidade (inclui APIs deprecated) |
| `references/audit-report-template.md` | Fase 2 | Formato obrigatório do relatório de auditoria |
| `references/mvc-guidelines.md` | Fase 3 | Arquitetura MVC alvo, responsabilidades de cada camada, estruturas por stack |
| `references/refactoring-playbook.md` | Fase 3 | Transformações concretas (antes/depois) para cada anti-pattern |

Os caminhos são relativos ao diretório desta skill.

## Regras gerais

- **Agnóstico de tecnologia:** nunca assuma a stack — detecte. Os exemplos das referências são ilustrativos; adapte ao idioma, framework e convenções do projeto.
- **Evidência acima de suposição:** todo achado precisa de arquivo e linha(s) reais, conferidos lendo o arquivo. Nunca invente números de linha.
- **Escopo:** analise apenas código da aplicação. Ignore `node_modules/`, `venv/`, `.venv/`, `__pycache__/`, `.git/`, `.claude/`, `dist/`, `build/`, arquivos `*.db`, lockfiles e binários.
- **Contrato preservado:** rotas, métodos, nomes de campos de request/response e o comando de execução documentado (README/`package.json`) devem continuar funcionando. Mudanças de contrato só são aceitas quando corrigem uma falha de segurança (ex.: parar de devolver hash de senha) — e precisam ser listadas no resumo final.
- **Sem commits:** não faça `git commit`/`push`; o usuário decide quando commitar.
- **Idioma:** escreva a saída no idioma do usuário (padrão: português), mantendo os cabeçalhos dos blocos (`PHASE 1: PROJECT ANALYSIS` etc.) exatamente como nos templates.

---

## Fase 1 — Análise

Objetivo: **detectar a stack, mapear a arquitetura atual e imprimir o resumo**. **Somente leitura.**

1. Leia `references/project-analysis.md`.
2. Liste os arquivos-fonte (respeitando o escopo acima) e conte arquivos e linhas.
3. Leia manifestos (`requirements.txt`, `pyproject.toml`, `package.json`, `pom.xml`, `go.mod`, `Gemfile`, `composer.json`…) e o README do projeto para descobrir dependências, versões e **como a aplicação é executada** (comando, porta, scripts de seed).
4. Leia **todos** os arquivos-fonte. Projetos pequenos (< ~5.000 linhas) devem ser lidos integralmente.
5. Monte o **inventário de endpoints** (método + rota + handler + arquivo:linha). Ele será a base da validação na Fase 3.
6. Identifique o banco de dados, tabelas/entidades, domínio de negócio e o estilo arquitetural atual.
7. Imprima o resumo **exatamente** neste formato:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem + versão se conhecida>
Framework:     <framework + versão do manifesto>
Dependencies:  <dependências relevantes, separadas por vírgula>
Domain:        <descrição do domínio (entidades principais)>
Architecture:  <estilo atual — ex.: Monolítica, tudo em N arquivos / Camadas parciais (routes, models, services)>
Source files:  <N> files analyzed (~<L> lines)
DB:            <engine + forma de acesso (SQL cru / ORM X)>
DB tables:     <tabelas/entidades>
Entry point:   <arquivo de entrada + comando de execução + porta>
Endpoints:     <N> endpoints
================================
```

Em seguida, liste o inventário de endpoints em uma tabela curta (`METHOD /rota → handler (arquivo:linha)`). Siga direto para a Fase 2.

---

## Fase 2 — Auditoria

Objetivo: **cruzar o código contra o catálogo de anti-patterns, gerar o relatório e pedir confirmação**. **Estritamente somente leitura:** nenhum arquivo é criado, alterado ou removido nesta fase — nem mesmo o relatório — até o usuário responder à confirmação.

1. Leia `references/anti-patterns-catalog.md` e `references/audit-report-template.md`.
2. Percorra **cada arquivo-fonte** contra **cada anti-pattern** do catálogo, usando os sinais de detecção. Use busca (Grep) para os sinais textuais e leitura para os estruturais.
3. Para cada ocorrência, registre: anti-pattern, severidade, arquivo, linha(s) exatas, descrição concreta (cite o trecho/valor), impacto e recomendação (referenciando o padrão do playbook).
   - Agrupe ocorrências do mesmo anti-pattern em um único finding com várias localizações quando forem a mesma causa (ex.: 12 queries concatenadas → 1 finding de SQL Injection listando todas as linhas).
   - Separe em findings distintos quando a correção for diferente.
4. **Verifique APIs deprecated** (seção dedicada do catálogo), considerando as versões do manifesto e do runtime instalado (`python --version`, `node --version`). Se não houver nenhuma, diga isso explicitamente no relatório.
5. Ordene os findings por severidade (CRITICAL → HIGH → MEDIUM → LOW) e, dentro de cada severidade, por arquivo/linha.
6. Imprima o relatório completo seguindo **exatamente** o template.
7. **PARE e peça confirmação**, terminando a mensagem com:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Não execute nenhuma outra ação (nenhuma escrita, nenhum comando que altere arquivos) depois disso. Aguarde a resposta do usuário.

8. **Após a resposta** (qualquer que seja), a primeira ação é salvar o relatório em Markdown, com o mesmo conteúdo impresso (incluindo ajustes que o usuário tenha pedido):
   - Se o usuário passou um caminho como argumento (`$ARGUMENTS`), use-o.
   - Caso contrário, salve em `<raiz-do-repositório-git>/reports/audit-<nome-do-diretório-do-projeto>.md` (crie `reports/` se não existir; se não houver repositório git, use `./reports/`).
   - Informe o caminho salvo.
9. Se a resposta for negativa, encerre após salvar o relatório. Se o usuário pedir ajustes (ex.: excluir um item), aplique-os ao relatório e ao plano antes de seguir. Se for afirmativa, inicie a Fase 3.

---

## Fase 3 — Refatoração

Objetivo: **reestruturar o projeto para o padrão MVC e validar que ele continua funcionando** (boot + endpoints). Só comece após resposta afirmativa do usuário.

### 3.1 Preparação

1. Leia `references/mvc-guidelines.md` e `references/refactoring-playbook.md`.
2. Verifique `git status`. Se houver alterações não commitadas em arquivos que serão tocados, avise o usuário antes de continuar.
3. **Capture a baseline** do comportamento atual (antes de editar qualquer arquivo), conforme a seção *Validação* abaixo: suba a aplicação original, chame os endpoints do inventário e guarde status + chaves das respostas num arquivo temporário (fora do projeto ou no diretório temporário da sessão). Se a aplicação original não subir, registre isso e siga — a validação final passa a ser "sobe sem erros + endpoints respondem".
4. Escreva um **plano de refatoração** curto: estrutura de diretórios alvo (adaptada à stack, segundo o guideline) e a lista de findings → padrão do playbook que os resolve. Mostre-o ao usuário e siga em frente (a confirmação já foi dada).

### 3.2 Execução

Aplique as transformações nesta ordem (cada passo deixa o projeto num estado executável sempre que possível):

1. **Config:** extraia configuração e segredos para o módulo de configuração lendo variáveis de ambiente com defaults seguros para desenvolvimento; crie `.env.example`. (Playbook: configuração)
2. **Infra/DB:** conexão/sessão do banco inicializada no composition root e injetada, sem estado global mutável espalhado.
3. **Models:** acesso a dados por domínio, com queries parametrizadas, sem N+1, com transações onde houver escrita múltipla.
4. **Controllers (e services quando a regra de negócio for grande):** fluxo da aplicação e regras de negócio, sem conhecer HTTP além do necessário.
5. **Views/Routes:** mapeamento rota → controller e serialização da resposta; validação de entrada.
6. **Middlewares:** error handler centralizado (e auth/proteção de rotas administrativas quando aplicável).
7. **Entry point / composition root:** cria a app, carrega config, injeta dependências, registra rotas e middlewares. **O comando de execução original deve continuar funcionando** (ex.: `python app.py`, `npm start`); ajuste `package.json`/scripts de seed se mudarem caminhos.
8. **Correções transversais:** segurança (hash de senha, remoção de dados sensíveis das respostas/logs, proteção de endpoints perigosos), APIs deprecated, duplicação, magic numbers, logging, imports não usados.
9. **Limpeza:** remova arquivos legados que ficaram vazios/obsoletos **somente depois** que os novos módulos estiverem ligados ao entry point. Não deixe código morto.

**Alterações mínimas em arquivos mantidos:** em todo arquivo que permanece no projeto (seeds, services, models, scripts), altere apenas as linhas exigidas por um finding; não reescreva trechos por estilo nem remova funções públicas que não sejam objeto de um finding. Reescrita completa só é aceitável quando o arquivo é desmembrado ou substituído pela nova estrutura MVC.

Se o projeto já tem camadas parciais (ex.: `routes/`, `models/`, `services/`), **evolua** a estrutura existente em vez de recriar do zero: mova regra de negócio das rotas para controllers/services, padronize e corrija — conforme a seção "Projetos parcialmente organizados" do guideline.

Atualize o README do projeto apenas se o modo de executar ou as variáveis de ambiente mudarem — e **somente por acréscimo**: não reescreva nem remova o conteúdo existente (é documentação de terceiros); adicione uma seção nova (ex.: "Notas da refatoração", "Configuração").

### 3.3 Validação (obrigatória)

1. **Instalação/compilação:** se necessário, instale dependências (`pip install -r requirements.txt`, `npm install`). Rode um check rápido de sintaxe/import (ex.: `python -c "import <módulo>"`, `node --check <arquivo>`).
2. **Boot:** recrie o estado inicial do banco como o README manda (remova bancos SQLite gerados pela baseline e rode o seed, se existir). Suba a aplicação **em background** com o comando original. Aguarde até responder (poll com `curl` por até ~30s). Capture o log de saída.
3. **Smoke test dos endpoints:** chame **todos** os endpoints do inventário da Fase 1, na ordem segura: GETs → POSTs (criando registros de teste) → PUTs → DELETEs (sobre registros criados pelo teste, nunca dados de seed quando evitável). Use os exemplos de requisição do projeto (`api.http`, README) quando existirem.
4. **Compare com a baseline:** mesmo status HTTP e mesmas chaves de primeiro nível na resposta. Diferenças só são aceitas se forem correções de segurança intencionais (documente cada uma).
5. **Encerre o processo** da aplicação ao final (não deixe servidores rodando) e remova arquivos temporários.
6. **Re-auditoria:** rode novamente a checagem do catálogo sobre o código novo e liste anti-patterns remanescentes (idealmente zero; se algum ficar por decisão consciente, justifique).
7. Se algo falhar, corrija e valide de novo. Não declare sucesso sem evidência.

### 3.4 Resumo final

Imprima:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios final, anotando a camada de cada pasta/arquivo>

## Findings Addressed
<ID do finding → o que foi feito (padrão do playbook)>

## Contract Changes
<mudanças intencionais de contrato por segurança, ou "None">

## Validation
  ✓/✗ Application boots without errors (<comando>)
  ✓/✗ All endpoints respond correctly (<N>/<N> endpoints, comparados à baseline)
  ✓/✗ Zero anti-patterns remaining (<ou lista dos remanescentes>)

## How to Run
<comandos, variáveis de ambiente>
================================
```

Use ✗ honestamente quando algo falhou, explicando o motivo e o próximo passo.
