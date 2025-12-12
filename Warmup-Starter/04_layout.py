from shiny import App, ui, render, run_app
from shinywidgets import output_widget, render_widget
import plotly.express as px
import numpy as np

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("Controls"),
        ui.input_slider("n", "Sample Size", 10, 1000, 500),
        ui.input_select("color", "Color", choices=["blue", "red", "green"]),
    ),
    ui.card(
        ui.card_header("Distribution Plot"),
        # Docs: https://shiny.rstudio.com/py/api/shinywidgets.output_widget.html
        output_widget("dist_plot"),
    ),
    ui.card(
        ui.card_header("Summary Statistics"),
        ui.output_text_verbatim("stats"),
    )
)

def server(input, output, session):
    
    @render_widget
    def dist_plot():
        rng = np.random.default_rng(123)
        # Generate random numbers from a standard normal distribution (mean=0, stdev=1)
        # Docs: https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.standard_normal.html
        data = rng.standard_normal(input.n())
        fig = px.histogram(x=data, nbins=30, title=f"Histogram of {input.n()} points")
        fig.update_traces(marker_color=input.color())
        return fig

    @render.text
    def stats():
        return f"Selected N: {input.n()}"

app = App(app_ui, server)

# Add this block to run directly
if __name__ == "__main__":
    run_app(app, launch_browser=True)