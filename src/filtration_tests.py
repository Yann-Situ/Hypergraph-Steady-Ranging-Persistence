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

H1 = {
    'e': {'v0', 'v1'}
}

H1_nw = {
    'v0' : 0,
    'v1' : 1
}

H1_ew = {
    'e': 0
}

def test_hypernet():
    H = hnx.Hypergraph(H1)
    node_weights = H1_nw
    edge_weights = H1_ew

    HGF = HyperGraphFiltration(H, node_weights, edge_weights)
    HGF.compute_time_range_from_weights()
    print(HGF.time_range)
    # H5 = HGF.get_sub_hypergraph(10)
    # fig, ax_handle = plt.subplots()
    # hnx.draw(HGF.H)
    # fig, ax_handle = plt.subplots()
    # hnx.draw(HGF.H.remove_edges([3,4]))
    # hnx.draw(HGF.H)
    # fig, ax_handle = plt.subplots()
    # hnx.draw(HGF.get_sub_hypergraph(0))
    # fig, ax_handle = plt.subplots()
    # hnx.draw(HGF.get_sub_hypergraph(1))
    # fig, ax_handle = plt.subplots()

    edges_kwargs={'linewidths': 2}
    node_labels_kwargs={'fontsize': 18}
    edge_labels_kwargs={'fontsize': 18}
    pos = {'v0':[0.0,0.0], 'v1':[1.0,0.0],'v2':[0.0,1.0],'v3':[1.0,1.0]}
    #
    # fig, ax_handle = plt.subplots()
    # hnx.draw(HGF.get_sub_hypergraph(0),node_radius = 5,
    #     pos = pos,
    #     edges_kwargs=edges_kwargs,
    #     node_labels_kwargs=node_labels_kwargs,
    #     edge_labels_kwargs=edge_labels_kwargs)
    #
    # fig, ax_handle = plt.subplots()
    # hnx.draw(HGF.get_sub_hypergraph(1),node_radius = 5,
    #     pos = pos,
    #     edges_kwargs=edges_kwargs,
    #     node_labels_kwargs=node_labels_kwargs,
    #     edge_labels_kwargs=edge_labels_kwargs)
    #
    # fig, ax_handle = plt.subplots()
    # hnx.draw(HGF.get_sub_hypergraph(0),node_radius = 5,
    #     pos = pos,
    #     edges_kwargs=edges_kwargs,
    #     node_labels_kwargs=node_labels_kwargs,
    #     edge_labels_kwargs=edge_labels_kwargs)

    HGF.plot_filtration(edges_kwargs=edges_kwargs, pos = pos,
    with_node_labels = True,
    node_labels_kwargs=node_labels_kwargs, edge_labels_kwargs=edge_labels_kwargs)
    plt.show()

################################################################################

if __name__ == "__main__":
    test_hypernet()
