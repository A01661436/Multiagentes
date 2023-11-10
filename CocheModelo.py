import mesa
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import random

class Banqueta(Agent):
    """Un obstáculo que representa una banqueta."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

class CustomAgent(Agent):
    """Un agente con movimiento limitado y detección de colisiones."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.state = 'normal'  # Estado inicial normal
        self.movements = 0

    def move(self):
        # El agente elige una dirección para moverse
        # El agente elige una dirección para moverse
        current_x, current_y = self.pos
        grid_width, grid_height = self.model.grid.width, self.model.grid.height
        choices = [(current_x, (current_y + 1) % grid_height)]  # al frente, toroidal

        if current_x > 2:  # puede moverse a la izquierda
            choices.append(((current_x - 1) % grid_width, (current_y + 1) % grid_height))
        if current_x < 5:  # puede moverse a la derecha
            choices.append(((current_x + 1) % grid_width, (current_y + 1) % grid_height))

        # Probabilidad de fallo
        if self.random.random() < 0.1:  # Supongamos un 10% de probabilidad de fallo
            choices = [(current_x + 1, current_y + 1)]  # Movimiento incorrecto

        # Intentar moverse a una celda libre
        self.random.shuffle(choices)  # Aleatorizar el orden de las opciones
        for new_position in choices:
            this_cell = self.model.grid.get_cell_list_contents([new_position])
            if not any(isinstance(obj, Banqueta) for obj in this_cell):
                # Mueve al agente si la celda está libre
                self.model.grid.move_agent(self, new_position)
                self.movements += 1  # Incrementar el contador de movimientos
                break

    def step(self):
        if self.state == 'choque':  # Si ha chocado, no se mueve
            return
        self.move()

class FastAgent(CustomAgent):
    """Un agente que se mueve rápidamente en línea recta hacia adelante."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def move(self):
        # El agente solo se mueve en línea recta hacia adelante.
        grid_height = self.model.grid.height
        next_moves = [(self.pos[0], (self.pos[1] + 1) % grid_height)]  # Solo hacia adelante
        for new_position in next_moves:
            this_cell = self.model.grid.get_cell_list_contents([new_position])
            if not any(isinstance(obj, Banqueta) for obj in this_cell):
                # Mueve al agente si la celda está libre
                self.model.grid.move_agent(self, new_position)
                self.movements += 1  # Incrementar el contador de movimientos
                break  # Si se ha movido, no necesita revisar más posiciones

    def step(self):
        super().step()

class RoomModel(Model):
    """Modelo que representa la habitación con agentes."""
    def __init__(self, width, height, initial_agents, fast_agents):
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.running = True
        self.current_id = 0
        self.collisions = 0
        
        # Crear banquetas (obstáculos) y colocarlas en el grid
        for cell in [(x, y) for x in range(2) for y in range(height)] + \
                     [(x, y) for x in range(6, 8) for y in range(height)]:
            banqueta = Banqueta(self.next_id(), self)
            self.grid.place_agent(banqueta, cell)

        # Coloca un FastAgent en una posición fija
        fixed_position_fast_agent = (2, 0)  # Puedes ajustar esta posición
        fast_agent = FastAgent(self.next_id(), self)
        self.grid.place_agent(fast_agent, fixed_position_fast_agent)
        self.schedule.add(fast_agent)

        # Coloca un CustomAgent en una posición fija diferente
        fixed_position_custom_agent = (4, 0)  # Puedes ajustar esta posición
        custom_agent = CustomAgent(self.next_id(), self)
        self.grid.place_agent(custom_agent, fixed_position_custom_agent)
        self.schedule.add(custom_agent)

        # Coloca un FastAgent en una posición fija diferente
        fixed_position_fast_agent1 = (5, 0)  # Primera posición fija para CustomAgent
        fast_agent1 = FastAgent(self.next_id(), self)
        self.grid.place_agent(fast_agent1, fixed_position_fast_agent1)
        self.schedule.add(fast_agent1)

        # Coloca un segundo CustomAgent en otra posición fija diferente
        fixed_position_custom_agent2 = (3, 0)  # Segunda posición fija para CustomAgent
        custom_agent2 = CustomAgent(self.next_id(), self)
        self.grid.place_agent(custom_agent2, fixed_position_custom_agent2)
        self.schedule.add(custom_agent2)

        self.datacollector = mesa.DataCollector(
            model_reporters={"Total Movements": self.compute_total_movements}
        )

    def check_collisions(self):
        """Verifica si hay colisiones después de que todos los agentes se hayan movido."""
        total_agents = 0
        collided_agents = 0

        for agent in self.schedule.agents:
            if isinstance(agent, (CustomAgent, FastAgent)):
                total_agents += 1
                cellmates = self.grid.get_cell_list_contents(agent.pos)
                if len(cellmates) > 1:
                    collided_agents += 1
                    for cellmate in cellmates:
                        if cellmate is not agent:
                            agent.state = 'choque'
                            cellmate.state = 'choque'

        # Si todos los agentes han chocado, detén la simulación
        if total_agents > 0 and collided_agents == total_agents:
            self.running = False

    @property
    def compute_collisions(self):
        """Devuelve el total de choques que han ocurrido."""
        return self.collisions
    
    def compute_total_movements(self):
        """Calcula el total de movimientos de todos los agentes."""
        return sum(agent.movements for agent in self.schedule.agents if isinstance(agent, (CustomAgent, FastAgent)))

    def next_id(self):
        """Genera un ID único para cada nuevo agente."""
        self.current_id += 1
        return self.current_id

    def is_cell_empty(self, x, y):
        """Verifica si la celda en (x, y) está vacía."""
        cell_contents = self.grid.get_cell_list_contents([(x, y)])
        return len(cell_contents) == 0

    def step(self):
        """Avanza un paso en la simulación."""
        self.schedule.step()  # Avanza todos los agentes
        self.check_collisions()  # Verifica colisiones
        self.datacollector.collect(self)  # Recoge los datos después de las colisiones