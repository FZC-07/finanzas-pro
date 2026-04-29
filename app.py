from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

def calcular_roic(nopat, capital):
    return round(nopat / capital, 4) if capital != 0 else 0

def flujo_libre(flujo_operativo, capex):
    return round(flujo_operativo - capex, 2)

def rotacion_inventario(costo_ventas, inventario):
    return round(costo_ventas / inventario, 2) if inventario != 0 else 0

def dias_inventario(rotacion):
    return round(365 / rotacion, 2) if rotacion != 0 else 0

def pago_proveedores(cxp, compras):
    return round((cxp / compras) * 365, 2) if compras != 0 else 0

def interpretar(roic, flujo, dias_inv):
    r = []
    if roic < 0.08: r.append("Mejora la rentabilidad")
    if flujo < 0: r.append("Flujo negativo")
    if dias_inv > 120: r.append("Inventario alto")
    if not r: r.append("Empresa saludable")
    return r

def analizar(data):
    roic = calcular_roic(data['nopat'], data['capital'])
    flujo = flujo_libre(data['flujo_operativo'], data['capex'])
    rotacion = rotacion_inventario(data['costo_ventas'], data['inventario'])
    dias_inv = dias_inventario(rotacion)
    pago = pago_proveedores(data['cxp'], data['compras'])
    return {"roic":roic,"flujo":flujo,"rotacion":rotacion,"dias_inv":dias_inv,"pago":pago,"recomendaciones":interpretar(roic,flujo,dias_inv)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analisis', methods=['POST'])
def analisis():
    data = {k: float(v) for k, v in request.form.items()}
    return render_template('resultados.html', **analizar(data))

@app.route('/excel', methods=['POST'])
def excel():
    file = request.files['file']
    df = pd.read_excel(file)
    resultados = []
    for _, row in df.iterrows():
        data = row.to_dict()
        res = analizar(data)
        res['empresa'] = data.get('empresa','Empresa')
        resultados.append(res)
    return render_template('comparacion.html', resultados=resultados)

if __name__ == '__main__':
    app.run()
