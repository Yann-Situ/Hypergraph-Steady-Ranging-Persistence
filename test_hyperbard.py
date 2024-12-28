from src.hypergraph_filtration import HyperGraphFiltration
import src.edge_features as feat

import matplotlib.pyplot as plt
import sys
import os.path

try:
    import hypernetx as hnx
except ImportError:
    print("HyperNetX not found")
    print("Installation complete; please try to install HyperNetX (for instance with a command like `pip install hypernetx`).")
    exit()

################################################################################

# Take an edges.csv file and return a list of dictionary, each dictionary represent a hyperedge.
# Note that this function was designed to work with the hyperbard dataset.
# strings_to_erase is a list of strings that should be replaced by "" when reading the file
def build_edgedict_from_hyperbard_file(file, strings_to_erase = []):
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

def usage():
    print("USAGE:")
    print("python3 test_hyperbard.py filename")
    print("----------------------------------")
    print("filename is a `*.edges.csv` file from the Hyperbard dataset.")
    print("This script opens a hyperbard file and build two hypergraph \
filtrations: the scene-hypergraph and the character-hypergraph filtrations. \
The script plots a sample of this two filtrations (for t=3,5,7,9).\n\
Then the script computes four persistence diagrams for each filtrations:\n\
    - the steady persistence for the hyperhub feature;\n\
    - the ranging persistence for the hyperhub feature;\n\
    - the steady(=ranging) persistence for the exclusivity feature;\n\
    - the steady(=ranging) persistence for the max originality feature.")

def test_hyperbard():
    if len(sys.argv) < 2:
        usage()
        return None
    
    filename = sys.argv[1]
    if not os.path.exists(filename):
        print("Error, the file "+filename+" doesn't exists")
        return None
    file = open(filename, "r")
    edgedict = build_edgedict_from_hyperbard_file(file, ["_Lr", "_Rom", "_Ham"])
    file.close()
    
    HGF = build_hypergraphfiltration_from_edgedict(edgedict,
        nodes_key = "onstage",
        name_key = None,
        weight_key = None)
    
    HGF.time_range = [3.0, 5.0, 7.0, 9.0] # arbitrary time values for the filtration plot
    
    ## plot scene-hypergraph
    HGF.plot_filtration(4, dual=False, with_node_labels = True, with_edge_labels = True)
    plt.tight_layout()
    
    ## plot character-hypergraph (dual of the first one)
    HGF.plot_filtration(4, dual=True, with_node_labels = True, with_edge_labels = True)
    plt.tight_layout()

    fig1, ax_scene = plt.subplots(2,2)
    fig1.suptitle('Persistence of the scene-hypergraph', fontsize=16)
    fig2, ax_character = plt.subplots(2,2)
    fig2.suptitle('Persistence of the character-hypergraph', fontsize=16)
    
    HGF.compute_time_range_from_weights()
    
    ## Compute scene-hypergraph persistence
    dual = False
    HGF.compute_feature_steady_persistence(feat.strict_hyperhub_feature, display_progress=True, dual = dual)
    HGF.compute_ranging_from_steady_persistence()
    ax_scene[0,0] = HGF.steady_pd.plot_gudhi(ax_scene[0,0], labeling=True, title="Steady hyperedge hub")
    ax_scene[0,1] = HGF.ranging_pd.plot_gudhi(ax_scene[0,1], labeling=True, title="Ranging hyperedge hub")
    
    HGF.compute_feature_steady_persistence(feat.exclusivity_feature, display_progress=True, dual = dual)
    ax_scene[1,0] = HGF.steady_pd.plot_gudhi(ax_scene[1,0], labeling=True, title="Exclusivity")
    
    HGF.compute_feature_steady_persistence(feat.max_originality_feature, display_progress=True, dual = dual)
    ax_scene[1,1] = HGF.steady_pd.plot_gudhi(ax_scene[1,1], labeling=True, title="Max originality")
    
    # HGF.compute_feature_steady_persistence(feat.mean_originality_feature, display_progress=True, dual = dual)
    # HGF.compute_ranging_from_steady_persistence()
    # ax_scene[2,0] = HGF.steady_pd.plot_gudhi(ax_scene[2,0], labeling=True, title="Steady mean originality")
    # ax_scene[2,1] = HGF.ranging_pd.plot_gudhi(ax_scene[2,1], labeling=True, title="Ranging mean originality")
    
    ## Compute character-hypergraph persistence
    dual = True
    HGF.compute_feature_steady_persistence(feat.strict_hyperhub_feature, display_progress=True, dual = dual)
    HGF.compute_ranging_from_steady_persistence()
    ax_character[0,0] = HGF.steady_pd.plot_gudhi(ax_character[0,0], labeling=True, title="Steady hyperedge hub")
    ax_character[0,1] = HGF.ranging_pd.plot_gudhi(ax_character[0,1], labeling=True, title="Ranging hyperedge hub")
    
    HGF.compute_feature_steady_persistence(feat.exclusivity_feature, display_progress=True, dual = dual)
    ax_character[1,0] = HGF.steady_pd.plot_gudhi(ax_character[1,0], labeling=True, title="Exclusivity")
    
    HGF.compute_feature_steady_persistence(feat.max_originality_feature, display_progress=True, dual = dual)
    ax_character[1,1] = HGF.steady_pd.plot_gudhi(ax_character[1,1], labeling=True, title="Max originality")
    
    # HGF.compute_feature_steady_persistence(feat.mean_originality_feature, display_progress=True, dual = dual)
    # HGF.compute_ranging_from_steady_persistence()
    # ax_character[2,0] = HGF.steady_pd.plot_gudhi(ax_character[2,0], labeling=True, title="Steady mean originality")
    # ax_character[2,1] = HGF.ranging_pd.plot_gudhi(ax_character[2,1], labeling=True, title="Ranging mean originality")
    
    fig1.tight_layout()
    fig2.tight_layout()
    plt.show()

################################################################################

if __name__ == "__main__":
    test_hyperbard()
