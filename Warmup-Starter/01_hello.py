from shiny import App, ui, render, run_app

# 1. The UI (User Interface)
app_ui = ui.page_fluid(
    ui.h2("Hello, Actuaries!"),
    ui.input_text("name", "Enter your name", placeholder="Enter name"),
    ui.input_slider("n", "Number of Claims", 0, 100, 20),
    ui.output_text_verbatim("txt"),
)

# 2. The Server (Logic)
def server(input, output, session):
    @render.text
    def txt():
        return f"Hello, {input.name()}! You selected {input.n()} claims."

# 3. The App Object
app = App(app_ui, server)

# Add this block to run directly
if __name__ == "__main__":
    run_app(app, launch_browser=True)