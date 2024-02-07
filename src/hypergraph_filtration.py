# Hypergraph Filtration module
# Made by OneC2 - 2024
import networkx as nx
try:
    import hypernetx as hnx
except ImportError:
    print("HyperNetX not found")
    #!pip install hypernetx --quiet 2> /dev/null
    #print("Installation complete; please rerun this cell in order for the rest of the cells to use HyperNetX.")
    exit()

TQDM_FOUND = True
try:
    from tqdm import tqdm
except ImportError:
    print("tqdm not found: progress bars will not be available.")
    TQDM_FOUND = False

import matplotlib.pyplot as plt
from numpy import inf as INFINITY

from persistence import CornerPoint
from persistence import PersistenceDiagram

import warnings
warnings.simplefilter('ignore')

class HyperGraphFiltration:
    """
    Attributes
    ----------

    edge_weights : dictionary
        dictionary of weights of edges. No weight for an edge is considered as
        -inf.
    node_weights : dictionary
        dictionary of weights of nodes. No weight for an node is considered as
        -inf.
    """
    def __init__(self, hnx_hypergraph = None, node_weights = {}, edge_weights = {}):
        if hnx_hypergraph is not None:
            self.H = hnx_hypergraph
            self.edge_weights = edge_weights
            self.node_weights = node_weights
            self.time_range = sorted(set(list(edge_weights.values()) + list(node_weights.values())))
        else:
            raise ValueError("Specify hypergraph as a hypernetworkx hypergraph")

    # def get_filtration_values(self, sub_hypergraph, func):
    #     """Evaluates func on the weights defined on the edges
    #     """
    #     return func(np.asarray(list(nx.get_edge_attributes(sub_hypergraph,
    #                                                        'weight').values())))


    def get_sub_hypergraph_edges(self, time):
        """Returns the edges of self.H part of the sublevel set defined by time
        """
        return [edge for edge in self.H.edges
            if (not edge in self.edge_weights or self.edge_weights[edge] <= time)]
    def get_sub_hypergraph_nodes(self, time):
        """Returns the nodes of self.H part of the sublevel set defined by time
        """
        return [node for node in self.H.nodes
            if (not node in self.node_weights or self.node_weights[node] <= time)]

    def get_sub_hypergraph(self, time):
        """Returns the sub_hypergraph defined by edges. Once the filtration is
        generated we are only interested in the 'hubbiness' of a
        sub_hypergraph.
        """
        return self.H.restrict_to_nodes(self.get_sub_hypergraph_nodes(time)) \
            .restrict_to_edges(self.get_sub_hypergraph_edges(time))

    def compute_feature_steady_persistence(self, feature, above_max_diagonal_gap=False, gap_number=0, display_progress=False):
        """Compute steady persistence of a feature. Recall that an object
        is steady if it lives through consecutive sublevel sets of
        the filtration induced by the weights of the hupergraph.
        """
        # feature should be a function that takes a sub-hypergraph
        # (hypergraph-filtered) and gives the set of its featured sets
        if TQDM_FOUND and display_progress:
            self.feature_sets = [feature(self.get_sub_hypergraph(t)) for t in tqdm(self.time_range)]
        else:
            self.feature_sets = [feature(self.get_sub_hypergraph(t)) for t in self.time_range]
        # compute cornerpoints:
        self.steady_cornerpoints = []
        current_feature_set = {} # dictionary
        for i in range(len(self.time_range)):
            new_feature_set = self.feature_sets[i]
            for object, birth in current_feature_set.copy().items(): # use copy in order to safely delete items during iteration
                if object not in new_feature_set:
                    self.steady_cornerpoints.append(CornerPoint(0, birth, self.time_range[i], label = str(object)))#object.name
                    current_feature_set.pop(object)

            for object in new_feature_set:
                if object not in current_feature_set:
                    current_feature_set[object] = self.time_range[i]

        for object, birth in current_feature_set.items():
            self.steady_cornerpoints.append(CornerPoint(0, birth, INFINITY, label = str(object)))#object.name

        self.steady_pd = PersistenceDiagram(cornerpoints = self.steady_cornerpoints)
        if above_max_diagonal_gap:
            _,_ = self.steady_pd.get_nth_widest_gap(n = gap_number)
            self.steady_gap_number = gap_number


    def compute_ranging_from_steady_persistence(self, above_max_diagonal_gap=False, gap_number=0):
        """Compute ranging persistence of a feature from the previous
        steady persistence computation. Make sure that this function is
        called after calling `self.compute_feature_steady_persistence(...)`
        """
        self.ranging_cornerpoints = []
        # ... TODO
        self.ranging_pd = PersistenceDiagram(cornerpoints = self.ranging_cornerpoints)
        if above_max_diagonal_gap:
            _,_ = self.ranging_pd.get_nth_widest_gap(n = gap_number)
            self.ranging_gap_number = gap_numb

    def plot_filtration(self, nb_plot = None):
        """Plots all the sub hypergraphs of self.H given by considering the sublevel
        sets of the function defined on the weighted edges and nodes
        """
        positions = hnx.drawing.rubber_band.layout_node_link(self.H)
        n = len(self.time_range)
        if nb_plot == None:
            nb_plot = n
        k = 3
        if nb_plot % 3 != 0:
            if nb_plot % 4 == 0:
                k = 4
            if nb_plot % 5 == 0:
                k = 5
        fig, self.ax_arr = plt.subplots(int( (nb_plot-1)/k)+1,k)
        self.ax_arr = self.ax_arr.ravel()
        for i in range(nb_plot-1):
            t = self.time_range[int(i*(n-1.0)/(nb_plot-1.0))]
            sub_H = self.get_sub_hypergraph(t)
            draw_sub_hypergraph(sub_H, plot_weights = True, pos = positions, ax = self.ax_arr[i],
                        title = "t="+str(t)+" sublevel")
        # print last step
        t = self.time_range[-1]
        sub_H = self.get_sub_hypergraph(t)
        draw_sub_hypergraph(sub_H, plot_weights = True, pos = positions, ax = self.ax_arr[-1],
                    title = "t="+str(t)+" sublevel")

def draw_sub_hypergraph(hypergraph, plot_weights = True, pos = None, ax = None, title = None):
    """Plots a sub hypergraph using hypernetx wrappers

    Parameters
    ----------
    hypergraph : <hypernetx hypergraph>
        A hypergraph instance of hnx.Hypergraph()
    plot_weights : bool
        If True weights are plotted on the edges and nodes of the hypergraph
    ax : <matplotlib.axis._subplot>
        matplotlib axes handle
    title : string
        title to be attributed to ax
    """
    if hypergraph is None:
        print("Warning: hypergraph is None")
        exit()
    if title is not None:
        ax.set_title(title)
    hnx.draw(hypergraph, pos = pos, ax = ax)