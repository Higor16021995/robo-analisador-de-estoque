from flask import Flask, jsonify
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

@app.route('/api/process', methods=['GET'])
def process_handler():
    try:
        # --- A CORREÇÃO FINAL ESTÁ AQUI ---
        # O caminho agora aponta para o diretório correto no ambiente da Vercel.
        # Em vez de procurar na pasta local, ele procura na pasta raiz do projeto.
        path_recente = os.path.join(os.getcwd(), 'abc-17-dias.xlsx')

        # Carrega o arquivo essencial
        df = pd.read_excel(path_recente)

        # ETAPAS DE CÁLCULO (INALTERADAS E CORRETAS)
        df['estoque_atual'] = pd.to_numeric(df['estoque_atual'], errors='coerce').fillna(0)
        df['qtd_venda'] = pd.to_numeric(df['qtd_venda'], errors='coerce').fillna(0)
        df = df[df['estoque_atual'] >= 0].copy()

        df['VDM'] = df['qtd_venda'] / 17
        df['VDM'] = df['VDM'].fillna(0)

        periodo_cobertura = 12
        df['Estoque_Alvo'] = df['VDM'] * periodo_cobertura
        df['Estoque_Alvo'] = df['Estoque_Alvo'].apply(np.ceil)

        df['Quantidade_a_Comprar'] = df['Estoque_Alvo'] - df['estoque_atual']
        df['Quantidade_a_Comprar'] = df['Quantidade_a_Comprar'].clip(lower=0).astype(int)

        lista_de_compras = df[df['Quantidade_a_Comprar'] > 0]
        colunas_finais = ['Código', 'Produto', 'Quantidade_a_Comprar']
        resultado = lista_de_compras[colunas_finais].sort_values(by='Quantidade_a_Comprar', ascending=False).to_dict(orient='records')
        
        return jsonify(resultado)

    except FileNotFoundError:
        # Mensagem de erro aprimorada para o futuro
        error_msg = f"Arquivo 'abc-17-dias.xlsx' não foi encontrado. O sistema procurou no caminho: {os.getcwd()}"
        return jsonify({"error": "Configuração de Arquivo Incorreta.", "details": error_msg}), 404
    except Exception as e:
        return jsonify({"error": "Falha crítica no processamento dos dados.", "details": str(e)}), 500
