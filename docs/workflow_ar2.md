# Workflow Ar2

Este documento resume o fluxo completo do estudo de caso Ar2 no `virialpy`.

## 1. Dados de entrada U(r)

O arquivo principal de energia potencial está em:

```text
data/raw/ar2/ar2_cep_bsse.csv
```

As colunas usadas nos exemplos são:

```text
r(angstrom)
E_int_CP(kcal/mol)
```

## 2. Ajuste dos potenciais

O ajuste e a comparação entre LJ, ILJ e Rydberg6 podem ser executados com:

```bash
python3 scripts/teste_compare_potentials_ar2.py
```

Esse script salva parâmetros, métricas, resíduos e figuras de ajuste.

## 3. Comparação dos ajustes

As figuras comparativas dos ajustes são geradas em:

```text
outputs/figures/ar2/fit/
```

## 4. Cálculo direto de B2

Execute:

```bash
python3 scripts/teste_b2_comparison_ar2.py
```

Esse script calcula `B2(T)` para múltiplos potenciais e integradores.

## 5. Cálculo particionado de B2

Execute:

```bash
python3 scripts/teste_partitioned_b2_ar2.py
```

O método particionado usa regiões de integração inspiradas no script legado.

## 6. Validação contra experimento

Execute:

```bash
python3 scripts/teste_b2_validation_ar2.py
```

O arquivo experimental usado é:

```text
data/raw/ar2/b2_experimental.csv
```

## 7. Comparação Monte Carlo

Execute:

```bash
python3 scripts/teste_monte_carlo_comparison_ar2.py
```

Essa etapa compara o integrador Monte Carlo contra SciPy quad, Gauss-Legendre, Simpson e Trapézio.

## 8. Figuras e tabelas finais

Execute:

```bash
python3 scripts/gerar_figuras_tabelas_finais_ar2.py
```

As figuras finais ficam em:

```text
outputs/figures/ar2/final/
```

As tabelas finais ficam em:

```text
outputs/reports/ar2/tables/
```

## Pipeline completo

Para executar todas as etapas principais na ordem recomendada:

```bash
python3 scripts/run_ar2_full_pipeline.py
```

