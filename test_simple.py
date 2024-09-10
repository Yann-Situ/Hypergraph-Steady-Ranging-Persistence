import matplotlib.pyplot as plt
from src.hypergraph_filtration import HyperGraphFiltration
import src.edge_features as feat

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
    edge_weights = {}
    i = 0
    for node in H.nodes:
        node_weights[node] = weight_test(i)
        i = i+1

    i = 0
    for edge in H.edges:
        edge_weights[edge] = weight_test(i*2.3)
        i = i+1
    print(edge_weights)
    # for edge in H.edges:
    #     print(set(H.incidence_dict[edge]))

    HGF = HyperGraphFiltration(H, node_weights, edge_weights)
    HGF.compute_time_range_from_weights()
    print(HGF.time_range)
    # H5 = HGF.get_sub_hypergraph(10)
    # fig, ax_handle = plt.subplots()
    # hnx.draw(HGF.H)
    # fig, ax_handle = plt.subplots()
    # hnx.draw(HGF.H.remove_edges([3,4]))
    HGF.plot_filtration()

    fig, ((ax0,ax1),(ax2,ax3)) = plt.subplots(2,2)
    HGF.compute_feature_steady_persistence(feat.strict_hyperhub_feature, display_progress=True)
    HGF.steady_pd.plot_gudhi(ax0, labeling=True)
    HGF.compute_feature_steady_persistence(feat.exclusivity_feature, display_progress=True)
    HGF.steady_pd.plot_gudhi(ax1, labeling=True)
    HGF.compute_feature_steady_persistence(feat.mean_originality_feature, display_progress=True)
    HGF.steady_pd.plot_gudhi(ax2, labeling=True)
    HGF.compute_feature_steady_persistence(feat.max_originality_feature, display_progress=True)
    HGF.steady_pd.plot_gudhi(ax3, labeling=True)
    plt.show()

################################################################################

if __name__ == "__main__":
    test_hypernet()
