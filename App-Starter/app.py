from shiny import App, render, ui, reactive
import polars as pl
import numpy as np
import plotly.express as px
from scipy.optimize import curve_fit
import json
from pathlib import Path
from shinywidgets import output_widget, render_widget

# --- 1. SETUP & DATA LOADING ---

# TODO: Load Data
# We need to load Policy_Book.parquet and Claims_Transaction.parquet
# and calculate the df_acph (Average Cost Per Home) just like in Session 6.
# For now, we will just put a placeholder.

def load_data():
    # Placeholder for student code
    # Should return df_acph
    return pl.DataFrame()

# df_acph = load_data() 

# --- 2. UI DEFINITION ---

app_ui = ui.page_fluid(
    ui.panel_title("The Outlier Excluder"),
    
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_select(
                "product", 
                "Select Product:",
                choices=["Detached", "Semi-detached", "Flat", "Social Housing"]
            ),
            
            ui.input_checkbox_group(
                "excluded_years",
                "Exclude Years from Fit:",
                choices=["2017", "2019", "2020", "2021"],
                selected=[]
            ),
            
            ui.input_action_button("save_btn", "Save Assumptions", class_="btn-success"),
            ui.output_text_verbatim("save_status")
        ),
        
        ui.card(
            ui.card_header("Curve Fit Analysis"),
            output_widget("main_plot")
        ),
        
        ui.card(
            ui.card_header("Fitted Parameters"),
            ui.output_table("params_table")
        )
    )
)

# --- 3. SERVER LOGIC ---

def server(input, output, session):
    
    # TODO: Reactive Data Filter
    # @reactive.Calc
    # def filtered_data():
    #     ... return df_acph filtered by input.product() ...
    
    # TODO: Reactive Curve Fit
    # @reactive.Calc
    # def fitted_curve():
    #     ... get filtered_data() ...
    #     ... remove input.excluded_years() ...
    #     ... run curve_fit ...
    #     ... return parameters ...
    
    @render_widget
    def main_plot():
        # Placeholder plot
        return px.scatter(title="Please implement data loading first!")
    
    @render.table
    def params_table():
        # Placeholder table
        return pl.DataFrame({"Parameter": ["A", "B", "C"], "Value": [0, 0, 0]})
    
    # TODO: Save Button Logic
    # @reactive.Effect
    # @reactive.event(input.save_btn)
    # def save():
    #     ... write to assumptions.json ...

app = App(app_ui, server)
