from modules.ibge import consultar_ibge

url = (
    "https://servicodados.ibge.gov.br/api/v3/agregados/"
    "6579/periodos/2022/variaveis/9324?"
    "localidades=N6[4106902]"
)

dados = consultar_ibge(url)

print(dados)