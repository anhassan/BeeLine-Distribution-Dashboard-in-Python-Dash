import pandas as pd
import dash
import dash_renderer
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# ---------- Import and clean data (importing csv into pandas)----------------------------------------------------------
file_location = "BeeLineDistribution.csv"
df = pd.read_csv("{}".format(file_location))
df = df.groupby(['State', 'ANSI', 'Affected by', 'Year', 'state_code'])[['Pct of Colonies Impacted']].mean()
df.reset_index(inplace=True)

# ----------------------------------------------------------------------------------------------------------------------
# App layout
app.layout = html.Div([
    dbc.Jumbotron(
        [
            html.H1("BeeLine Distribution", className="display-4"),
            html.P(
                "A dashboard providing the distribution and insights of bees effected "
                "across United States",
                className="lead",
            ),
            html.Hr(className="my-2"),
            html.P(
                "Wild life is essential for a healthy society. "
                "Lets start preserving nature with a step towards helping beeline revival"
            )
        ]
    ),
    dcc.Slider(
        id='year-slider',
        min=df['Year'].min(),
        max=df['Year'].max(),
        value=df['Year'].min(),
        marks={str(year): str(year) for year in df['Year'].unique()},
        step=None
    ),
    dbc.Row([
        dbc.Col(dcc.Graph(id='graph-with-slider'), width=6),
        dbc.Col(dcc.Graph(id='yearly-bar-distribution'), width=6)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='state-pie-with-slider'), width=5),
        dbc.Col(dcc.Graph(id='cause-pie-with-slider'), width=5)
    ])
])

# ----------------------------------------------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output('graph-with-slider', 'figure'),
     Output('yearly-bar-distribution', 'figure'),
     Output('state-pie-with-slider', 'figure'),
     Output('cause-pie-with-slider', 'figure')],
    [Input('year-slider', 'value')]
)
def render_figures(year_selected):
    title_states = 'States With Most Effected Bee Population'
    title_causes = 'Causes of Decline in Bee Line Distribution'
    selected_year_df = get_year_wise(year_selected, df)
    summarized_df = summarize_year_wise(df)
    states_df = get_most_impacted_states(year_selected, df, 5)
    causes_df = get_most_impactful_causes(year_selected, df, 5)
    return update_choropleth_map(selected_year_df), update_bar_chart(summarized_df), \
           update_pie_chart(states_df, 'State', title_states) \
        , update_pie_chart(causes_df, 'Affected by', title_causes)

# ----------------------------------------------------------------------------------------------------------------------
# Utility Functions for Filter Transformations
def get_most_impacted_states(year_selected, df, num_states):
    df_state_sorted = df.copy()
    df_state_sorted = df[df['Year'] == year_selected].groupby(by='State').mean().reset_index().sort_values(
        by='Pct of Colonies Impacted', ascending=False).round(2)
    return df_state_sorted.head(num_states)

def get_most_impactful_causes(year_selected, df, num_causes):
    df_cause_sorted = df.copy()
    df_cause_sorted = df[df['Year'] == year_selected].groupby(by='Affected by').mean().reset_index().sort_values(
        by='Pct of Colonies Impacted', ascending=False).round(2)
    return df_cause_sorted.head(num_causes)

def get_year_wise(year_selected, df):
    return df[df['Year'] == year_selected].round(2)

def summarize_year_wise(df):
    df_yearly = df.copy()
    return df.groupby(by='Year').mean().reset_index().sort_values(by='Year').round(2)

# Utility Functions for Building Visualizations
def update_choropleth_map(df):
    fig = px.choropleth(data_frame=df,
                        title="Percentage of Bees Effected Across USA",
                        locations='state_code',
                        locationmode="USA-states",
                        color='Pct of Colonies Impacted',
                        color_continuous_scale=px.colors.sequential.Mint,
                        scope="usa",
                        hover_data=['State', 'Pct of Colonies Impacted'],
                        labels={'Pct of Colonies Impacted': 'Bee Colonies Percentage'},
                        width=700,
                        height=600
                        )
    return fig

def update_bar_chart(df):
    fig = px.bar(data_frame=df,
                 title='Yearly Percentage Decrease in Bee Line Colonies Across USA',
                 x='Year',
                 y='Pct of Colonies Impacted',
                 text='Pct of Colonies Impacted',
                 height=550,
                 width=550,
                 color='Pct of Colonies Impacted',
                 color_continuous_scale=px.colors.sequential.Darkmint)
    fig.update_traces(texttemplate='%{text:.3s}', textposition='outside')
    return fig

def update_pie_chart(df, feature, title):
    fig = px.pie(data_frame=df,
                 title=title,
                 values='Pct of Colonies Impacted',
                 names=feature, color='Pct of Colonies Impacted',
                 color_discrete_sequence=px.colors.sequential.Mint
                 )
    return fig

if __name__ == "__main__":
    app.run_server(port=4500)

