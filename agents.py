import math
## Using experimental agent type with native "cell" property that saves its current position in cellular grid
from mesa.experimental.cell_space import CellAgent

## Helper function to get distance between two cells
def get_distance(cell_1, cell_2):
    x1, y1 = cell_1.coordinate
    x2, y2 = cell_2.coordinate
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx**2 + dy**2)

class SugarAgent(CellAgent):
    ## Initiate agent, inherit model property from parent class
    def __init__(self, model, cell, sugar=0, metabolism=0, vision = 0, tech = 0, affiliation = 0):
        super().__init__(model)
        ## Set variable traits based on model parameters
        self.cell = cell
        self.sugar = sugar
        self.metabolism = metabolism
        self.vision = vision
        self.tech = tech
        self.affiliation = affiliation
    ## Define movement action
    def move(self):
        ## Determine currently empty cells within line of sight
        possibles = [
            cell
            for cell in self.cell.get_neighborhood(self.vision, include_center=True)
            if cell.is_empty 
        ]
        ## Determine how much sugar is in each possible movement target
        sugar_values = [
            cell.sugar
            for cell in possibles
        ]
        ## Calculate the maximum possible sugar value in possible targets
        if sugar_values:
            max_sugar = max(sugar_values)
            ## Get indices of cell(s) with maximum sugar potential within range
            candidates_index = [
                i for i in range(len(sugar_values)) if math.isclose(sugar_values[i], max_sugar)
            ]
            ## Indentify cell(s) with maximum possible sugar
            candidates = [
                possibles[i]
                for i in candidates_index
            ]
            ## Find the closest cells with maximum possible sugar
            min_dist = min(get_distance(self.cell, cell) for cell in candidates)
            final_candidates = [
                cell
                for cell in candidates
                if math.isclose(get_distance(self.cell, cell), min_dist, rel_tol=1e-02)
            ]
        else:
            final_candidates = possibles
        ## Choose one of the closest cells with maximum sugar (randomly if more than one)
        self.cell = self.random.choice(final_candidates if final_candidates else [self.cell])
    ## consumer sugar in current cell, depleting it, then consumer metabolism
    def gather_and_eat(self):
        self.sugar += self.cell.sugar
        self.cell.sugar = 0
        self.sugar -= self.metabolism
    ## If an agent has zero or negative suger, it dies and is removed from the model
    def see_if_die(self):
        if self.sugar <= 0:
            self.remove()

    def update_tech_level(self):
        '''
        Update the agent's technology level to the one higher level,
        update the agent's metabolism to new reduced metabolism 
        '''
        self.tech += 1
        self.metabolism = self.metabolism * self.model.reduction_scale

    def innovate(self):
        '''
        Evalues whether the agent belongs to group 0, whether sugar level is sufficient
        for one more step, calculates probability of success of innovation, compares the 
        probability with a randomly generated number between 0 and 1, evaluates whether 
        technology level has not yet achieved the highest possible(5), if all above is true, 
        the agent's current tech level is updated to current level + 1 and the metabolism 
        s updated to a pre-specified percentage of the current metabolism level
        '''
        if self.sugar > self.metabolism and self.affiliation == 0:
            p_success = self.sugar * self.model.innovation_difficulty
            if p_success > self.random.random() and self.tech < self.model.tech_bottleneck:
                self.update_tech_level()

    def share(self):
        '''
        If agent belongs to innovating group, chooses one neighbor 
        to share technology advancement with who belongs to the 
        same affiliation and inside reachable neighborhood
        Each agent can only communicate with one other agent at each step
        '''
        if self.affiliation == 0:
            ## Determine neighbors
            neighbors_cells = [
                cell
                for cell in self.cell.get_neighborhood(self.vision, include_center=True)
                if not cell.is_empty
            ]
            ## Filter neighbors based on affiliation
            filtered_neighbors = [a for cell in neighbors_cells for a in self.model.agents 
                                if a.cell == cell and a.affiliation == 0]
            ## Randomly choose one neighbor
            neighbor = self.random.choice(filtered_neighbors)
            if neighbor.tech > self.tech:
                self.update_tech_level()
            elif neighbor.tech < self.tech:
                neighbor.update_tech_level()
    
        