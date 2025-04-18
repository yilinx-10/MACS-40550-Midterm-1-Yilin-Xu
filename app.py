from model import SugarScapeModel
from mesa.visualization import Slider, SolaraViz, make_plot_component
from mesa.visualization.components.matplotlib_components import make_mpl_space_component

## Define agent portrayal (color, size, shape), distinguish affiliation by color, 
# innovating agents are represented in yellow
def agent_portrayal(agent):
    if agent.affiliation == 0:
        return {"marker": "o", 
                "color": "yellow", 
                "size": 20}
    else:
        return {"marker": "o", 
                "color": "purple", 
                "size": 20}
## Define map portrayal, with greyer squares having more sugar than white squares
propertylayer_portrayal = {
    "sugar": {"color": "grey", 
              "alpha": 0.8, 
              "colorbar": True, 
              "vmin": 0, 
              "vmax": 10},
}

## Define model space component based on above
sugarscape_space = make_mpl_space_component(
    agent_portrayal=agent_portrayal,
    propertylayer_portrayal=propertylayer_portrayal,
    post_process=None,
    draw_grid=False,
)

## Define variable model parameters
model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    ## set initial reduction scaler to 0.9
    "reduction_scale": {
        "type": "InputText",
        "value": 0.9,
        "label": "Reduction Scale",
    },    
    ## set initial innovation difficulty to 0.00001
    "innovation_difficulty": {
        "type": "InputText",
        "value": 0.00001,
        "label": "Innovation Difficulty",
    },    
    "width": 50,
    "height": 50,
    "initial_population": Slider(
        "Initial Population", value=500, min=50, max=500, step=10
    ), # initial population set to 500
    # Agent endowment parameters, set initial endowment to 30
    "endowment_min": Slider("Min Initial Endowment", value=30, min=5, max=30, step=1),
    "endowment_max": Slider("Max Initial Endowment", value=30, min=30, max=100, step=1),
    # Metabolism parameters, set initial metabolism to 3
    "metabolism_min": Slider("Min Metabolism", value=3, min=1, max=3, step=1),
    "metabolism_max": Slider("Max Metabolism", value=3, min=3, max=8, step=1),
    # Vision parameters, set initial vision to 3
    "vision_min": Slider("Min Vision", value=3, min=1, max=3, step=1),
    "vision_max": Slider("Max Vision", value=3, min=3, max=8, step=1),
}

##Instantiate model
model = SugarScapeModel()

##Generate three plots for three of our data collectors
Plot_gini = make_plot_component("Gini")
Plot_tech = make_plot_component("Tech")
Plot_ratio = make_plot_component("Ratio")

## Define all aspects of page, all plots of three data collectors are displayed in the interfact
page = SolaraViz(
    model,
    components=[
        sugarscape_space,
        Plot_gini,
        Plot_tech,
        Plot_ratio,
    ],
    model_params=model_params,
    name="Sugarscape",
    play_interval=150,
)
## Return page
page