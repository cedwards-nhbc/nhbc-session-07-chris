from shiny import App, ui, render, reactive, run_app
import numpy as np

app_ui = ui.page_fluid(
    ui.h2("Reactivity 101"),
    ui.input_slider("n", "Count", 1, 100, 10),
    ui.input_action_button("btn", "Regenerate"),
    
    ui.h4("Sum"),
    ui.output_text_verbatim("sum_out"),
    
    # Task 3 & 4: Add UI for Mean and Max
    ui.h4("Mean"),
    ui.output_text_verbatim("mean_out"),
    ui.h4("Max"),
    ui.output_text_verbatim("max_out"),
)

def server(input, output, session):
    
    @reactive.calc
    def random_data():
        input.btn() 
        # Task 1: Return array
        return np.random.randint(0, 100, input.n())

    @render.text
    def sum_out():
        # Task 2: Calculate sum
        data = random_data()
        return f"Sum: {np.sum(data)}"

    @render.text
    def mean_out():
        # Task 3: Calculate mean
        data = random_data()
        return f"Mean: {np.mean(data):.2f}"

    @render.text
    def max_out():
        # Task 4: Calculate max
        data = random_data()
        return f"Max: {np.max(data)}"

app = App(app_ui, server)

if __name__ == "__main__":
    run_app(app, launch_browser=True)