from CocheModelo import RoomModel
import seaborn as sns
import matplotlib.pyplot as plt

# Lista para almacenar el total de movimientos de cada simulación
total_movements_each_simulation = []

# Ejecutar 100 simulaciones
for simulation in range(100):
    model = RoomModel(8, 20, 1, 1)  # Crear una nueva instancia del modelo
    for i in range(100):  # Ejecutar cada simulación por 100 pasos, por ejemplo
        model.step()

    # Obtener los datos finales de esta simulación
    movimientos_data = model.datacollector.get_model_vars_dataframe()
    total_movements = movimientos_data['Total Movements'].iloc[-1]
    total_movements_each_simulation.append(total_movements)

# Graficar los resultados
plt.figure(figsize=(10, 6))
sns.histplot(total_movements_each_simulation, kde=True)
plt.title("Distribución de Movimientos Totales en 100 Simulaciones")
plt.xlabel("Total de Movimientos")
plt.ylabel("Frecuencia")
plt.show()

#Otra gráfica
"""
plt.figure(figsize=(8, 6))
plt.plot(total_movements_each_simulation, 'o-', color='red')  # 'o-' crea puntos conectados por líneas
plt.title("Movimientos Totales en 100 Simulaciones Diferentes")
plt.xlabel("Número de Simulación")
plt.ylabel("Total de Movimientos")
plt.grid(True)
plt.show()
"""
