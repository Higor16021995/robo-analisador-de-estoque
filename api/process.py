from flask import Flask, jsonify
import pandas as pd
import os

# Inicializa a aplicação Flask
app = Flask(__name__)

def calcular_reposicao():
    # Define o caminho para os arquivos de dados
    # O Vercel executa o código a partir do diretório raiz, então precisamos construir o caminho para a pasta 'api'
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path_nov = os.path.join(base_dir, 'Curva-abc-NOV.xlsx')
    path_17_dias = os.path.join(base_dir, 'abc-17-dias.xlsx')

    # Carrega os dados das planilhas
    try:
        df_nov = pd.read_excel(path_nov)
        df_17_dias = pd.read_excel(path_17_dias)
    except FileNotFoundError as e:
        return {'error': f"Arquivo não encontrado: {e}. Verifique se as planilhas estão na pasta 'api'."}

    # --- ETAPA 1: LIMPEZA DOS DADOS ---
    # Garante que a coluna de estoque atual seja numérica e remove itens com estoque negativo.
    df_17_dias['estoque_atual'] = pd.to_numeric(df_17_dias['estoque_atual'], errors='coerce').fillna(0)
    df_17_dias = df_17_dias[df_17_dias['estoque_atual'] >= 0].copy()

    # --- ETAPA 2: CALCULAR A VELOCIDADE DE VENDAS (Venda Diária Média - VDM) ---
    # A VDM é calculada com base nos dados mais recentes (17 dias)
    df_17_dias['VDM'] = df_17_dias['qtd_venda'] / 17
    df_17_dias['VDM'] = df_17_dias['VDM'].fillna(0)

    # --- ETAPA 3: DEFINIR O NÍVEL DE ESTOQUE ALVO ---
    # Cobertura = 7 dias (ciclo de compra) + 5 dias (estoque de segurança) = 12 dias
    periodo_cobertura = 12
    df_17_dias['Estoque_Alvo'] = df_17_dias['VDM'] * periodo_cobertura
    # Arredonda para cima, pois não podemos ter frações de estoque
    df_17_dias['Estoque_Alvo'] = df_17_dias['Estoque_Alvo'].apply(lambda x: pd.np.ceil(x))

    # --- ETAPA 4: CALCULAR A QUANTIDADE A COMPRAR ---
    df_17_dias['Quantidade_a_Comprar'] = df_17_dias['Estoque_Alvo'] - df_17_dias['estoque_atual']
    
    # Regra de Negócio: Não comprar se o estoque já for suficiente.
    # A função clip(lower=0) define qualquer valor negativo como 0.
    df_17_dias['Quantidade_a_Comprar'] = df_17_dias['Quantidade_a_Comprar'].clip(lower=0)
    
    # Converte para inteiro, pois não podemos comprar frações de itens.
    df_17_dias['Quantidade_a_Comprar'] = df_17_dias['Quantidade_a_Comprar'].astype(int)

    # --- GERAÇÃO DA SAÍDA ---
    # Filtra apenas os itens que precisam de compra
    lista_de_compras = df_17_dias[df_17_dias['Quantidade_a_Comprar'] > 0]
    
    # Seleciona as colunas relevantes para a lista de compras
    colunas_finais = ['Código', 'Produto', 'Quantidade_a_Comprar']
    resultado = lista_de_compras[colunas_finais].to_dict(orient='records')
    
    return resultado

@app.route('/api/process', methods=['GET'])
def process_handler():
    # Chama a função principal que contém toda a lógica
    resultado_final = calcular_reposicao()
    
    # Retorna o resultado no formato JSON para a interface web
    if 'error' in resultado_final:
        return jsonify(resultado_final), 500
    
    return jsonify(resultado_final)
