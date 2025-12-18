from flask import Flask, jsonify
import pandas as pd
import numpy as np
import os

# Inicializa a aplicação Flask
app = Flask(__name__)

def calcular_reposicao():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path_nov = os.path.join(base_dir, 'Curva-abc-NOV.xlsx')
        path_17_dias = os.path.join(base_dir, 'abc-17-dias.xlsx')

        df_nov = pd.read_excel(path_nov)
        df_17_dias = pd.read_excel(path_17_dias)

        df_17_dias['estoque_atual'] = pd.to_numeric(df_17_dias['estoque_atual'], errors='coerce').fillna(0)
        df_17_dias = df_17_dias[df_17_dias['estoque_atual'] >= 0].copy()

        df_17_dias['qtd_venda'] = pd.to_numeric(df_17_dias['qtd_venda'], errors='coerce').fillna(0)
        df_17_dias['VDM'] = df_17_dias['qtd_venda'] / 17
        df_17_dias['VDM'] = df_17_dias['VDM'].fillna(0)

        periodo_cobertura = 12
        df_17_dias['Estoque_Alvo'] = df_17_dias['VDM'] * periodo_cobertura
        df_17_dias['Estoque_Alvo'] = df_17_dias['Estoque_Alvo'].apply(lambda x: np.ceil(x))

        df_17_dias['Quantidade_a_Comprar'] = df_17_dias['Estoque_Alvo'] - df_17_dias['estoque_atual']
        df_17_dias['Quantidade_a_Comprar'] = df_17_dias['Quantidade_a_Comprar'].clip(lower=0)
        df_17_dias['Quantidade_a_Comprar'] = df_17_dias['Quantidade_a_Comprar'].astype(int)

        lista_de_compras = df_17_dias[df_17_dias['Quantidade_a_Comprar'] > 0]
        colunas_finais = ['Código', 'Produto', 'Quantidade_a_Comprar']
        resultado = lista_de_compras[colunas_finais].sort_values(by='Quantidade_a_Comprar', ascending=False).to_dict(orient='records')
        
        return resultado

    except Exception as e:
        # Este bloco agora só serve como uma segurança final, mas o erro principal foi resolvido.
        return {"error": "Ocorreu uma falha inesperada durante o cálculo.", "details": str(e)}


@app.route('/api/process', methods=['GET'])
def process_handler():
    resultado_final = calcular_reposicao()
    if 'error' in resultado_final:
        return jsonify(resultado_final), 500
    
    return jsonify(resultado_final)
