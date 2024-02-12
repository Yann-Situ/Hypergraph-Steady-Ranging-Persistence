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
    #filename = "romeo-and-juliet_hg-scene-mw.edges.csv"
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

def size_3_feature(H):
    r = [edge for edge in H.edges
        if H.size(edge)==3 or H.size(edge)==2]
    return r #set(r)

def compute_originality_values(H):
    max_intersections = {edge : 0 for edge in H.edges}
    processed_edge = set()
    for edge in H.edges:
        edge_nodes = set(H.incidence_dict[edge])
        processed_edge.add(edge)
        for neighbor in set(H.edge_neighbors(edge)).difference(processed_edge):
            d = len(edge_nodes.intersection(H.incidence_dict[neighbor]))
            max_intersections[edge] = max(d, max_intersections[edge])
            max_intersections[neighbor] = max(d, max_intersections[neighbor])
    #print(max_intersections)
    for e, n in max_intersections.items():
        max_intersections[e] = 1.0 - n/(1.0*H.size(e))
    return max_intersections

def originality_feature(H, t = 0.5):
    originalities = compute_originality_values(H)
    return {e for e, o in originalities.items() if o > t}

def local_max_size_feature(H):
    not_max_edges = set()
    r = set()
    for e1 in H.edges:
        if not e1 in not_max_edges:
            is_e1_max = True
            se1 = H.size(e1)
            i = 0
            for e2 in H.edge_neighbors(e1):
                i = i+1
                se2 = H.size(e2)
                if se1 > se2:
                    not_max_edges.add(e2)
                elif se1 < se2:
                    is_e1_max = False
                    not_max_edges.add(e1)
                    break
            if i > 0 and is_e1_max:
                r.add(e1)
    return r

def strict_hyperhub_feature(H):
    neighb = {}
    lens = {}
    for e in H.edges:
        n_e = H.edge_neighbors(e)
        neighb[e] = n_e
        lens[e] = len(n_e)

    not_max_edges = set()
    r = set()
    for e1 in H.edges:
        if not e1 in not_max_edges and lens[e1] > 0:
            is_e1_max = True
            n_e1 = neighb[e1]
            l1 = lens[e1]
            for e2 in n_e1:
                l2 = lens[e2]
                if l1 > l2:
                    not_max_edges.add(e2)
                else: # l1 <= l2:
                    is_e1_max = False
                    not_max_edges.add(e1)
                    if l1 == l2:
                        not_max_edges.add(e2)
                    break

            if is_e1_max:
                r.add(e1)
    return r
################################################################################

if __name__ == "__main__":
    test_hypernet()
