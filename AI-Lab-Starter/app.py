from shiny import App, ui, render, reactive
import polars as pl
from openai import OpenAI
import json

# Load Data
df = pl.read_csv("properties.csv")

# Configuration
# Choose provider: 'ollama', 'gemini', or 'azure'
PROVIDER = 'ollama' 

# --- Client Setup ---
if PROVIDER == 'ollama':
    client = OpenAI(
        base_url='http://localhost:11434/v1',
        api_key='ollama', # required but unused
    )
    MODEL = "llama3.2:3b"

elif PROVIDER == 'gemini':
    # Requires: GOOGLE_API_KEY environment variable or set directly
    # Usage: export GOOGLE_API_KEY="AIza..."
    client = OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=os.environ.get("GOOGLE_API_KEY", "INSERT_KEY_HERE"),
    )
    MODEL = "gemini-1.5-flash"

elif PROVIDER == 'azure':
    # Requires: AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT
    from openai import AzureOpenAI
    client = AzureOpenAI(
        api_key=os.environ.get("AZURE_OPENAI_API_KEY", "INSERT_KEY_HERE"),
        api_version="2023-12-01-preview",
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", "https://your-resource.openai.azure.com/")
    )
    MODEL = "gpt-4o" # or your deployment name



# TODO: Define your System Prompt here
# TODO: Our example code assumes a JSON response; you can do something different if you want.
SYSTEM_PROMPT = """
You are a data filtering assistant.
The user will ask for properties based on specific criteria.
XXX TODO: This is how our example code work but you can change: **DELETE ME** XXX
You must return a JSON object representing the filters.
Do not return any text other than the JSON.

XXX TODO: FINISH **DELETE ME** XXX
"""

app_ui = ui.page_fluid(
    ui.h2("AI Property Filter"),
    
    ui.layout_sidebar(
        ui.sidebar(
            # New in Shiny 1.0!
            ui.chat_ui("chat"),
            width=400
        ),
        ui.card(
            ui.card_header("Property Schedule"),
            ui.output_data_frame("grid"),
        )
    )
)

def server(input, output, session):
    
    # Reactive value to hold the filtered dataframe
    # We initialize it with the full dataset
    filtered_df = reactive.Value(df)
    
    # Initialize the Chat
    chat = ui.Chat(id="chat", messages=[
        {"role": "assistant", "content": "Describe the properties you want to see (e.g., 'High risk timber in London')."}
    ])
    
    # Handle User Input
    @chat.on_user_submit
    async def handle_query(user_input: str):
        # 1. Append user message to chat
        await chat.append_message(user_input)
        
        # TODO: Call LLM to get filters
        if False:
            # TODO
            try:
                response = client.chat.completions.create(
                    model=MODEL,
                    ### TODO
                )
                
                json_str = response.choices[0].message.content
                filters = json.loads(json_str)
                
                # 3. Apply Filters
                current_df = df
                filter_desc = []
                
                if not filters:
                    filter_desc.append("Showing all data.")
                else:
                    for col, val in filters.items():
                        if col in df.columns:
                            # TODO - try at least simple strings
                
                filtered_df.set(current_df)
        else:
            # For now, we just echo
            response = f"You said: {user_input}. (AI logic not implemented yet)"
        
        await chat.append_message(response)

    @render.data_frame
    def grid():
        return render.DataGrid(filtered_df())

app = App(app_ui, server)
