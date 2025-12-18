from flask import Flask, jsonify
import pandas as pd
import numpy as np
import os
import traceback  # <-- Adicionado para capturar o erro detalhado

# Inicializa a aplicação Flask
app = Flask(__name__)

def calcular_reposicao():
    # --- NOVO BLOCO DE DIAGNÓSTICO ---
    # Este bloco 'try...except' agora envolve toda a função
    # para capturar qualquer erro possível durante a execução.
    try:
        # Define o caminho para os arquivos de dados
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path_nov = os.path.join(base_dir, 'Curva-abc-NOV.xlsx')
        path_17_dias = os.path.join(base_dir, 'abc-17-dias.xlsx')

        # Carrega os dados das planilhas
        df_nov = pd.read_excel(path_nov)
        df_17_dias = pd.read_excel(path_17_dias)

        # ETAPA 1: LIMPEZA DOS DADOS
        df_17_dias['estoque_atual'] = pd.to_numeric(df_17_dias['estoque_atual'], errors='coerce').fillna(0)
        df_17_dias = df_17_dias[df_17_dias['estoque_atual'] >= 0].copy()

        # ETAPA 2: CALCULAR A VELOCIDADE DE VENDAS (Venda Diária Média - VDM)
        df_17_dias['qtd_venda'] = pd.to_numeric(df_17_dias['qtd_venda'], errors='coerce').fillna(0)
        df_17_dias['VDM'] = df_17_dias['qtd_venda'] / 17
        df_17_dias['VDM'] = df_17_dias['VDM'].fillna(0)

        # ETAPA 3: DEFINIR O NÍVEL DE ESTOQUE ALVO
        periodo_cobertura = 12
        df_17_dias['Estoque_Alvo'] = df_17_dias['VDM'] * periodo_cobertura
        df_17_dias['Estoque_Alvo'] = df_17_dias['Estoque_Alvo'].apply(lambda x: np.ceil(x))

        # ETAPA 4: CALCULAR A QUANTIDADE A COMPRAR
        df_17_dias['Quantidade_a_Comprar'] = df_17_dias['Estoque_Alvo'] - df_17_dias['estoque_atual']
        df_17_dias['Quantidade_a_Comprar'] = df_17_dias['Quantidade_a_Comprar'].clip(lower=0)
        df_17_dias['Quantidade_a_Comprar'] = df_17_dias['Quantidade_a_Comprar'].astype(int)

        # GERAÇÃO DA SAÍDA
        lista_de_compras = df_17_dias[df_17_dias['Quantidade_a_Comprar'] > 0]
        colunas_finais = ['Código', 'Produto', 'Quantidade_a_Comprar']
        resultado = lista_de_compras[colunas_finais].sort_values(by='Quantidade_a_Comprar', ascending=False).to_dict(orient='records')
        
        return resultado

    except Exception as e:
        # --- ESTA É A MÁGICA DO DIAGNÓSTICO ---
        # Se qualquer erro ocorrer, ele será capturado aqui e retornado como uma mensagem detalhada.
        error_details = {
            "error_message": str(e),
            "traceback": traceback.format_exc()
        }
        return {"error": "Falha no processamento interno dos dados.", "details": error_details}


@app.route('/api/process', methods=['GET'])
def process_handler():
    resultado_final = calcular_reposicao()
    if 'error' in resultado_final:
        # Se a função retornar um erro, envie-o para o frontend com um status de erro do servidor
        return jsonify(resultado_final), 500
    
    return jsonify(resultado_final)
