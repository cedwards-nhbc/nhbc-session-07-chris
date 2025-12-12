from shiny import App, ui, render, run_app

app_ui = ui.page_fluid(
    ui.h2("Widget Showcase"),
    ui.row(
        ui.column(4, 
            ui.input_select("busclass", "Business Class", 
                          choices=["Property", "Motor", "Casualty"]),
            ui.input_date("val_date", "Valuation Date"),
            ui.input_numeric("threshold", "Large Loss Threshold", 100000),
            ui.input_switch("gross", "Show Gross?", True),
            ui.input_radio_buttons("dist", "Distribution", 
                        choices=["Normal", "Uniform", "Exponential"]),
        ),
        ui.column(8,
            ui.output_text_verbatim("summary")
        )
    )
)

def server(input, output, session):
    @render.text
    def summary():
        return  (
            f"Selected Class: {input.busclass()}\n"
            f"Date: {input.val_date()}\n"
            f"Threshold: {input.threshold()}\n"
            f"Gross: {input.gross()}\n"
            f"Distribution: {input.dist()}\n"
        )

app = App(app_ui, server)

# Add this block to run directly
if __name__ == "__main__":
    run_app(app, launch_browser=True)