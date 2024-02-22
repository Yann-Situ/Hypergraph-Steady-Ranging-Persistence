import matplotlib.pyplot as plt
from hypergraph_filtration import HyperGraphFiltration

from tqdm import tqdm
from sys import getsizeof
import os.path

try:
    import hypernetx as hnx
except ImportError:
    print("HyperNetX not found")
    #!pip install hypernetx --quiet 2> /dev/null
    #print("Installation complete; please rerun this cell in order for the rest of the cells to use HyperNetX.")
    exit()

import warnings
warnings.simplefilter('ignore')

def build_dict_from_file(filename, strings_to_erase = []):
    if not os.path.exists(filename):
        print("Error, file doesn't exists")
        return None
    file = open(filename, "r")

    # process first line
    keys = file.readline()[:-1].split(',')
    keys_n = len(keys)

    # process other lines
    r = []
    while (l := file.readline()):
        l = l[:-1]
        for s in strings_to_erase:
            l = l.replace(s, "")
        dict = {}
        objects = l.split(',')
        if keys_n == len(objects):
            for i, s in enumerate(objects):
                if s.isnumeric():
                    dict[keys[i]] = int(s)
                elif ' ' in s or '#' in s:
                    dict[keys[i]] = s.replace("#", "").split(' ')
                else:
                    dict[keys[i]] = s
            r.append(dict)
        else:
            print("Error, keys and objects doesn't have the same cardinal")
    file.close()
    return r

def build_hypergraphfiltration_from_edgedict(edgedict, nodes_key, name_key = None, weight_key = None, max_edges = 100000):
    hypergraphdict = {}
    edge_weights = {}
    node_weights = {}

    for edge_number, dict in enumerate(edgedict):

        nodes = set(dict[nodes_key])
        name = edge_number if name_key is None else dict[name_key]
        weight = edge_number if weight_key is None else dict[weight_key]
        hypergraphdict[name] = nodes
        edge_weights[name] = weight
        if edge_number >= max_edges:
            break
    return HyperGraphFiltration(hnx.Hypergraph(hypergraphdict, sort=False), node_weights, edge_weights, [0.0])

def test_hypernet():
    directory = "data/hyperbard/graphdata/"
    filename = "king-lear_hg-scene-mw.edges.csv"
    # filename = "othello_hg-scene-mw.edges.csv"
    # filename = "richard-iii_hg-scene-mw.edges.csv"
    # filename = "romeo-and-juliet_hg-scene-mw.edges.csv"
    # filename = "henry-iv-part-2_hg-scene-mw.edges.csv"
    # filename = "hamlet_hg-scene-mw.edges.csv"
    edgedict = build_dict_from_file(directory+filename,
        ["_Lr", "_Oth", "_R3", "_3H6", "_Rom", "_2H4", "_1H4", "_H5"])
    HGF = build_hypergraphfiltration_from_edgedict(edgedict,
        nodes_key = "onstage",
        name_key = None,
        weight_key = None)
    # HGF = build_hypergraph_edge_filtration(size_file, edge_file, time_file, 10)

    #print(HGF.time_range)
    #compute_originality_values(H)
    # H5 = HGF.get_sub_hypergraph(10)
    HGF.compute_time_range_from_weights()
    plt.subplots(figsize=(30,20))
    hnx.draw(HGF.H.collapse_nodes(), with_node_counts=True, with_edge_labels = True)
    # hnx.draw(HGF.H.collapse_nodes_and_edges(), with_node_counts=True, with_edge_counts = True)
    # hnx.draw(HGF.H, with_node_labels=True, with_edge_labels = True)
    # HGF.plot_filtration(4, dual=True, with_node_labels = False, with_edge_labels = True)
    # HGF.plot_filtration(4, with_node_labels = False, with_edge_labels = True)

    plt.subplots(figsize=(30,20))
    hnx.draw(HGF.H.dual(), with_node_labels = True, with_edge_labels = True)

    # HGF.compute_feature_steady_persistence(size_3_feature, display_progress=True)
    # fig, axs = plt.subplots(2,2)
    # HGF.compute_feature_steady_persistence(originality_feature, display_progress=True)
    # axs[0,0] = HGF.steady_pd.plot_gudhi(axs[0,0], labeling=True, title="Edge Originality")
    # # HGF.compute_feature_steady_persistence(local_max_size_feature, display_progress=True)
    # # axs[0,1] = HGF.steady_pd.plot_gudhi(axs[0,1], labeling=True, title="Local max")
    # HGF.compute_feature_steady_persistence(strict_hyperhub_feature, display_progress=True)
    # axs[1,0] = HGF.steady_pd.plot_gudhi(axs[1,0], labeling=True, title="Edge Hyperhub")
    #
    # HGF.compute_feature_steady_persistence(originality_feature, display_progress=True, dual=True)
    # axs[0,1] = HGF.steady_pd.plot_gudhi(axs[0,1], labeling=True, title="Node Originality")
    # # HGF.compute_feature_steady_persistence(local_max_size_feature, display_progress=True)
    # # axs[0,1] = HGF.steady_pd.plot_gudhi(axs[0,1], labeling=True, title="Local max")
    # HGF.compute_feature_steady_persistence(strict_hyperhub_feature, display_progress=True, dual=True)
    # axs[1,1] = HGF.steady_pd.plot_gudhi(axs[1,1], labeling=True, title="Node Hyperhubs")

    plt.show()

################################################################################

if __name__ == "__main__":
    test_hypernet()
