# Formato dos dados

## Dados de potencial

Formato padrão:

```csv
r,energy
3.0,1.2
3.5,-0.1
4.0,-0.2
```

Colunas personalizadas também são aceitas nos loaders e workflows:

```csv
r(angstrom),E_int_CP(kcal/mol)
3.0,2.078
3.5,-0.120
4.0,-0.230
```

## Dados experimentais de B2

Formato padrão:

```csv
temperature,b2
100,-180.0
200,-45.0
```

Exemplo usado no Ar2:

```csv
Temperatura,B(segundo coef. virial) [cm³/mol]
100.3086419753086,-183.7441314553991
```

## Unidades recomendadas

- Distância: angstrom.
- Energia de ajuste: kcal/mol para os exemplos de Ar2.
- Temperatura: K.
- Resultado de `B2`: cm³/mol.

## Unidades suportadas

`distance_unit`:

- `angstrom`
- `pm`
- `meter`

`energy_unit`:

- `kelvin`
- `kcal/mol`
- `kj/mol`
- `ev`
- `mev`

As unidades de distância dos dados devem ser consistentes com os parâmetros do potencial.

