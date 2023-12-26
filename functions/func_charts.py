import numpy as np
import matplotlib.pyplot as plt
import squarify as sqf
colores_I_G = ['#196F3D', '#E74C3C']
colormap_azules = plt.get_cmap('Blues')
colormap_rojos = plt.get_cmap('Reds')
colormap_verdes = plt.get_cmap('Greens')
colormap_lilas = plt.get_cmap('Purples')
color_min = 0.2
color_max = 0.7

def salary_tracing(df, ax):

    etiquetas = df['Fecha']
    valores = df['Saldo']

    # Ahora se van a graficar textos de información relativo a máximos y míminos
    valor_inicial = df['Saldo'].iloc[0]
    valor_final = df['Saldo'].iloc[-1]
    max_balance = 0
    min_balance = 0
    for i, valor in enumerate(valores):
        if (valor - valor_inicial) > max_balance:
            max_balance = int(valor - valor_inicial)
            pos_max_balance = i
        if (valor - valor_inicial) < min_balance:
            min_balance = int(valor - valor_inicial)
            pos_min_balance = i

    i_inicial = 0
    i_final = df['Saldo'].size - 1
    status = False
    for i, valor in enumerate(valores):
        if i == i_inicial:
            pass
        else:
            # Se evalúa qué dirección toma. Status True se usará para estados positivos, False para negativos
            if valor >= valor_inicial:
                change_status = status == False
                status = True
            else:
                change_status = status == True
                status = False

            if change_status == True:
                color = colores_I_G[1] if status == True else colores_I_G[0]
                ax.plot(etiquetas[i_inicial:i], valores[i_inicial:i], color=color)
                i_inicial = i - 1
            elif i == i_final:
                color = colores_I_G[0] if status == True else colores_I_G[1]
                ax.plot(etiquetas[i_inicial:i], valores[i_inicial:i], color=color)

    # Se añade información al gráfico

    # Saldo inicial
    ax.text(etiquetas.iloc[0], valores.iloc[0], f"Saldo Inicial: {int(valores[0])} €", va='top', ha='left',
             fontweight='bold', fontsize=10, color='black')
    # Máximo balance
    balance = int(valor_final - valor_inicial)
    ax.text(etiquetas.iloc[pos_max_balance], valores.iloc[pos_max_balance],
             f"Max. Balance: +{max_balance} €\nSaldo: {int(valores[pos_max_balance])} €", va='center', ha='right',
             fontweight='bold', fontsize=10, color='g')
    ax.scatter(etiquetas.iloc[pos_max_balance], valores.iloc[pos_max_balance], marker='o', color='none', edgecolor='g',
                s=100)
    # Mínimo balance
    ax.text(etiquetas.iloc[pos_min_balance], valores.iloc[pos_min_balance],
             f"Min Balance: {min_balance} €\nSaldo: {int(valores[pos_min_balance])} €", va='center', ha='right',
             fontweight='bold', fontsize=10, color='r')
    ax.scatter(etiquetas.iloc[pos_min_balance], valores.iloc[pos_min_balance], marker='o', color='none', edgecolor='r',
                s=100)
    # balance final
    color_balance = 'r' if balance < 0 else 'g'
    ax.text(etiquetas.iloc[-1], max(valores), f"Balance final: {balance} €\nSaldo Final: {int(valor_final)} €",
             va='top', ha='right', fontweight='bold', fontsize=10, color=color_balance)
    # Dibuja constante como la barrera entre balance negativo o positivo
    ax.axhline(valores[0], color='r', linestyle='--', label='Límite Ahorro / Gasto')
    #ax.set_xlabel('Fecha')
    ax.set_ylabel('€')
    ax.legend(loc='lower left')
    ax.set_title('Evolución del Saldo')

def monthly_comparison(df_ingresos, df_gastos, ax):
    df_ingresos['mes'] = df_ingresos['Fecha'].apply(lambda fecha: fecha.month)
    df_gastos['mes'] = df_gastos['Fecha'].apply(lambda fecha: fecha.month)
    filtro_gastos = df_gastos.groupby('mes')['Importe'].sum()
    filtro_ingresos = df_ingresos.groupby('mes')['Importe'].sum()
    etiquetas_gastos = list(filtro_gastos.index)
    valores_gastos = list(filtro_gastos.values)
    etiquetas_ingresos = list(filtro_ingresos.index)
    valores_ingresos = list(filtro_ingresos.values)

    ancho_barra = 0.35
    posicion_ingresos = np.arange(len(etiquetas_ingresos))
    posicion_gastos = posicion_ingresos + ancho_barra

    # (valores, labels = etiquetas, colors = colores, startangle = 90, autopct=lambda p: '{:.0f} €'.format(p * sum(valores) / 100), wedgeprops = {'linewidth': 1, 'edgecolor': 'grey'})
    ax.bar(posicion_ingresos, valores_ingresos, color=colores_I_G[0], width=ancho_barra, label='Ingresos',
            edgecolor='white')
    ax.bar(posicion_gastos, valores_gastos, color=colores_I_G[1], width=ancho_barra, label='Gastos', edgecolor='white')

    # Se cambian los nombre de las etiquetas del eje X
    ax.set_xticks(posicion_ingresos + ancho_barra / 2, etiquetas_gastos, ha='center')

    # Se añaden etiquetas a cada barra mostrando su valor (ingresos)
    for i, valor in enumerate(valores_ingresos):
        ax.text(posicion_ingresos[i], valor + 0.1, str(int(valor)), color=colores_I_G[0], ha='center', va='bottom',
                 fontdict={'weight': 'bold', 'size': 12})

    # Se añaden etiquetas a cada barra mostrando su valor (gastos)
    for i, valor in enumerate(valores_gastos):
        ax.text(posicion_gastos[i], valor + 0.1, str(int(valor)), color=colores_I_G[1], ha='center', va='bottom',
                 fontdict={'weight': 'bold', 'size': 12})

    ax.set_title('Ingresos VS Gastos Mensual')
    ax.set_ylabel("€")
    #ax.set_xlabel('Months')
    ax.legend()

    #df_ingresos.drop('mes', inplace=True, axis=1)
    #df_gastos.drop('mes', inplace=True, axis=1)

def generate_trendline(valores):
    x = np.linspace(0, len(valores), len(valores))
    y = valores
    #Obtener coeficientes de la ecuación recta de tendencia
    coef = np.polyfit(x, y, 1)  # El último parámetro es el grado del polinomio, 1 para una línea recta
    # Crear una función polinómica con los coeficientes calculados
    polynomial = np.poly1d(coef)
    #Devuelve los valores de acuerdo a dicha funcion
    y = polynomial(x)
    return y

def acum_comparison(df_ingresos, df_gastos, ax):
    #Gastos
    etiquetas = df_gastos['Fecha']
    valores = df_gastos['Importe'].cumsum()
    ax.plot(etiquetas, valores, label = "Gastos Acum.", color = colores_I_G[1])
    #Calcular tendencias
    y = generate_trendline(valores)
    #Extraemos el primer y último dato de los valores y etiquetas para pintar una recta perfecta
    etiquetas_recta = [etiquetas.iloc[0], etiquetas.iloc[-1]]
    y_recta = [y[0], y[-1]]
    ax.plot(etiquetas_recta, y_recta, label = "Tendencia gastos", color = 'r', linewidth = 0.8, linestyle = '--')

    #Ingresos
    etiquetas = df_ingresos['Fecha']
    valores = df_ingresos['Importe'].cumsum()
    ax.plot(etiquetas, valores, label = "Ingresos Acum.", color = colores_I_G[0])
    #Calcular tendencias
    y = generate_trendline(valores)
    #Extraemos el primer y último dato de los valores y etiquetas para pintar una recta perfecta
    etiquetas_recta = [etiquetas.iloc[0], etiquetas.iloc[-1]]
    y_recta = [y[0], y[-1]]
    #Se pinta la linea de tendencia
    ax.plot(etiquetas_recta, y_recta, label = "Tendencia Ingresos", color = 'g', linewidth = 0.8, linestyle = '--')

    ax.set_title("Acumulado Ingresos vs Gastos")
    #ax.set_xlabel("Fecha")
    ax.set_ylabel("€")
    ax.legend()

def pie_chart(ax, valores, etiquetas, titulo, unidad = '€', colormap = plt.get_cmap('cividis')):
    # Se definen los colores
    num_colores = len(valores)

    colores = colormap(np.linspace(color_max, color_min, num_colores))
    # Se pinta la gráfica
    autopcts, texts, autotexts = ax.pie(valores, labels=etiquetas, autopct='%1.1f%%',
                                         wedgeprops={'linewidth': 1, 'edgecolor': 'white', 'width': 0.3},
                                         colors=colores, startangle=45)
    # Se "eliminan" las etiquetas que cumplen con cierto criterio
    for i in range(len(autotexts)):  # esto me servirá para iterar las veces necesarias para los tres parámetros
        valor_porc = float(autotexts[i].get_text().strip('%'))
        if valor_porc < 2:
            autotexts[i].set_color('white')
            texts[i].set_color('white')
    ax.set_title(titulo, loc='center', fontsize = 10)
    # Se añade un texto con el valor de la suma total
    suma_valores = "{:,}".format(int(sum(valores)))
    ax.text(0, -1.3, f'Porcentajes sobre {suma_valores} {unidad}', ha='center',
             va='center', fontdict={'weight': 'bold', 'size': 10})

def barh_chart(ax, valores, etiquetas, titulo, unidad = '€', colormap = plt.get_cmap('cividis')):
    #Se definen los colores
    num_colores = len(valores)
    colores = colormap(np.linspace(color_max, color_min, num_colores))
    ax.barh(etiquetas, valores, color = colores)
    #ax.set_ylabel('Concepto')
    ax.set_xlabel(unidad)
    ax.set_title(titulo, fontsize = 10)
    #Se añaden los valores de cada barra en forma de texto
    for i, valor in enumerate(valores):
        ax.text(valor / 2, i, int(valor), va = 'center', ha = 'center')


def squared_chart(ax, valores, etiquetas, n_dias, titulo, unidad = '€', colormap=plt.get_cmap('viridis')):
    # Se definen los colores
    num_colores = len(valores)
    colores = colormap(np.linspace(color_max, color_min, num_colores))
    # Se modifican las etiquetas para añadir, además, el valor

    etiquetas_valor = [f"{etiqueta}\n{int(valores[i])}\n{int((valores[i] / n_dias) * 30)} € / mes" for i, etiqueta in
                       enumerate(etiquetas)]
    # Se grafica
    sqf.plot(sizes=valores, label=etiquetas_valor, ax = ax, alpha=0.7, color=colores, text_kwargs={'fontsize': 8})
    ax.set_title(titulo, fontsize = 10)
    ax.axis("off")