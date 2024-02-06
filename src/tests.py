import matplotlib.pyplot as plt
from hypergraph_filtration import HyperGraphFiltration

try:
    import hypernetx as hnx
except ImportError:
    print("HyperNetX not found")
    #!pip install hypernetx --quiet 2> /dev/null
    #print("Installation complete; please rerun this cell in order for the rest of the cells to use HyperNetX.")
    exit()

import warnings
warnings.simplefilter('ignore')

def weight_test(i):
    return int(10.0 * (i/12.0 * i/11.0))

def test_hypernet():
    scenes = {
        0: {'FN' : {'w':1}, 'TH': {'w':2}},
        1: {'TH' : {'w':1}, 'JV': {'w':3}},
        2: {'BM' : {'w':1}, 'FN': {'w':3}, 'JA': {'w':2}},
        3: {'JV' : {'w':1}, 'JU': {'w':4}, 'CH': {'w':3}, 'BM': {'w':6}},
        4: {'JU' : {'w':1}, 'CH': {'w':5}, 'BR': {'w':4}, 'CN': {'w':5}, 'CC': {'w':7}, 'JV': {'w':8}, 'BM': {'w':9}},
        5: {'TH' : {'w':1}, 'GP': {'w':6}},
        6: {'GP' : {'w':1}, 'MP': {'w':7}},
        7: {'MA' : {'w':1}, 'GP': {'w':8}}
    }
    H = hnx.Hypergraph(scenes, cell_weight_col='w', sort=False)

    node_weights = {}
    i = 0
    for node in H.nodes:
        node_weights[node] = weight_test(i)
        i = i+1
    edge_weights = {}

    # i = 0
    # for edge in H.edges:
    #     edge_weights[edge] = i
    #     i = i+1
    # for edge in H.edges:
    #     print(set(H.incidence_dict[edge]))

    HGF = HyperGraphFiltration(H, node_weights, edge_weights)
    print(HGF.time_range)
    compute_originality_values(H)
    # H5 = HGF.get_sub_hypergraph(10)
    # plt.subplots(figsize=(5,5))
    # #hnx.draw(H)
    # hnx.draw(H5)
    HGF.plot_filtration()

    #HGF.compute_feature_steady_persistence(size_3_feature, display_progress=True)
    HGF.compute_feature_steady_persistence(originality_feature, display_progress=True)
    print(HGF.steady_pd)
    fig, ax_handle = plt.subplots()
    HGF.steady_pd.plot_gudhi(ax_handle, labeling=True)
    plt.show()

def size_3_feature(hypergraph):
    r = [edge for edge in hypergraph.edges
        if hypergraph.size(edge)==3 or hypergraph.size(edge)==2]
    return r #set(r)

def compute_originality_values(hypergraph):
    max_intersections = {edge : 0 for edge in hypergraph.edges}
    processed_edge = set()
    for edge in hypergraph.edges:
        edge_nodes = set(hypergraph.incidence_dict[edge])
        processed_edge.add(edge)
        for neighbor in set(hypergraph.edge_neighbors(edge)).difference(processed_edge):
            d = len(edge_nodes.intersection(hypergraph.incidence_dict[neighbor]))
            max_intersections[edge] = max(d, max_intersections[edge])
            max_intersections[neighbor] = max(d, max_intersections[neighbor])
    #print(max_intersections)
    for e, n in max_intersections.items():
        max_intersections[e] = 1.0 - n/(1.0*hypergraph.size(e))
    return max_intersections

def originality_feature(hypergraph, t = 0.5):
    originalities = compute_originality_values(hypergraph)
    return {e for e, o in originalities.items() if o > t}

if __name__ == "__main__":
    test_hypernet()
