# Workflow Ar2

Este documento resume o fluxo completo do estudo de caso Ar2 no `virialpy`.

## CLI recomendada

Depois de instalar o pacote com `pip install -e .`, use:

```bash
virialpy --help
virialpy ar2 --help
virialpy ar2 fit
virialpy ar2 b2
virialpy ar2 validate
virialpy ar2 full-pipeline
```

Os scripts continuam disponíveis e são chamados internamente pela CLI.

## CLI geral por argumentos

A CLI geral permite executar as etapas principais com caminhos, colunas,
potenciais, integradores e unidades definidos no terminal:

```bash
virialpy run fit \
    --system ar2 \
    --potential-data data/raw/ar2/ar2_cep_bsse.csv \
    --r-column "r(angstrom)" \
    --energy-column "E_int_CP(kcal/mol)" \
    --potentials all \
    --output-dir data/results/ar2_general_cli

virialpy run b2 \
    --system ar2 \
    --experimental-data data/raw/ar2/b2_experimental.csv \
    --temperature-column "Temperatura" \
    --potentials all \
    --integrators all \
    --results-dir data/results/ar2_general_cli \
    --energy-unit "kcal/mol" \
    --distance-unit angstrom \
    --r-min 2.5 \
    --r-max 30.0

virialpy run validate \
    --system ar2 \
    --experimental-data data/raw/ar2/b2_experimental.csv \
    --temperature-column "Temperatura" \
    --b2-column "B(segundo coef. virial) [cm³/mol]" \
    --results-dir data/results/ar2_general_cli \
    --figures-dir outputs/figures/ar2_general_cli

virialpy run full \
    --system ar2 \
    --potential-data data/raw/ar2/ar2_cep_bsse.csv \
    --experimental-data data/raw/ar2/b2_experimental.csv \
    --r-column "r(angstrom)" \
    --energy-column "E_int_CP(kcal/mol)" \
    --temperature-column "Temperatura" \
    --b2-column "B(segundo coef. virial) [cm³/mol]" \
    --potentials all \
    --integrators all \
    --energy-unit "kcal/mol" \
    --distance-unit angstrom \
    --r-min 2.5 \
    --r-max 30.0 \
    --results-dir data/results/ar2_general_cli \
    --figures-dir outputs/figures/ar2_general_cli \
    --reports-dir outputs/reports/ar2_general_cli
```

## Execução por arquivo YAML

O mesmo fluxo geral pode ser descrito em um arquivo YAML:

```bash
virialpy run-config configs/ar2.yaml
```

O arquivo `configs/ar2.yaml` define dados de entrada, colunas, potenciais,
integradores, unidades, limites de integração e diretórios de saída. Consulte
`docs/configuration.md` para a referência completa.

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
virialpy ar2 fit
```

ou diretamente:

```bash
python3 scripts/run_compare_potentials_ar2.py
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
virialpy ar2 b2
```

ou diretamente:

```bash
python3 scripts/run_b2_comparison_ar2.py
```

Esse script calcula `B2(T)` para múltiplos potenciais e integradores.

## 5. Cálculo particionado de B2

Execute:

```bash
virialpy ar2 partitioned
```

ou diretamente:

```bash
python3 scripts/run_partitioned_b2_ar2.py
```

O método particionado usa regiões de integração inspiradas no script legado.

## 6. Validação contra experimento

Execute:

```bash
virialpy ar2 validate
```

ou diretamente:

```bash
python3 scripts/run_b2_validation_ar2.py
```

O arquivo experimental usado é:

```text
data/raw/ar2/b2_experimental.csv
```

## 7. Comparação Monte Carlo

Execute:

```bash
virialpy ar2 monte-carlo
```

ou diretamente:

```bash
python3 scripts/run_monte_carlo_comparison_ar2.py
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
virialpy ar2 full-pipeline
```

ou diretamente:

```bash
python3 scripts/run_ar2_full_pipeline.py
```
