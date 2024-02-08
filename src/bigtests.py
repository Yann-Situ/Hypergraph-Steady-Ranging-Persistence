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

def build_hypergraph_edge_filtration(size_file, edge_file, time_file, max_edges = 1000000):
    dict = {}
    edge_weights = {}
    node_weights = {}

    file_size = os.path.getsize(size_file.name)
    pbar = tqdm(total=file_size*0.501, unit="MB")

    for edge_number, size in enumerate(size_file):
        nodes = set()
        edge_weights[edge_number] = int(time_file.readline())
        for i in range(int(size)):
            nodes.add(edge_file.readline())
        dict[edge_number] = nodes

        pbar.update(getsizeof(size)-getsizeof('\n'))
        if edge_number >= max_edges:
            break
    pbar.close()
    return HyperGraphFiltration(hnx.Hypergraph(dict, sort=False), node_weights, edge_weights, [0.0])

def build_hypergraph_node_filtration(size_file, edge_file, time_file, max_edges = 1000000):
    dict = {}
    edge_weights = {}
    node_weights = {}

    file_size = os.path.getsize(size_file.name)
    pbar = tqdm(total=file_size*0.501, unit="MB")

    for edge_number, size in enumerate(size_file):
        nodes = set()
        edge_time = int(time_file.readline())
        for i in range(int(size)):
            node = edge_file.readline()
            nodes.add(node)
            if node in node_weights:
                node_weights[node] = min(node_weights[node], edge_time)
            else:
                node_weights[node] = edge_time
        dict[edge_number] = nodes

        pbar.update(getsizeof(size)-getsizeof('\n'))
        if edge_number >= max_edges:
            break
    pbar.close()
    return HyperGraphFiltration(hnx.Hypergraph(dict, sort=False), node_weights, edge_weights, [0.0])

def test_hypernet():
    # model = "data/example/example"
    model = "data/threads-math-sx/threads-math-sx"
    assert(os.path.exists(model+"-nverts.txt"))
    assert(os.path.exists(model+"-simplices.txt"))
    assert(os.path.exists(model+"-times.txt"))
    size_file = open(model+"-nverts.txt", "r")
    edge_file = open(model+"-simplices.txt", "r")
    time_file = open(model+"-times.txt", "r")
    HGF = build_hypergraph_edge_filtration(size_file, edge_file, time_file, 10)
    size_file.close()
    edge_file.close()
    time_file.close()

    #print(HGF.time_range)
    #compute_originality_values(H)
    # H5 = HGF.get_sub_hypergraph(10)
    # plt.subplots(figsize=(5,5))
    hnx.draw(HGF.H.collapse_nodes_and_edges(),with_node_counts=True,with_edge_counts=True)
    # hnx.draw(H5)
    HGF.compute_time_range_from_weights(100)
    # HGF.plot_filtration(4, collapse = True)

    # HGF.compute_feature_steady_persistence(size_3_feature, display_progress=True)
    # HGF.compute_feature_steady_persistence(originality_feature, display_progress=True)
    # fig, ax_handle = plt.subplots()
    # HGF.steady_pd.plot_gudhi(ax_handle, labeling=True)
    HGF.compute_feature_steady_persistence(local_max_size_feature, display_progress=True)
    # fig, ax_handle = plt.subplots()
    # HGF.steady_pd.plot_gudhi(ax_handle, labeling=True)
    # HGF.compute_feature_steady_persistence(strict_hyperhub_feature, display_progress=True)
    fig, ax_handle = plt.subplots()
    HGF.steady_pd.plot_gudhi(ax_handle, labeling=True)
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
        if not e1 in not_max_edges:
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
