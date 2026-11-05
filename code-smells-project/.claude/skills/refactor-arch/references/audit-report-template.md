# Template do Relatório de Auditoria (Fase 2)

O relatório é impresso no terminal e, **somente depois que o usuário responder à confirmação**, salvo como Markdown com o mesmo conteúdo. Siga a estrutura abaixo literalmente; substitua apenas os `<placeholders>`.

## Regras

1. **Ordenação:** CRITICAL → HIGH → MEDIUM → LOW; dentro da severidade, por arquivo e linha.
2. **Numeração:** IDs sequenciais `F-01`, `F-02`… na ordem final.
3. **Localização exata:** `arquivo:linha` ou `arquivo:inicio-fim`, caminho relativo à raiz do projeto. Várias localizações separadas por vírgula. Confira cada número lendo o arquivo — nunca estime.
4. **Descrição concreta:** cite o trecho, valor ou nome real (ex.: "`SECRET_KEY` = `'minha-chave-super-secreta-123'`"), não generalidades.
5. **Recomendação** aponta o padrão do playbook (`PB-xx`) e o destino na arquitetura MVC.
6. **Summary** deve bater com a contagem dos findings; **Total** = soma.
7. A seção **Deprecated APIs** é obrigatória (lista os findings AP-17 ou declara que não há).
8. Não inclua achados sem evidência. Na dúvida sobre severidade, use a escala do catálogo e explique o ajuste.

## Estrutura

````markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do diretório do projeto>
Stack:   <Linguagem> + <Framework versão>
Files:   <N> analyzed | ~<L> lines of code
Date:    <AAAA-MM-DD>

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

| ID | Severity | Anti-pattern | Location |
|----|----------|--------------|----------|
| F-01 | CRITICAL | <nome> | <arquivo:linha> |
| ... | ... | ... | ... |

## Findings

### F-01 [CRITICAL] <Nome do anti-pattern> (AP-xx)
File: <arquivo:linha[-linha]>[, <arquivo:linha>...]
Description: <o que foi encontrado, citando o código/valor>
Impact: <consequência concreta para segurança/manutenção/performance>
Recommendation: <ação + padrão PB-xx + camada destino>

### F-02 [HIGH] <...>
File: ...
Description: ...
Impact: ...
Recommendation: ...

<... demais findings, na ordem ...>

## Deprecated APIs
| Location | Deprecated | Modern replacement |
|----------|-----------|--------------------|
| <arquivo:linha> | <API> | <substituto> |
<ou: "Nenhuma API deprecated detectada para <versões>.">

## Architecture Snapshot
Current:  <classificação da Fase 1, uma linha>
Target:   MVC — config / models / views(routes) / controllers / middlewares / composition root

================================
Total: <N> findings
================================
````

Após o bloco, termine com a pergunta de confirmação definida no SKILL.md (nada é gravado em disco antes da resposta; depois dela, salve o relatório e informe o caminho):

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

## Exemplo de finding bem escrito

```markdown
### F-02 [CRITICAL] SQL Injection (AP-02)
File: models.py:28, models.py:47-50, models.py:57-61, models.py:109-111
Description: Queries montadas por concatenação de strings com dados do request, ex.: `"SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"` no login.
Impact: Bypass de autenticação com `' OR '1'='1` e leitura/alteração arbitrária do banco.
Recommendation: Usar queries parametrizadas com placeholders `?` (PB-02) nos novos models de cada domínio.
```

## Exemplo de finding mal escrito (não faça)

```markdown
### [HIGH] Código ruim
File: models.py
Description: O código tem problemas de qualidade.
```
(sem linha, sem evidência, sem impacto, sem recomendação acionável)
