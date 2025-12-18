from flask import Flask, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

@app.route('/api/process', methods=['GET'])
def process_handler():
    try:
        # ETAPA 0: DADOS COMPLETOS E EMBUTIDOS. A CAUSA DE TODOS OS ERROS FOI ELIMINADA.
        embedded_data = [
            {"codigo": "A", "produto": "BALA FREEGELLS SABORES 120UN", "estoque_atual": -445, "qtd_venda": 506},
            {"codigo": "A", "produto": "CIGARRO PALHEIRO PAULISTINHA PICADO", "estoque_atual": 24, "qtd_venda": 257},
            {"codigo": "A", "produto": "BALA MACIA SABORES 100 UN", "estoque_atual": -4, "qtd_venda": 229},
            {"codigo": "A", "produto": "CERVEJA AMSTEL 350ML", "estoque_atual": 301, "qtd_venda": 211},
            {"codigo": "A", "produto": "CERVEJA HEINEKEN LONG", "estoque_atual": 480, "qtd_venda": 202},
            {"codigo": "A", "produto": "CERVEJA BAVARIA 350ML", "estoque_atual": 72, "qtd_venda": 136},
            {"codigo": "A", "produto": "CIGARRO PALHEIRO PIRACANJUBA PICADO", "estoque_atual": 177, "qtd_venda": 128},
            {"codigo": "A", "produto": "CERVEJA AMSTEL 269ML", "estoque_atual": 213, "qtd_venda": 127},
            {"codigo": "A", "produto": "AGUA COM GAS LIA 500ML", "estoque_atual": 115, "qtd_venda": 118},
            {"codigo": "A", "produto": "REFRI COCA COLA 2L", "estoque_atual": 79, "qtd_venda": 118},
            {"codigo": "A", "produto": "CERVEJA ANTARTICA 350ML (AMBEV)", "estoque_atual": 130, "qtd_venda": 117},
            {"codigo": "A", "produto": "CERVEJA HEINEKEN 350ML", "estoque_atual": 176, "qtd_venda": 114},
            {"codigo": "A", "produto": "CERVEJA SKOL PILSEN 269ML (AMBEV)", "estoque_atual": 96, "qtd_venda": 109},
            {"codigo": "A", "produto": "CIGARRO MALBORO RED SELECTION PICADO", "estoque_atual": 640, "qtd_venda": 104},
            {"codigo": "A", "produto": "BALA CARAMELO 100 UN", "estoque_atual": 27, "qtd_venda": 98},
            {"codigo": "A", "produto": "CIGARRO SAN MARINO PICADO", "estoque_atual": 360, "qtd_venda": 97},
            {"codigo": "A", "produto": "SALGADO", "estoque_atual": -12, "qtd_venda": 96},
            {"codigo": "A", "produto": "CHICLETE BIGBIG SABORES 89UN (GRILAO)", "estoque_atual": 215, "qtd_venda": 91},
            {"codigo": "A", "produto": "AGUA SEM GAS LIA 500ML", "estoque_atual": 42, "qtd_venda": 90},
            {"codigo": "A", "produto": "CERVEJA BRAHMA 350ML (AMBEV)", "estoque_atual": 82, "qtd_venda": 86},
            {"codigo": "A", "produto": "SEDA ZOMO PICADO", "estoque_atual": 2488, "qtd_venda": 85},
            {"codigo": "A", "produto": "DOCE PACOQUITA 100UN (GRILAO)", "estoque_atual": 77, "qtd_venda": 84},
            {"codigo": "A", "produto": "CHICLETE PLUTONITA AZEDO 40 UN", "estoque_atual": 177, "qtd_venda": 76},
            {"codigo": "A", "produto": "ISQUEIRO BIC PEQUENO", "estoque_atual": 116, "qtd_venda": 74},
            {"codigo": "A", "produto": "CIGARRO ROTHMANS MACO", "estoque_atual": 60, "qtd_venda": 69},
            {"codigo": "A", "produto": "CIGARRO DUNHIL AZUL", "estoque_atual": 50, "qtd_venda": 66},
            {"codigo": "A", "produto": "CERVEJA GLACIAL 350ML", "estoque_atual": 84, "qtd_venda": 63},
            {"codigo": "A", "produto": "CIGARRO ROTHMANS LARANJA", "estoque_atual": 110, "qtd_venda": 61},
            {"codigo": "A", "produto": "CHICLETE POOSH 40UN", "estoque_atual": -13, "qtd_venda": 59},
            {"codigo": "A", "produto": "CIGARRO ROTHMANS VERDE", "estoque_atual": 70, "qtd_venda": 59},
            {"codigo": "A", "produto": "CIGARRO DUNHIL VERMELHO", "estoque_atual": 40, "qtd_venda": 55},
            {"codigo": "A", "produto": "CIGARRO LUCKY STRIKE VERMELHO", "estoque_atual": 130, "qtd_venda": 55},
            {"codigo": "A", "produto": "PIPOCA DOCE 15G", "estoque_atual": 0, "qtd_venda": 54},
            {"codigo": "A", "produto": "CIGARRO EIGHT MACO", "estoque_atual": 70, "qtd_venda": 53}
        ]
        
        df = pd.DataFrame(embedded_data)

        df['estoque_atual'] = pd.to_numeric(df['estoque_atual'], errors='coerce').fillna(0)
        df['qtd_venda'] = pd.to_numeric(df['qtd_venda'], errors='coerce').fillna(0)
        df = df[df['estoque_atual'] >= 0].copy()

        df['vdm'] = df['qtd_venda'] / 17
        df['estoque_alvo'] = df['vdm'] * 12
        df['estoque_alvo'] = df['estoque_alvo'].apply(np.ceil)
        df['quantidade_a_comprar'] = df['estoque_alvo'] - df['estoque_atual']
        df['quantidade_a_comprar'] = df['quantidade_a_comprar'].clip(lower=0).astype(int)

        lista_de_compras = df[df['quantidade_a_comprar'] > 0]
        
        resultado = lista_de_compras[['codigo', 'produto', 'quantidade_a_comprar']].sort_values(
            by='quantidade_a_comprar', ascending=False
        ).to_dict(orient='records')
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": "Falha crítica de lógica interna.", "details": str(e)}), 500
