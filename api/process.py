from flask import Flask, jsonify
import pandas as pd
import numpy as np  # <-- MUDANÇA 1: Importamos a biblioteca numpy diretamente
import os

# Inicializa a aplicação Flask
app = Flask(__name__)

def calcular_reposicao():
    # Define o caminho para os arquivos de dados
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path_nov = os.path.join(base_dir, 'Curva-abc-NOV.xlsx')
        path_17_dias = os.path.join(base_dir, 'abc-17-dias.xlsx')

        df_nov = pd.read_excel(path_nov)
        df_17_dias = pd.read_excel(path_17_dias)
    except FileNotFoundError as e:
        return {'error': f"Arquivo de dados não encontrado. Detalhe: {e}. Verifique se as planilhas 'Curva-abc-NOV.xlsx' e 'abc-17-dias.xlsx' estão na pasta 'api'."}
    except Exception as e:
        return {'error': f"Erro ao ler as planilhas: {e}"}

    # ETAPA 1: LIMPEZA DOS DADOS
    df_17_dias['estoque_atual'] = pd.to_numeric(df_17_dias['estoque_atual'], errors='coerce').fillna(0)
    df_17_dias = df_17_dias[df_17_dias['estoque_atual'] >= 0].copy()

    # ETAPA 2: CALCULAR A VELOCIDADE DE VENDAS (Venda Diária Média - VDM)
    df_17_dias['VDM'] = df_17_dias['qtd_venda'] / 17
    df_17_dias['VDM'] = df_17_dias['VDM'].fillna(0)

    # ETAPA 3: DEFINIR O NÍVEL DE ESTOQUE ALVO
    periodo_cobertura = 12
    df_17_dias['Estoque_Alvo'] = df_17_dias['VDM'] * periodo_cobertura
    
    # --- MUDANÇA 2: CORREÇÃO DA LINHA DE CÓDIGO COM ERRO ---
    # Usamos np.ceil() diretamente, que é a forma correta e moderna.
    df_17_dias['Estoque_Alvo'] = df_17_dias['Estoque_Alvo'].apply(lambda x: np.ceil(x))

    # ETAPA 4: CALCULAR A QUANTIDADE A COMPRAR
    df_17_dias['Quantidade_a_Comprar'] = df_17_dias['Estoque_Alvo'] - df_17_dias['estoque_atual']
    df_17_dias['Quantidade_a_Comprar'] = df_17_dias['Quantidade_a_Comprar'].clip(lower=0)
    df_17_dias['Quantidade_a_Comprar'] = df_17_dias['Quantidade_a_Comprar'].astype(int)

    # GERAÇÃO DA SAÍDA
    lista_de_compras = df_17_dias[df_17_dias['Quantidade_a_Comprar'] > 0]
    colunas_finais = ['Código', 'Produto', 'Quantidade_a_Comprar']
    
    # Ordena a lista da maior para a menor quantidade a comprar para priorização
    resultado = lista_de_compras[colunas_finais].sort_values(by='Quantidade_a_Comprar', ascending=False).to_dict(orient='records')
    
    return resultado

@app.route('/api/process', methods=['GET'])
def process_handler():
    resultado_final = calcular_reposicao()
    if 'error' in resultado_final:
        # Retorna um erro 500 (Internal Server Error) com uma mensagem clara
        return jsonify(resultado_final), 500
    
    return jsonify(resultado_final)
