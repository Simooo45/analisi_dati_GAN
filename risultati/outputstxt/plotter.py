import os
import math
import pandas as pd
import matplotlib.pyplot as plt
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
    return df[0] * df.index.map(exp_fun)

def n_connections(input_size: int, layers: list[int], output_size: int = 1):
    n_conn = 0
    layers = [input_size] + layers + [output_size]
    for idx in range(len(layers) - 1):
        n_conn += layers[idx] * layers[idx + 1]
    return n_conn

def pond_avg(df: pd.DataFrame):
    return sum((df[0] * df.index.map(exp_fun)))/sum([1 - math.e**(-n/200) for n in range(df[0].size)])

def multiple_contains(string: str, substring_list: list):
    return any(sub in string for sub in substring_list)


def plot():
    # Definisci la cartella contenente i file
    folder_path = 'D:\D\gitRepos\\analisi_dati_GAN\\risultati\outputstxt\outputstxt\outputs'  

    # Lista per memorizzare i percorsi dei file
    file_paths = []

    contents = os.listdir(folder_path)
    dirs = []
    for content in contents:
        dir = os.path.join(folder_path, content)
        if os.path.isdir(dir):
            file_paths.append(os.path.join(dir, 
                                        'caloChallenge',
                                        'Baseline_pions_lwtnn',
                                        'All',
                                        'checkpoints',
                                        'pions',
                                        'checkpoints_eta_20_25',
                                        'time_per_epoch.txt' if TIME else 'chi2.txt'))
            dirs.append(content)

    # Carica i file di testo e uniscili in un unico DataFrame
    dfs = [pd.read_csv(file, delimiter='\t', header=None).head(1000) for file in file_paths]  # Se i dati sono separati da tabulazioni, altrimenti modifica il separatore di conseguenza
    filtered_dfs = [df for df in dfs if len(df[0]) >= N_MIN]
    sorted_dfs = sorted([df for df in filtered_dfs if df.min()[0] > 0], 
                        key=lambda x: ((x.iloc[:, 0].values < 10).sum()), 
                        reverse=True)[:]

    # Plotta i dati
    plt.figure(figsize=(10, 6))  # Imposta le dimensioni della figura

    
    infos = []
    # Plotta i dati da ogni file
    for file_path, df in zip(dirs, dfs):
        if any(df.equals(sorted_df) for sorted_df in sorted_dfs):
            min_value = df.min()[0]
            min_index = df.idxmin()[0]*(10**3)
            if min_value >= 0 and not TIME:
                layers_list = file_path[6:].split('_')
                layers = []
                for l in layers_list:
                    try: 
                        layers.append(int(l))
                    except:
                        pass
                dict_info = {}
                dict_info["file"] = file_path
                print(f"FILE:       {dict_info['file']}")

                dict_info["n_conn"] = n_connections(533, layers)
                print(f"CONN:       {dict_info['n_conn']}")

                dict_info["avg_chi"] = pond_avg(df)
                print(f"CHI_AVG:    {dict_info['avg_chi']}")

                infos.append(dict_info)

            if any(df.equals(sorted_df) for sorted_df in sorted_dfs) \
                    and multiple_contains(file_path, [''] )\
                    and min_value >= 0:
                

                filtered_df = df[df.index >= 2]
                line, = plt.plot(filtered_df.index*(10**3), normalize(filtered_df), label=os.path.basename(file_path)) 
                if (not TIME):
                    plt.annotate('{}  \n{:.2f}'.format(file_path[6:].replace('_', '|'), min_value), xy=(min_index, min_value),
                        xytext=(min_index + 10, min_value + 0.1),
                        arrowprops=dict(facecolor=line.get_color(), shrink=0.05, color=line.get_color()),
                        rotation='vertical', verticalalignment='top')

    plt.xlabel('Epoca') 
    plt.ylabel('Secondi' if TIME else 'Chi2/dof')
    plt.title('Tempo impiegato' if TIME else 'Chi quadro' + 
            ' in funzione della topologia del discriminatore')  
    plt.legend()  # Aggiunge la legenda
    plt.grid(True)  # Aggiunge la griglia al grafico
    plt.show()  # Mostra il graficorisultati

    if not TIME:
        # Estrai i valori di n_conn, avg_chi e file_name dalla lista infos
        n_conn_values = [info["n_conn"] for info in infos]
        avg_chi_values = [info["avg_chi"] for info in infos]
        file_names = [' > ' + '|'.join(info["file"][6:].split('_')) for info in infos]
        distances = np.sqrt((np.array(n_conn_values)/max(n_conn_values))**2 + (np.array(avg_chi_values)/max(avg_chi_values))**2)

        # Normalizza le distanze per avere valori compresi tra 0 e 1
        normalized_distances = (distances - min(distances)) / (max(distances) - min(distances))

        # Mappa le distanze normalizzate a una scala di colori tra verde e rosso
        colors = plt.cm.RdYlGn(1 - normalized_distances)

        # Creazione del plot
        plt.figure(figsize=(8, 6))

        # Plot dei punti
        plt.scatter(n_conn_values, avg_chi_values, marker='o', color=colors)

        # Aggiungi il nome del file a ciascun pallino
        for i, file_name in enumerate(file_names):
            plt.text(n_conn_values[i], avg_chi_values[i], file_name, fontsize=8, ha='left', va='center')

        # Aggiungi etichette agli assi
        plt.xlabel('Numero di connessioni')
        plt.ylabel(r'$\frac{\sum_{i}^{N_{EPOCH}} \chi^2_{i}\cdot(1 - e^{\frac{i}{200}})}{\sum_{i}^{N_{EPOCH}} (1 - e^{\frac{i}{200}})}$')

        # Aggiungi una linea tratteggiata per l'origine del plot
        plt.axhline(0, color='black', linestyle='--', linewidth=0.5)
        plt.axvline(0, color='black', linestyle='--', linewidth=0.5)

        # Aggiungi un titolo al plot
        plt.title('Scatter plot: Numero di connessioni vs Media pesata')

        # Mostra il plot
        plt.grid(True)
        plt.show()
if __name__ == "__main__":

    plot()