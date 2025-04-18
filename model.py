from pathlib import Path

import numpy as np

import mesa
from agents import SugarAgent
## Using experimental cell space for this model that enforces von Neumann neighborhoods
from mesa.experimental.cell_space import OrthogonalVonNeumannGrid
## Use experimental space feature that allows us to save sugar as a property of the grid spaces
from mesa.experimental.cell_space.property_layer import PropertyLayer

class SugarScapeModel(mesa.Model):
    def calc_ratio(self):
        '''
        Helper function to calculate the ratio of innovating agents to total population of agents
        '''
        total = len(self.agents)
        innovating = len([a for a in self.agents if a.affiliation == 0])
        return innovating / total
    def calc_gini(self):
        '''
        Helper function to calculate Gini coefficient, used in plot
        '''
        agent_sugars = [a.sugar for a in self.agents]
        sorted_sugars = sorted(agent_sugars)
        n = len(sorted_sugars) 
        den = (n * sum(sorted_sugars))
        x = sum(el * (n - ind) for ind, el in enumerate(sorted_sugars)) / den
        return 1 + (1 / n) - 2 * x
    def calc_avg_tech(self):
        '''
        Helper function to calculate the average technology level among agents who can innovate
        '''
        agent_tech = [a.tech for a in self.agents if a.affiliation == 0]
        return sum(agent_tech) / len(agent_tech)
    ## Define initiation, inherit seed property from parent class
    def __init__(
        self,
        width = 50,
        height = 50,
        initial_population=200,
        endowment_min=25,
        endowment_max=50,
        metabolism_min=1,
        metabolism_max=5,
        vision_min=1,
        vision_max=5,
        tech_min = 1, # minimum technology level which all agents start with
        tech_bottleneck = 5, # define bottleneck tech level(maximum technology level achievable in this implementation)
        reduction_scale = 0.9, # reduction scale to metabolism if innovation happens
        innovation_difficulty = 0.00001, # how difficult innocation is for one agent with 1 unit of sugar
        seed = None
    ):
        super().__init__(seed=seed)
        ## Instantiate model parameters
        self.reduction_scale = float(reduction_scale) #initialize reduction scale for model
        self.innovation_difficulty = float(innovation_difficulty) #initialize innovation difficulty for model
        self.tech_bottleneck = tech_bottleneck #initialize max tech level for model
        self.width = width
        self.height = height
        ## Set model to run continuously
        self.running = True
        ## Create grid
        self.grid = OrthogonalVonNeumannGrid(
            (self.width, self.height), torus=False, random=self.random
        )
        ## Define datacollector, which calculates current Gini coefficient, average tech level, 
        # and ratio of agents in two affiliations
        self.datacollector = mesa.DataCollector(
            model_reporters = {"Gini": self.calc_gini, "Tech": self.calc_avg_tech, "Ratio": self.calc_ratio}
        )
        ## Import sugar distribution from raster, define grid property
        self.sugar_distribution = np.genfromtxt(Path(__file__).parent / "sugar-map.txt")
        self.grid.add_property_layer(
            PropertyLayer.from_data("sugar", self.sugar_distribution)
        )
        ## Create agents, give them random properties, and place them randomly on the map
        SugarAgent.create_agents(
            self,
            initial_population,
            self.random.choices(self.grid.all_cells.cells, k=initial_population),
            sugar=self.rng.integers(
                endowment_min, endowment_max, (initial_population,), endpoint=True
            ),
            metabolism=self.rng.integers(
                metabolism_min, metabolism_max, (initial_population,), endpoint=True
            ),
            vision=self.rng.integers(
                vision_min, vision_max, (initial_population,), endpoint=True
            ),
            tech=[tech_min] * initial_population,
            affiliation = self.rng.integers(
                0, 1, (initial_population,), endpoint=True
            )
        )
        ## Initialize datacollector
        self.datacollector.collect(self)
    ## Define step: Sugar grows back at constant rate of 1, all agents move, 
    # some agents share, then all agents consume, then all see if they die, 
    # some potentially innovate. Then model calculated Gini coefficient, ratio, 
    # and average tech level among innovating agets.
    def step(self):
        self.grid.sugar.data = np.minimum(
            self.grid.sugar.data + 1, self.sugar_distribution
        )
        self.agents.shuffle_do("move")
        # agents with non-one tech level interact with one of their randomly selected 
        # same-affiliation neighbor to align techology level
        self.agents.shuffle_do("share") 
        self.agents.shuffle_do("gather_and_eat")
        self.agents.shuffle_do("see_if_die")
        # innovating agents with sugar level sufficient for one future step attempt innovation
        self.agents.shuffle_do("innovate")
        self.datacollector.collect(self)
    
