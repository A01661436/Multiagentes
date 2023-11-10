from CocheModelo import RoomModel, CustomAgent, Banqueta, FastAgent, mesa
import pandas as pd
import matplotlib.pyplot as plt

def agent_portrayal(agent):
    if isinstance(agent, (CustomAgent, FastAgent)) and agent.state == 'choque':
        portrayal = {"Shape": "circle", "Color": "green", "Filled": "true", "Layer": 1, "r": 0.5}
    elif isinstance(agent, FastAgent):
        portrayal = {"Shape": "circle", "Color": "blue", "Filled": "true", "Layer": 1, "r": 0.5}
    elif isinstance(agent, CustomAgent):
        portrayal = {"Shape": "circle", "Color": "red", "Filled": "true", "Layer": 1, "r": 0.5}
    elif isinstance(agent, Banqueta):
        portrayal = {"Shape": "rect", "Color": "grey", "Filled": "true", "Layer": 0, "w": 1, "h": 1}
    else:
        portrayal = {"Shape": "rect", "Color": "black", "Filled": "false", "Layer": 0, "w": 1, "h": 1}
    return portrayal

grid = mesa.visualization.CanvasGrid(agent_portrayal, 8, 20, 500, 500)

chart = mesa.visualization.ChartModule([{"Label": "Total Movements", "Color": "Blue"}],
                    data_collector_name='datacollector')

server = mesa.visualization.ModularServer(RoomModel,
                       [grid, chart],
                       "Room Model",
                       {"width": 8, "height": 20, "initial_agents": 2, "fast_agents": 2})

server.port = 8521
server.launch()