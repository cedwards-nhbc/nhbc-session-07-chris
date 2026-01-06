from shiny import App, render, ui, reactive
import polars as pl
import numpy as np
import plotly.express as px
from scipy.optimize import curve_fit
import json
from pathlib import Path
from shinywidgets import output_widget, render_widget

# --- 1. SETUP & DATA LOADING ---

def load_data():
    # Adjust path to point to the root of the repo
    # Assuming we run this from the repo root or Session-7 folder
    # We'll look for the files in the parent directory or current
    
    # Try to find the data files
    possible_paths = [Path("."), Path(".."), Path("../..")]
    data_dir = None
    for p in possible_paths:
        if (p / "Policy_Book.parquet").exists():
            data_dir = p
            break
            
    if data_dir is None:
        # Fallback for demo purposes if files missing
        return pl.DataFrame()

    df_policies = pl.read_parquet(data_dir / "Policy_Book.parquet")
    df_claims = pl.read_parquet(data_dir / "Claims_Transaction.parquet")

    # 1. Exposure
    df_exposure = (
        df_policies
        .group_by("CohortYear")
        .agg(pl.col("NumHomes").sum().alias("TotalHomes"))
    )

    # 2. Claims Dev
    df_dev = (
        df_claims
        .join(df_policies.select(["PolicyID", "CohortYear", "ProductType"]), on="PolicyID")
        .with_columns(
            (pl.col("ReportDate").dt.year() - pl.col("CohortYear")).alias("DevYear")
        )
        .group_by(["CohortYear", "DevYear", "ProductType"])
        .agg(pl.col("PaymentAmount").sum().alias("TotalClaims"))
    )

    # 3. ACPH
    df_acph = (
        df_dev
        .join(df_exposure, on="CohortYear")
        .with_columns(
            (pl.col("TotalClaims") / pl.col("TotalHomes")).alias("ACPH")
        )
        .sort(["ProductType", "CohortYear", "DevYear"])
    )
    
    return df_acph

# Load once at startup
df_acph = load_data() 

# Curve Definition
def actuarial_curve(t, A, B, C):
    t_safe = np.maximum(t, 0.1) 
    return A * (t_safe ** B) * np.exp(-C * t_safe)

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
            
            ui.card(
                ui.card_header("Select Points to Exclude"),
                ui.output_data_frame("exclusion_grid"),
                height="400px"
            ),
            
            ui.input_action_button("save_btn", "Save Assumptions", class_="btn-success"),
            # ui.output_text_verbatim("save_status")
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
    
    @reactive.Calc
    def filtered_data():
        selected_product = input.product()
        if df_acph.is_empty(): return pl.DataFrame()
        
        return df_acph.filter(pl.col("ProductType") == selected_product)
    
    @render.data_frame
    def exclusion_grid():
        df = filtered_data()
        if df.is_empty(): return render.DataGrid(pl.DataFrame())
        
        # Show relevant columns for selection
        display_df = df.select(["CohortYear", "DevYear", "ACPH"]).to_pandas()
        
        return render.DataGrid(
            display_df,
            selection_mode="rows",
            summary=False,
            filters=True
        )
    
    @reactive.Calc
    def fitted_curve():
        df = filtered_data()
        if df.is_empty(): return None
        
        # Get selected rows to exclude
        # input.exclusion_grid.selected_rows() returns a tuple of row indices
        selected_indices = input.exclusion_grid_selected_rows()
        
        # Create a boolean mask for inclusion
        # Default is include all
        include_mask = np.ones(len(df), dtype=bool)
        
        if selected_indices:
            include_mask[list(selected_indices)] = False
            
        df_clean = df.filter(pl.Series(include_mask))
        
        # Aggregate to get the pattern to fit
        df_pattern = (
            df_clean
            .group_by("DevYear")
            .agg(pl.col("ACPH").mean().alias("AvgACPH"))
            .sort("DevYear")
            .filter(pl.col("DevYear") <= 10)
        )
        
        if df_pattern.height < 3: return None # Not enough points
        
        x_data = df_pattern["DevYear"].to_numpy()
        y_data = df_pattern["AvgACPH"].to_numpy()
        
        try:
            popt, _ = curve_fit(actuarial_curve, x_data, y_data, p0=[100, 2, 0.5], maxfev=5000)
            return popt
        except:
            return None
    
    @render_widget
    def main_plot():
        df = filtered_data()
        if df.is_empty(): return px.scatter(title="No Data Found")
        
        # Identify excluded points for visualization
        selected_indices = input.exclusion_grid_selected_rows() or []
        df_pd = df.to_pandas()
        df_pd["Status"] = "Included"
        if selected_indices:
            df_pd.iloc[list(selected_indices), df_pd.columns.get_loc("Status")] = "Excluded"
        
        # Plot Actuals
        fig = px.scatter(
            df_pd, 
            x="DevYear", 
            y="ACPH", 
            color="CohortYear", 
            symbol="Status", # Different symbol for excluded
            symbol_map={"Included": "circle", "Excluded": "x"},
            title=f"ACPH Analysis: {input.product()}",
            opacity=0.7
        )
        
        # Plot Fitted Curve
        popt = fitted_curve()
        if popt is not None:
            x_range = np.linspace(0, 10, 100)
            y_fit = actuarial_curve(x_range, *popt)
            
            fig.add_scatter(
                x=x_range, 
                y=y_fit, 
                mode='lines', 
                name='Fitted Curve', 
                line=dict(color='black', width=4)
            )
            
        return fig
    
    @render.table
    def params_table():
        popt = fitted_curve()
        if popt is None: return pl.DataFrame({"Status": ["Fit Failed"]})
        
        return pl.DataFrame({
            "Parameter": ["A (Scale)", "B (Shape)", "C (Decay)"],
            "Value": popt
        })
    
    @reactive.Effect
    @reactive.event(input.save_btn)
    def save():
        # Load existing or create new
        path = Path("assumptions.json")
        if path.exists():
            with open(path, 'r') as f:
                data = json.load(f)
        else:
            data = {"products": {}}
            
        # Update
        prod = input.product()
        if "products" not in data: data["products"] = {}
        if prod not in data["products"]: data["products"][prod] = {}
        
        # Get excluded points
        df = filtered_data()
        selected_indices = input.exclusion_grid_selected_rows()
        
        excluded_points = []
        if selected_indices:
            excluded_rows = df.filter(pl.Series(np.isin(np.arange(len(df)), list(selected_indices))))
            for row in excluded_rows.iter_rows(named=True):
                excluded_points.append({
                    "CohortYear": row["CohortYear"],
                    "DevYear": row["DevYear"]
                })
        
        data["products"][prod]["excluded_points"] = excluded_points
        
        # Save
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
            
        ui.notification_show(f"Saved {len(excluded_points)} exclusions for {prod}!", type="success")

app = App(app_ui, server)