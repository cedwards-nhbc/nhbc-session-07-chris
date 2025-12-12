from shiny import App, render, ui
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

app_ui = ui.page_fluid(
    ui.h2("The Slow App 🐢"),
    ui.input_slider("n", "Sample Size", 100, 1000, 100),
    ui.output_text_verbatim("info"),
    ui.output_plot("plot")
)

def server(input, output, session):

    # This function simulates a slow database query
    def get_data(n):
        print("Querying Database... (Slow)")
        time.sleep(1.0) # Sleep for 1 second to simulate lag
        return pd.DataFrame({'x': range(n), 'y': np.random.randn(n)})

    @render.text
    def info():
        # EAGER EXECUTION PROBLEM:
        # This calls get_data() every time input.n() changes
        df = get_data(input.n())
        return f"Loaded {len(df)} rows from the database."

    @render.plot
    def plot():
        # EAGER EXECUTION PROBLEM:
        # This calls get_data() AGAIN, doubling the wait time!
        df = get_data(input.n())
        fig, ax = plt.subplots()
        ax.plot(df['x'], df['y'])
        return fig

app = App(app_ui, server)
