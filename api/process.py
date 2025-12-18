from flask import Flask, jsonify
import pandas as pd

# Cria a aplicação Flask. A Vercel vai procurar por esta variável 'app'.
app = Flask(__name__)

# A lógica de análise de estoque permanece a mesma.
def analisar_estoque_dinamico(df_estoque, janela_movel=3, fator_seguranca=1.5):
    df_estoque = df_estoque.sort_values(by=['Produto', 'Mês']).reset_index(drop=True)
    df_estoque['Media_Movel_Estoque'] = df_estoque.groupby('Produto')['Estoque_Final'].transform(lambda x: x.rolling(window=janela_movel, min_periods=1).mean())
    df_estoque['Volatilidade_Estoque (Desvio_Padrão)'] = df_estoque.groupby('Produto')['Estoque_Final'].transform(lambda x: x.rolling(window=janela_movel, min_periods=1).std()).fillna(0)
    df_estoque['Estoque_Ideal_Dinamico'] = (df_estoque['Media_Movel_Estoque'] + (df_estoque['Volatilidade_Estoque (Desvio_Padrão)'] * fator_seguranca))
    cols_to_round = ['Media_Movel_Estoque', 'Volatilidade_Estoque (Desvio_Padrão)', 'Estoque_Ideal_Dinamico']
    for col in cols_to_round:
        df_estoque[col] = df_estoque[col].round(0).astype(int)
    return df_estoque

# --- ROTA DA API ---
# Define o endereço que o botão vai chamar.
# A Vercel automaticamente direciona requisições para /api/process para esta função.
@app.route('/api/process', methods=['GET'])
def process_handler():
    # Cria os dados de simulação
    data = {
        'Mês': pd.to_datetime(['2023-01-01', '2023-02-01', '2023-03-01', '2023-01-01', '2023-02-01', '2023-03-01', '2023-01-01', '2023-02-01', '2023-03-01']),
        'Produto': ['Carrinho', 'Carrinho', 'Carrinho', 'Boneca', 'Boneca', 'Boneca', 'Bola', 'Bola', 'Bola'],
        'Estoque_Final': [ 500, 450, 600, 200, 210, 205, 20, 25, 10 ]
    }
    df_historico_estoque = pd.DataFrame(data)

    # Executa a análise
    df_analisado = analisar_estoque_dinamico(df_historico_estoque)
    
    # Converte o resultado para um dicionário Python
    resultado_dict = df_analisado.to_dict(orient='records')
    
    # Usa a função jsonify do Flask para criar uma resposta JSON perfeita
    return jsonify(resultado_dict)
