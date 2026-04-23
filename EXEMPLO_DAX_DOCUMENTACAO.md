# Exemplo de Documentação Gerada

Este é um exemplo de como a documentação markdown gerada pelo script aparece para **medidas DAX** e **colunas calculadas**.

---

## Tabelas

### fat_saldo_alienacoes

**Status**: Visível
**Atualização Automática**: Sim

#### Colunas

| Nome | Tipo | Sumarização | Oculta |
|------|------|-------------|--------|
| contrato_id | string | none | Não |
| data_referencia | dateTime | none | Não |
| saldo_devedor | decimal | sum | Não |

#### Colunas Calculadas (Resumo)

| Nome | Tipo | Formato |
|------|------|---------|
| Dias em Atraso | int64 | - |
| Status Contrato | string | - |
| Faixa de Atraso | string | - |

#### Colunas Calculadas - Código DAX

##### Dias em Atraso

**Tipo**: `int64`

```dax
DATEDIFF(
    fat_saldo_alienacoes[data_vencimento],
    fat_saldo_alienacoes[data_referencia],
    DAY
)
```

##### Status Contrato

**Tipo**: `string`

```dax
IF(
    fat_saldo_alienacoes[Dias em Atraso] > 90,
    "Inadimplente",
    IF(
        fat_saldo_alienacoes[Dias em Atraso] > 30,
        "Atraso",
        "Normal"
    )
)
```

##### Faixa de Atraso

**Tipo**: `string`

```dax
SWITCH(
    TRUE(),
    fat_saldo_alienacoes[Dias em Atraso] <= 0, "Em dia",
    fat_saldo_alienacoes[Dias em Atraso] <= 30, "1-30 dias",
    fat_saldo_alienacoes[Dias em Atraso] <= 60, "31-60 dias",
    fat_saldo_alienacoes[Dias em Atraso] <= 90, "61-90 dias",
    "Acima de 90 dias"
)
```

---

### _Medidas

**Status**: Visível
**Atualização Automática**: Sim

#### Medidas (Resumo)

| Nome | Formato |
|------|---------|
| Total Carteira | R$ #,##0.00 |
| Inadimplência % | 0.00% |
| Saldo Devedor | R$ #,##0.00 |
| Taxa Média | 0.00% |

#### Medidas - Código DAX

##### Total Carteira

**Formato**: `R$ #,##0.00`

```dax
CALCULATE(
    SUM(fat_saldo_alienacoes[saldo_devedor]),
    FILTER(
        fat_saldo_alienacoes,
        fat_saldo_alienacoes[data_referencia] = MAX(fat_saldo_alienacoes[data_referencia])
    )
)
```

##### Inadimplência %

**Formato**: `0.00%`

```dax
DIVIDE(
    [Saldo Inadimplente],
    [Total Carteira],
    0
)
```

##### Saldo Devedor

**Formato**: `R$ #,##0.00`

```dax
SUM(fat_saldo_alienacoes[saldo_devedor])
```

##### Taxa Média

**Formato**: `0.00%`

```dax
AVERAGEX(
    FILTER(
        fat_saldo_alienacoes,
        fat_saldo_alienacoes[saldo_devedor] > 0
    ),
    fat_saldo_alienacoes[taxa_juros_mensal]
)
```

---

**Agora TODAS as expressões DAX estão documentadas com código completo:**
- ✅ **Medidas** - Tabela resumo + código DAX completo
- ✅ **Colunas Calculadas** - Tabela resumo + código DAX completo

