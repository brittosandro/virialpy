# virialpy

`virialpy` é um pacote Python científico para:

- ajustar potenciais intermoleculares `U(r)`;
- calcular o segundo coeficiente do virial `B2(T)`;
- comparar resultados calculados com dados experimentais;
- avaliar diferentes potenciais, integradores e metodologias de integração;
- gerar tabelas e figuras para análise científica.

## Motivação científica

O segundo coeficiente do virial conecta propriedades macroscópicas de gases reais com a interação microscópica entre pares moleculares. Ao combinar potenciais intermoleculares ajustados, integração numérica e dados experimentais, o `virialpy` ajuda a investigar como a forma de `U(r)` afeta `B2(T)`.

## Funcionalidades atuais

- leitura de dados teóricos `U(r)`;
- leitura de dados experimentais `B2(T)`;
- potenciais LJ, ILJ e Rydberg6;
- ajuste de potenciais com SciPy;
- exportação de parâmetros, resíduos e métricas;
- gráficos individuais e comparativos dos ajustes;
- integradores numéricos:
  - SciPy quad;
  - Gauss-Legendre;
  - Simpson;
  - Trapézio;
  - Monte Carlo;
- cálculo direto de `B2(T)`;
- cálculo particionado de `B2(T)`;
- comparação com dados experimentais;
- métricas estatísticas;
- tabelas finais em CSV e LaTeX;
- figuras finais para relatório/artigo.

## Estrutura do projeto

```text
virialpy/
├── data/
├── examples/
├── legacy/
├── outputs/
├── scripts/
├── src/virialpy/
└── tests/
```

- `data/`: dados brutos, processados e resultados numéricos.
- `examples/`: exemplos e templates de sistemas.
- `legacy/`: scripts antigos usados como referência científica.
- `outputs/`: figuras, relatórios e tabelas finais.
- `scripts/`: scripts reproduzíveis para o estudo de caso Ar2.
- `src/virialpy/`: código-fonte do pacote.
- `tests/`: testes automatizados.

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

## Testes

```bash
pytest
```

Os testes verificam potenciais, leitura de dados, ajuste, integradores, cálculo de `B2`, validação experimental, gráficos e tabelas.

## CLI

Depois da instalação em modo editável, a forma recomendada de executar os workflows principais é a CLI:

```bash
virialpy --help
virialpy ar2 --help
virialpy ar2 fit
virialpy ar2 b2
virialpy ar2 validate
virialpy ar2 full-pipeline
```

Os scripts em `scripts/` continuam disponíveis para execução direta e para fins de reprodutibilidade, mas a CLI fornece uma interface mais conveniente para uso no terminal.

## Formato dos dados de entrada

Dados de potencial no formato padrão:

```csv
r,energy
3.0,1.2
3.5,-0.1
4.0,-0.2
```

Também é possível usar colunas personalizadas, por exemplo:

```csv
r(angstrom),E_int_CP(kcal/mol)
3.0,2.078
3.5,-0.120
4.0,-0.230
```

Dados experimentais de virial no formato padrão:

```csv
temperature,b2
100,-180.0
200,-45.0
```

No estudo de caso Ar2, o arquivo experimental usa:

```csv
Temperatura,B(segundo coef. virial) [cm³/mol]
100.3086419753086,-183.7441314553991
```

## Exemplo rápido: ajuste de potencial

```python
from virialpy.datasets import load_potential_data
from virialpy.fitting import fit_potential_scipy
from virialpy.potentials import lennard_jones

data = load_potential_data(
    "data/raw/ar2/ar2_cep_bsse.csv",
    r_column="r(angstrom)",
    energy_column="E_int_CP(kcal/mol)",
)

result = fit_potential_scipy(
    data=data,
    potential_func=lennard_jones,
    initial_guess=[0.25, 3.5],
    parameter_names=["epsilon", "sigma"],
    potential_name="lj",
)
```

## Exemplo rápido: workflow de ajuste

```python
from virialpy.workflows import run_fit_workflow

result = run_fit_workflow(
    data_path="data/raw/ar2/ar2_cep_bsse.csv",
    potential_name="lj",
    initial_guess=[0.25, 3.5],
    parameter_names=["epsilon", "sigma"],
    r_column="r(angstrom)",
    energy_column="E_int_CP(kcal/mol)",
    output_dir="data/results/ar2/lj",
)
```

## Exemplo rápido: comparação entre potenciais

Via CLI:

```bash
virialpy ar2 fit
```

Ou via script:

```bash
python3 scripts/run_compare_potentials_ar2.py
```

## Exemplo rápido: cálculo de B2

Via CLI:

```bash
virialpy ar2 b2
```

Ou via script:

```bash
python3 scripts/run_b2_comparison_ar2.py
```

## Exemplo rápido: validação experimental

Via CLI:

```bash
virialpy ar2 validate
```

Ou via script:

```bash
python3 scripts/run_b2_validation_ar2.py
```

## Exemplo rápido: método particionado

```bash
python3 scripts/run_partitioned_b2_ar2.py
```

## Exemplo rápido: comparação Monte Carlo

```bash
python3 scripts/run_monte_carlo_comparison_ar2.py
```

## Gerar figuras e tabelas finais

Via CLI:

```bash
virialpy ar2 figures
```

Ou via script:

```bash
python3 scripts/gerar_figuras_tabelas_finais_ar2.py
```

As saídas principais ficam em:

```text
outputs/figures/ar2/final/
outputs/reports/ar2/tables/
```

## Como adicionar um novo potencial

1. Crie um arquivo em `src/virialpy/potentials/`.
2. Implemente a função `U(r)`.
3. Registre a função em `src/virialpy/potentials/registry.py`.
4. Exporte em `src/virialpy/potentials/__init__.py`, se necessário.
5. Crie testes em `tests/`.

## Como adicionar um novo integrador

1. Crie uma classe que herda `BaseIntegrator`.
2. Implemente `integrate(function, lower, upper)`.
3. Registre/importe em `src/virialpy/integrators/__init__.py`.
4. Crie testes em `tests/`.

## Organização dos resultados

Convenção recomendada:

```text
data/results/<sistema>/<modelo>/
outputs/figures/<sistema>/<etapa>/
outputs/reports/<sistema>/tables/
```

## Observações sobre unidades

- A unidade de `r` deve ser consistente com `sigma`, `req` ou `re`.
- A unidade de energia dos parâmetros ajustados deve ser informada no cálculo de `B2` por `energy_unit`.
- `B2` é retornado em `cm³/mol`.
- `distance_unit` pode ser `angstrom`, `pm` ou `meter`.
- `energy_unit` pode ser `kelvin`, `kcal/mol`, `kj/mol`, `ev` ou `mev`.

## Status do projeto

O projeto está em desenvolvimento. Atualmente, o Ar2 é o principal estudo de caso usado para validar e demonstrar os workflows.

## Licença

Consulte o arquivo [LICENSE](LICENSE).
