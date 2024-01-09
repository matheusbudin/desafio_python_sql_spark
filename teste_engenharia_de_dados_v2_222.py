# -*- coding: utf-8 -*-
"""teste_engenharia_de_dados_v2_222.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1CUQWNxreaVVCcGqBBvncXoh-mdVSTk17

# Setup Geral

Se estiver executando este exercício no Google Colab, execute as próximas duas células.

Caso esteja executando localmente, não é necessário executar mas certifique-se de que o **pyspark** está instalado e configurado em sua máquina.
"""

# Commented out IPython magic to ensure Python compatibility.
# %%bash
# 
# # Instal Java
# apt-get update && apt-get install openjdk-8-jdk-headless -qq > /dev/null
# 
# # Install PySpark
# pip install -q pyspark

import os
os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-8-openjdk-amd64'

from pyspark.sql import SparkSession

spark = SparkSession.builder.master("local[*]").getOrCreate()

"""# Teste

O teste a ser realizado é composto de 3 partes:

- um exercício de programação em Python
- alguns exercícios de programação em SQL
- alguns exercícios de programação com PySpark

Você pode escolher qual das partes do exercício vai fazer primeiro. Todo o exercício deve ser completado no período de 48 horas.

# Python
"""

# SETUP
nomes_alunos = [
    ('Maria', 1),
    ('João', 2),
    ('Pedro', 3),
    ('Gabriella', 4),
    ('Giovana', 5),
    ('Arthur', 6)
]

notas_alunos = {
    1: 9.5,
    2: 5.1,
    3: 8.7,
    4: 7.1,
    5: 4.8,
    6: 6.3
}

"""Implemente uma função que recebe uma lista de nomes de alunos, um dicionário de notas dos mesmo, sendo que essas estruturas se relacionam por um ID.

A função deve retornar em ordem alfabética, o nome dos alunos que obtiveram notas maior ou igual de uma nota de corte informada.
"""

def filtra_alunos_acima_corte(alunos, notas, nota_corte):
  # Desenvolva aqui
    # Primeiro, cria-se um dicionário para mapear IDs de alunos:
    dicionario_estudantes = {id: name for name, id in alunos}

    # Verifica-se que cada ID na lista de alunos corresponda a um ID no dicionário de notas
    alunos_verificados = [id for nome, id in alunos if id in notas]

    # Filtra-se as notas do dicionário para encontrar alunos com notas acima do corte:
    alunos_aprovados = {id: nota for id, nota in notas.items() if nota >= nota_corte}

    # Mapeia-se os estudantes aprovados, referenciando-se os nomes novamente:
    nomes_alunos_aprovados = [dicionario_estudantes[id] for id in alunos_aprovados]

    # Ordena em ordem alfabética e retorna a lista com o resultado
    return sorted(nomes_alunos_aprovados)
filtra_alunos_acima_corte(nomes_alunos, notas_alunos, 6)

"""# SQL

**Setup**
"""

# Commented out IPython magic to ensure Python compatibility.
# %%bash
# mkdir bases_teste
# curl https://raw.githubusercontent.com/A3Data/bases_testes/main/bases_teste/produtos.csv -o bases_teste/produtos.csv
# curl https://raw.githubusercontent.com/A3Data/bases_testes/main/bases_teste/vendas.csv -o bases_teste/vendas.csv
# curl https://raw.githubusercontent.com/A3Data/bases_testes/main/bases_teste/usuarios.csv -o bases_teste/usuarios.csv

# Setup Spark Session
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("AtividadeSQL").getOrCreate()

def cria_tabela(path, nome_tabela):
    df = spark.read.csv(path, inferSchema=True, header=True)
    df.createOrReplaceTempView(nome_tabela)
    return df

usuarios = cria_tabela("bases_teste/usuarios.csv", "usuarios")
produtos = cria_tabela("bases_teste/produtos.csv", "produtos")
vendas = cria_tabela("bases_teste/vendas.csv", "vendas")

"""**Função para execução de queries**"""

def q(query, n=30):
    return spark.sql(query).show(n=n, truncate=False)

"""Para executar alguma consulta, basta colocar seu código sql dentro da função q como no exemplo abaixo:

```python
q('''
    SELECT *
    FROM usuarios
''')
```

e o resultado será exibido na tela.

---

Nesta parte da atividade, você vai trabalhar com três tabelas:

- produtos
- usuarios
- vendas

Use-as para responder às perguntas a seguir.

1) Qual foi a quantidade de vendas nos estados de Minas Gerais e São Paulo para cada ano e mês?
"""

#amostras de cada tabela
q("""
SELECT * FROM usuarios LIMIT 3
""")
q("""
SELECT * FROM vendas LIMIT 3
""")
q("""
SELECT * FROM produtos LIMIT 3
""")

q("""
SELECT
YEAR(vendas.data_compra) AS ano
,MONTH(vendas.data_compra) AS mes
,usuarios.estado
,SUM(vendas.quantidade) AS total_vendas

FROM vendas AS vendas
INNER JOIN usuarios AS usuarios ON vendas.cod_usuario = usuarios.cod_usuario
WHERE usuarios.estado IN ('Minas Gerais', 'São Paulo')
GROUP BY YEAR(vendas.data_compra), MONTH(vendas.data_compra), usuarios.estado
ORDER BY ano, mes, usuarios.estado
""")

"""2) Quais são os usuários por Estado que mais compraram em todo o período analisado e qual foi o número de compras realizadas, a quantidade total de itens comprados e valor total pago por usuário?"""

q("""
WITH vendas_por_usuario AS (
    SELECT
    usuarios.cod_usuario
    ,usuarios.estado
    ,COUNT(*) AS total_compras
    ,SUM(vendas.quantidade) AS total_itens
    ,FORMAT_NUMBER(ROUND(SUM(vendas.valor),2),2) AS valor_total
    FROM vendas
    JOIN usuarios ON vendas.cod_usuario = usuarios.cod_usuario
    GROUP BY usuarios.cod_usuario, usuarios.estado
)
SELECT estado, cod_usuario, total_compras, total_itens, valor_total
FROM (
    SELECT *,
           RANK() OVER (PARTITION BY estado ORDER BY total_compras DESC, total_itens DESC, valor_total DESC) as rank
    FROM vendas_por_usuario
) ranked
WHERE ranked.rank = 1
ORDER BY estado
""")

"""3) Quais são os usuários que não fizeram nenhuma compra?"""

q("""
SELECT
  usuarios.cod_usuario
FROM usuarios
LEFT JOIN vendas ON usuarios.cod_usuario = vendas.cod_usuario
WHERE vendas.quantidade IS NULL
""")

"""4) Qual é o ticket médio (média de valor gasto) e o número total de usuários que fizeram pelo menos uma compra por faixa etária?"""

q("""
WITH total_gasto_por_usuario AS (
    SELECT
     vendas.cod_usuario
    ,SUM(vendas.valor) AS total_gasto
    FROM vendas
    GROUP BY vendas.cod_usuario
)
SELECT
usuarios.faixa_etaria
,FORMAT_NUMBER(ROUND(AVG(total_gasto_por_usuario.total_gasto), 2),2) AS ticket_medio
,COUNT(DISTINCT usuarios.cod_usuario) AS total_usuarios
FROM total_gasto_por_usuario
JOIN usuarios ON total_gasto_por_usuario.cod_usuario = usuarios.cod_usuario
GROUP BY usuarios.faixa_etaria
ORDER BY usuarios.faixa_etaria

""")

spark.stop()

"""# PySpark

**setup**:
"""

# Commented out IPython magic to ensure Python compatibility.
# %%bash
# mkdir bases_teste
# curl https://raw.githubusercontent.com/A3Data/bases_testes/main/bases_teste/produtos.csv -o bases_teste/produtos.csv
# curl https://raw.githubusercontent.com/A3Data/bases_testes/main/bases_teste/vendas.csv -o bases_teste/vendas.csv
# curl https://raw.githubusercontent.com/A3Data/bases_testes/main/bases_teste/usuarios.csv -o bases_teste/usuarios.csv

# Setup Spark Session
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("Atividade_Spark_DataFrames").getOrCreate()

def cria_tabela(path, nome_tabela):
    df = spark.read.csv(path, inferSchema=True, header=True)
    df.createOrReplaceTempView(nome_tabela)
    return df

usuarios = cria_tabela("bases_teste/usuarios.csv", "usuarios")
produtos = cria_tabela("bases_teste/produtos.csv", "produtos")
vendas = cria_tabela("bases_teste/vendas.csv", "vendas")

#amostras
usuarios.show(3, truncate = False)
produtos.show(3, truncate = False)
vendas.show(3, truncate = False)

"""Responda às perguntas a seguir utilizando **Spark DATAFRAMES**.

1) Qual foi o total de compras realizadas, o total de itens comprados e a receita total obtida em todo o período analisado?
"""

from pyspark.sql import functions as F

# Cálculo do total de compras, total de itens, e receita total:
resultado = vendas.agg(
    F.count(F.lit(1)).alias("Total_Compras"),
    F.sum("quantidade").alias("Total_Itens"),
    F.format_number(F.sum("valor"), 2).alias("Receita_Total")
)

resultado.show(truncate = False)

"""2) Quais são os 3 produtos mais comprados dos estados da região Sul e Sudeste, a quantidade de itens comprados, o valor total pago e a média de preço paga?"""

from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Listagem de Estados do Sul e Sudeste:
estados_sul_sudeste = ["Rio Grande do Sul", "Santa Catarina", "Paraná",
                       "São Paulo", "Rio de Janeiro", "Espírito Santo", "Minas Gerais"]

# Condição do JOIN entre as tabelas vendas , usuarios e produtos:
condicao_join = [vendas.cod_usuario == usuarios.cod_usuario, vendas.cod_produto == produtos.cod_produto]
df_join = vendas.join(usuarios, condicao_join[0]).join(produtos, condicao_join[1])

# Aplicando as condições de retorno solicitadas e filtradas por estado
df_agregacao = df_join.filter(usuarios.estado.isin(estados_sul_sudeste)) \
    .groupBy(produtos.nome_produto) \
    .agg(
        F.sum("quantidade").alias("Total_Itens"),
        F.format_number(F.sum("valor"), 2).alias("Valor_Total"),
        F.format_number(F.sum("valor") / F.sum("quantidade"), 2).alias("Preco_Medio")
    )

# Aplicando o conceito de window functions para rankeamento
windowSpec = Window.partitionBy().orderBy(F.desc("Total_Itens"))

# Aplicando a função de window functions e selecionando os 3 primeiros
top_produtos = df_agregacao.withColumn("rank", F.row_number().over(windowSpec)) \
    .filter(F.col("rank") <= 3)

top_produtos.show(truncate = False)

"""3) Para cada produto, quantos usuários fizeram pelo menos uma compra desse produto e qual é o valor mínimo e máximo pago por eles?"""

from pyspark.sql import functions as F

# dataframe com JOIN entre as tabelas vendas e produtos
df_join = vendas.join(produtos, vendas.cod_produto == produtos.cod_produto)

# Calculando o número de usuários distintos, valor mínimo e máximo pago por produto
resultado = df_join.groupBy(produtos.nome_produto) \
                   .agg(
                       F.countDistinct(vendas.cod_usuario).alias("Total_Usuarios"),
                       F.format_number(F.min(vendas.valor),2).alias("Valor_minimo"),
                       F.format_number(F.max(vendas.valor),2).alias("Valor_Maximo")
                   )

resultado.show(truncate = False)

"""4) Aplique um desconto de 10% em todas as vendas dos usuários que fizeram pelo menos 3 compras de produtos na mesma categoria, a partir da 4ª compra realizada. Exiba apenas os usuários que terão o desconto aplicado, mantendo todas as compras, o valor original e o valor com o desconto aplicado."""

from pyspark.sql import Window
from pyspark.sql.functions import col, when, count, lit, format_number

# INNER JOIN da tabela vendas com a tabela produtos:
df_join = vendas.join(produtos, "cod_produto")

# Definição do particionamento por window functions, por usuário e categoria
windowSpec = Window.partitionBy("cod_usuario", "categoria_produto").orderBy("data_compra")

# Contando o número de compras por usuário em cada categoria e marcando compras que se qualificam para desconto
df_compras = df_join.withColumn("num_compras_categoria", count(lit(1)).over(windowSpec)) \
                    .withColumn("qualifica_desconto", when(col("num_compras_categoria") >= 4, 1).otherwise(0))

# Calculando o valor com desconto e formatando as colunas númericas:
df_com_desconto = df_compras.withColumn("valor_com_desconto", when(col("qualifica_desconto") == 1, col("valor") * 0.9).otherwise(col("valor"))) \
                            .withColumn("valor", format_number(col("valor"), 2)) \
                            .withColumn("valor_produto", format_number(col("valor_produto"), 2)) \
                            .withColumn("valor_com_desconto", format_number(col("valor_com_desconto"), 2))

# Filtrando para exibir apenas os usuários que se qualificados para o desconto
df_resultado = df_com_desconto.filter(col("qualifica_desconto") == 1)

df_resultado.show(truncate=False)
#Fim dos desafios por hora

"""# FIM!"""

# Commented out IPython magic to ensure Python compatibility.
# #exportando para HTML
# %%shell
# jupyter nbconvert --to html /content/teste_engenharia_de_dados_v2_222.ipynb