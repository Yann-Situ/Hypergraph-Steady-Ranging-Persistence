import matplotlib.pyplot as plt
from src.hypergraph_filtration import HyperGraphFiltration
import src.edge_features as feat

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

# Take an edges.csv file and return a list of dictionary, each dictionary represent a hyperedge.
# Note that this function was designed to work with the hyperbard dataset.
# strings_to_erase is a list of strings that should be replaced by "" when reading the file
def build_edgedict_from_file(filename, strings_to_erase = []):
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

# Build a HyperGraphFiltration object from a list of dictionary (each representing a hyperedge).
# nodes_key is the dictionary key that must be associated with a set of nodes
# name_key is the dictionary key that must be associated with the name of the hyperedge
# weight_key is the dictionary key that must be associated with the weight of the hyperedge
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
    directory = "data/"
    filename = "king-lear_hg-scene-mw.edges.csv"
    # filename = "romeo-and-juliet_hg-scene-mw.edges.csv"
    edgedict = build_edgedict_from_file(directory+filename,["_Lr", "_Rom"])
    HGF = build_hypergraphfiltration_from_edgedict(edgedict,
        nodes_key = "onstage",
        name_key = None,
        weight_key = None)
    # HGF = build_hypergraph_edge_filtration(size_file, edge_file, time_file, 10)

    #print(HGF.time_range)
    #compute_originality_values(H)
    # HGF.compute_time_range_from_weights()
    HGF.time_range = [5.0, 8.0]

    #plt.subplots(figsize=(30,20))
    # hnx.draw(HGF.H.collapse_nodes(), with_node_counts=True, with_edge_labels = True)
    # hnx.draw(HGF.H.collapse_nodes_and_edges(), with_node_counts=True, with_edge_counts = True)
    # hnx.draw(HGF.H, with_node_labels=True, with_edge_labels = True)
    # HGF.plot_filtration(4, dual=True, with_node_labels = False, with_edge_labels = True)
    # HGF.plot_filtration(4, with_node_labels = False, with_edge_labels = True)

    HGF.plot_filtration(2, dual=False, with_node_labels = True, with_edge_labels = True)
    plt.tight_layout()
    HGF.time_range = [3.0, 5.0]
    HGF.plot_filtration(2, dual=True, with_node_labels = True, with_edge_labels = True)
    plt.tight_layout()

    # plt.subplots(figsize=(30,20))
    # hnx.draw(HGF.H.dual(), with_node_labels = True, with_edge_labels = True)

    # plt.subplots(figsize=(30,20))
    # hnx.draw(HGF.get_sub_hypergraph(7), with_node_labels=True, with_edge_labels = True)
    # plt.subplots(figsize=(30,20))
    # hnx.draw(HGF.get_sub_hypergraph(6), with_node_labels=True, with_edge_labels = True)
    # plt.subplots(figsize=(30,20))
    # hnx.draw(HGF.get_sub_hypergraph(7).dual(), with_node_labels=True, with_edge_labels = True)
    # plt.subplots(figsize=(30,20))
    # hnx.draw(HGF.get_sub_hypergraph(6).dual(), with_node_labels=True, with_edge_labels = True)


    # fig1, ax_steady = plt.subplots(2,2)
    # fig2, ax_ranging = plt.subplots(2,1)
    # dual = True
    #
    # HGF.compute_feature_steady_persistence(feat.strict_hyperhub_feature, display_progress=True, dual = dual)
    # HGF.compute_ranging_from_steady_persistence()
    # ax_steady[0,0] = HGF.steady_pd.plot_gudhi(ax_steady[0,0], labeling=True, title="Steady hyperedge hub")
    # ax_ranging[0] = HGF.ranging_pd.plot_gudhi(ax_ranging[0], labeling=True, title="Ranging hyperedge hub")
    #
    #
    # HGF.compute_feature_steady_persistence(feat.exclusivity_feature, display_progress=True, dual = dual)
    # ax_steady[1,0] = HGF.steady_pd.plot_gudhi(ax_steady[1,0], labeling=True, title="Exclusivity")
    #
    # HGF.compute_feature_steady_persistence(feat.mean_originality_feature, display_progress=True, dual = dual)
    # HGF.compute_ranging_from_steady_persistence()
    # ax_steady[0,1] = HGF.steady_pd.plot_gudhi(ax_steady[0,1], labeling=True, title="Steady mean originality")
    # ax_ranging[1] = HGF.ranging_pd.plot_gudhi(ax_ranging[1], labeling=True, title="Ranging mean originality")
    #
    # HGF.compute_feature_steady_persistence(feat.max_originality_feature, display_progress=True, dual = dual)
    # ax_steady[1,1] = HGF.steady_pd.plot_gudhi(ax_steady[1,1], labeling=True, title="Max originality")
    #
    # fig1.tight_layout()
    # fig2.tight_layout()
    plt.show()

################################################################################

if __name__ == "__main__":
    test_hypernet()
