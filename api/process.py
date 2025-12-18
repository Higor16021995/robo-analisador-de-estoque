from http.server import BaseHTTPRequestHandler
import json
import pandas as pd

def analisar_estoque_dinamico(df_estoque, janela_movel=3, fator_seguranca=1.5):
    df_estoque = df_estoque.sort_values(by=['Produto', 'Mês']).reset_index(drop=True)
    df_estoque['Media_Movel_Estoque'] = df_estoque.groupby('Produto')['Estoque_Final'].transform(lambda x: x.rolling(window=janela_movel, min_periods=1).mean())
    df_estoque['Volatilidade_Estoque (Desvio_Padrão)'] = df_estoque.groupby('Produto')['Estoque_Final'].transform(lambda x: x.rolling(window=janela_movel, min_periods=1).std()).fillna(0)
    df_estoque['Estoque_Ideal_Dinamico'] = (df_estoque['Media_Movel_Estoque'] + (df_estoque['Volatilidade_Estoque (Desvio_Padrão)'] * fator_seguranca))
    cols_to_round = ['Media_Movel_Estoque', 'Volatilidade_Estoque (Desvio_Padrão)', 'Estoque_Ideal_Dinamico']
    for col in cols_to_round:
        df_estoque[col] = df_estoque[col].round(0).astype(int)
    return df_estoque

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        data = {
            'Mês': pd.to_datetime(['2023-01-01', '2023-02-01', '2023-03-01', '2023-01-01', '2023-02-01', '2023-03-01', '2023-01-01', '2023-02-01', '2023-03-01']),
            'Produto': ['Carrinho', 'Carrinho', 'Carrinho', 'Boneca', 'Boneca', 'Boneca', 'Bola', 'Bola', 'Bola'],
            'Estoque_Final': [ 500, 450, 600, 200, 210, 205, 20, 25, 10 ]
        }
        df_historico_estoque = pd.DataFrame(data)
        df_analisado = analisar_estoque_dinamico(df_historico_estoque)
        resultado_json = df_analisado.to_dict(orient='records')
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(resultado_json).encode('utf-8'))
        return
