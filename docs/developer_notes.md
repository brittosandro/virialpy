# Notas para desenvolvimento

## Adicionar novos potenciais

1. Crie um módulo em `src/virialpy/potentials/`.
2. Implemente uma função vetorizável `U(r)`.
3. Registre a função em `src/virialpy/potentials/registry.py`.
4. Exporte a função em `src/virialpy/potentials/__init__.py`, se fizer parte da API pública.
5. Adicione testes em `tests/`.

## Adicionar novos integradores

1. Crie um módulo em `src/virialpy/integrators/`.
2. Crie uma classe que herda `BaseIntegrator`.
3. Implemente `integrate(function, lower, upper)`.
4. Retorne sempre `(value, error)`.
5. Exporte a classe em `src/virialpy/integrators/__init__.py`.
6. Adicione testes numéricos.

## Criar novos workflows

Workflows devem ficar em `src/virialpy/workflows/`.

Boas práticas:

- ler dados uma vez;
- validar entradas;
- delegar cálculos para módulos científicos;
- salvar arquivos apenas quando um caminho de saída for informado;
- não imprimir dentro de funções do pacote;
- retornar `DataFrame`, `FitResult` ou estruturas explícitas.

## Escrever testes

Use `pytest`.

Os testes devem cobrir:

- entradas válidas;
- erros claros para entradas inválidas;
- formatos de saída;
- criação de arquivos temporários com `tmp_path`;
- backend gráfico `Agg` para testes de figuras.

## Convenção de diretórios

```text
data/raw/<sistema>/
data/results/<sistema>/<modelo>/
outputs/figures/<sistema>/<etapa>/
outputs/reports/<sistema>/tables/
```

## Cuidados

- Não misture unidades sem informar `energy_unit` e `distance_unit`.
- Não altere scripts legados sem preservar os workflows atuais.
- Evite lógica científica em scripts; prefira funções no pacote.

