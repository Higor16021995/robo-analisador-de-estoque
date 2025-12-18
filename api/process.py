from flask import Flask, jsonify
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

@app.route('/api/process', methods=['GET'])
def process_handler():
    try:
        # ETAPA 0: CARREGAR APENAS O ARQUIVO ESSENCIAL
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path_recente = os.path.join(base_dir, 'abc-17-dias.xlsx')
        df = pd.read_excel(path_recente)

        # ETAPA 1: LIMPEZA ROBUSTA DOS DADOS
        df['estoque_atual'] = pd.to_numeric(df['estoque_atual'], errors='coerce').fillna(0)
        df['qtd_venda'] = pd.to_numeric(df['qtd_venda'], errors='coerce').fillna(0)
        df = df[df['estoque_atual'] >= 0].copy()

        # ETAPA 2: CÁLCULO DA VELOCIDADE DE VENDAS (VDM)
        df['VDM'] = df['qtd_venda'] / 17
        df['VDM'] = df['VDM'].fillna(0)

        # ETAPA 3: CÁLCULO DO ESTOQUE ALVO
        periodo_cobertura = 12  # 7 dias (ciclo) + 5 dias (segurança)
        df['Estoque_Alvo'] = df['VDM'] * periodo_cobertura
        df['Estoque_Alvo'] = df['Estoque_Alvo'].apply(np.ceil)

        # ETAPA 4: CÁLCULO DA NECESSIDADE DE COMPRA
        df['Quantidade_a_Comprar'] = df['Estoque_Alvo'] - df['estoque_atual']
        df['Quantidade_a_Comprar'] = df['Quantidade_a_Comprar'].clip(lower=0).astype(int)

        # GERAÇÃO DA SAÍDA
        lista_de_compras = df[df['Quantidade_a_Comprar'] > 0]
        colunas_finais = ['Código', 'Produto', 'Quantidade_a_Comprar']
        resultado = lista_de_compras[colunas_finais].sort_values(by='Quantidade_a_Comprar', ascending=False).to_dict(orient='records')
        
        return jsonify(resultado)

    except FileNotFoundError:
        return jsonify({"error": "Arquivo 'abc-17-dias.xlsx' não encontrado na pasta 'api'."}), 404
    except Exception as e:
        # Se um erro ainda ocorrer, ele será capturado e retornado de forma estruturada.
        return jsonify({"error": "Falha crítica no processamento dos dados.", "details": str(e)}), 500
