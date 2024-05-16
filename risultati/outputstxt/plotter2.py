import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import os
import math
import numpy as np

TIME = False
NORM = False
N_MIN = 50

def exp_fun(idx):
    return (1 - math.e**(-idx/200))

# I dati hanno un peso in funzione della loro posizione 
def normalize(df: pd.DataFrame):
    if not NORM:
        return df
    return df.iloc[:, 0] * df.index.map(exp_fun)

def n_connections(input_size: int, layers: list[int], output_size: int = 1):
    n_conn = 0
    layers = [input_size] + layers + [output_size]
    for idx in range(len(layers) - 1):
        n_conn += layers[idx] * layers[idx + 1]
    return n_conn

def pond_avg(df: pd.DataFrame):
    return sum((df.iloc[:, 0] * df.index.map(exp_fun)))/sum([1 - math.e**(-n/200) for n in range(df.iloc[:, 0].size)])

def multiple_contains(string: str, substring_list: list):
    return any(sub in string for sub in substring_list)

# Funzione per leggere i file di testo
def read_txt_file(file_path):
    return pd.read_csv(file_path, header=None, names=['value'])

# Leggi i file di testo
folder_path = 'D:\\D\\gitRepos\\analisi_dati_GAN\\risultati\\outputstxt\\outputstxt\\outputs'

# Lista per memorizzare i percorsi dei file
file_names = []
dirs = []

contents = os.listdir(folder_path)
for content in contents:
    dir_path = os.path.join(folder_path, content)
    if os.path.isdir(dir_path):
        file_path = os.path.join(dir_path, 'caloChallenge', 'Baseline_pions_lwtnn', 'All', 'checkpoints', 'pions', 'checkpoints_eta_20_25', 'chi2.txt')
        if os.path.isfile(file_path):
            file_names.append(file_path)
            dirs.append(content)

# Crea un dizionario di DataFrame dai file letti
dataframes = {dir_name: read_txt_file(file_path) for dir_name, file_path in zip(dirs, file_names)}

# Processa i dati per lo scatter plot
infos = []
for dir_name, df in dataframes.items():
    if len(df) >= N_MIN:
        min_value = df.iloc[:, 0].min()
        if min_value > 0 and not TIME:
            layers_list = dir_name.split('_')
            layers = [int(l) for l in layers_list if l.isdigit()]
            dict_info = {
                "file": dir_name,
                "layers": layers,
                "n_conn": n_connections(533, layers),
                "avg_chi": pond_avg(df)
            }
            infos.append(dict_info)

# Crea l'app Dash
app = Dash(__name__)

# Layout dell'app
app.layout = html.Div([
    html.Label('Seleziona i dati da visualizzare:'),
    html.Div(
        dcc.Checklist(
            id='data-checkboxes',
            options=[
                {
                    'label': dir_name, 
                    'value': dir_name,
                    'disabled': df.iloc[:, 0].min() <= 0
                } for dir_name, df in dataframes.items()
            ],
            value=[],  # Nessun valore di default selezionato
            labelStyle={'display': 'inline-block', 'margin-right': '10px', 'width': '24%'}
        )
    ),
    dcc.Graph(
        id='line-chart',
        style={'height': '800px'}  
    ),
    dcc.Graph(
        id='scatter-plot',
        style={'height': '800px'}  
    ),
    dcc.Graph(
        id='scatter-plot3D',
        style={'height': '800px'} 
    )
])

# Callback per aggiornare il grafico a linee in base alle selezioni
@app.callback(
    Output('line-chart', 'figure'),
    [Input('data-checkboxes', 'value')]
)
def update_line_chart(selected_datasets):
    fig = go.Figure()
    for dir_name in selected_datasets:
        df = dataframes[dir_name]
        if df.iloc[:, 0].min() > 0:
            fig.add_trace(go.Scatter(y=df['value'], mode='markers', name=f'{dir_name}'))
    
    fig.update_layout(title='Grafico Interattivo',
                      xaxis_title='Indice',
                      yaxis_title='Valore')
    
    return fig

# Callback per aggiornare lo scatter plot
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('data-checkboxes', 'value')]
)
def update_scatter_plot(selected_datasets):
    filtered_infos = [info for info in infos] #if info['file'] in selected_datasets]
    if not filtered_infos:
        return go.Figure()

    n_conn_values = [info["n_conn"] for info in filtered_infos]
    avg_chi_values = [info["avg_chi"] for info in filtered_infos]
    file_names = [info["file"] for info in filtered_infos]
    
    scatter_fig = go.Figure(data=go.Scatter(
        x=n_conn_values,
        y=avg_chi_values,
        mode='markers+text',
        text=[f'{file_name}' for file_name in file_names],
        textposition='middle right',
        
    ))
    
    scatter_fig.update_layout(
        title='Scatter plot: Numero di connessioni vs Media pesata',
        xaxis_title='Numero di connessioni',
        yaxis_title=r'media ponderata chi2',
        showlegend=False
    )
    
    return scatter_fig

# Callback per aggiornare lo scatter plot
@app.callback(
    Output('scatter-plot3D', 'figure'),
    [Input('data-checkboxes', 'value')]
)
def update_scatter_plot_3d(selected_datasets):
    filtered_infos = [info for info in infos if len(info["layers"]) == 3]
    if not filtered_infos:
        return go.Figure()

    Xs = [info["layers"][0] for info in filtered_infos]
    Ys = [info["layers"][1] for info in filtered_infos]
    Zs = [info["layers"][2] for info in filtered_infos]
    avg_chi_values = [info["avg_chi"] for info in filtered_infos]
    file_names = [info["file"] for info in filtered_infos]
    n_conn_values = [info["n_conn"] for info in filtered_infos]

    # Normalizza le dimensioni per renderle visibili e comparabili
    size_min = 5
    size_max = 20
    normalized_sizes = [size_min + (size_max - size_min) * (n_conn - min(n_conn_values)) / (max(n_conn_values) - min(n_conn_values)) for n_conn in n_conn_values]

    scatter_fig = go.Figure(data=go.Scatter3d(
        x=Xs,
        y=Ys,
        z=Zs,
        mode='markers',
        marker=dict(
            color=avg_chi_values,
            colorscale='RdYlGn_r',  # Utilizza la gradazione inversa di RdYlGn
            colorbar=dict(title='Avg Chi2'),
            size=normalized_sizes,
            symbol='circle'
        ),
        text=['{}\n{:.3f}'.format(info["file"], info["avg_chi"]) for info in filtered_infos],
    ))

    scatter_fig.update_layout(
        title='Scatter plot 3D: Struttura dei layers',
        scene=dict(
            xaxis_title='N neuroni Layer 1',
            yaxis_title='N neuroni Layer 2',
            zaxis_title='N neuroni Layer 3'
        ),
        showlegend=False
    )

    return scatter_fig


# Esegui l'app
if __name__ == '__main__':
    app.run_server(debug=True)
