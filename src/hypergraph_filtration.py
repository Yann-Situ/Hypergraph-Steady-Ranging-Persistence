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
from numpy import linspace as linspace

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
    def __init__(self, hnx_hypergraph = None, node_weights = {}, edge_weights = {}, time_range = [0.0]):
        print("init HyperGraphFiltration")
        if hnx_hypergraph is not None:
            self.H = hnx_hypergraph
            self.edge_weights = edge_weights
            self.node_weights = node_weights
            if time_range == []:
                self.time_range = [0.0]
            else:
                self.time_range = time_range
        else:
            raise ValueError("Specify hypergraph as a hypernetworkx hypergraph")

    # def get_filtration_values(self, sub_hypergraph, func):
    #     """Evaluates func on the weights defined on the edges
    #     """
    #     return func(np.asarray(list(nx.get_edge_attributes(sub_hypergraph,
    #                                                        'weight').values())))
    def compute_time_range_from_weights(self, nb_sample = None):
        self.time_range = sorted(set(list(self.edge_weights.values()) + list(self.node_weights.values())))
        if nb_sample != None and nb_sample > 0 and nb_sample < len(self.time_range):
            self.time_range = [self.time_range[int(round(i))] for i in linspace(0, len(self.time_range)-1, nb_sample)]

    def get_sub_hypergraph_edges(self, time):
        """Returns the edges of self.H part of the sublevel set defined by time
        Warning: it also returns the edges that do not have weights.
        """
        return [edge for edge in self.H.edges
            if (not edge in self.edge_weights or self.edge_weights[edge] <= time)]

    def get_sup_hypergraph_edges(self, time):
        """Returns the edges of self.H part of the suplevel set defined by time
        Warning: it also returns the edges that do not have weights.
        """
        return [edge for edge in self.H.edges
            if (not edge in self.edge_weights or self.edge_weights[edge] > time)]

    def get_sub_hypergraph_nodes(self, time):
        """Returns the nodes of self.H part of the sublevel set defined by time.
        Warning: it also returns the nodes that do not have weights.
        """
        return [node for node in self.H.nodes
            if (not node in self.node_weights or self.node_weights[node] <= time)]

    def get_sup_hypergraph_nodes(self, time):
        """Returns the nodes of self.H part of the suplevel set defined by time.
        Warning: it also returns the nodes that do not have weights.
        """
        return [node for node in self.H.nodes
            if (not node in self.node_weights or self.node_weights[node] > time)]

    def get_sub_hypergraph(self, time, dual=False):
        """Returns the sub_hypergraph at time. If dual, returns the dual graph.
        """
        if dual:
            return self.H.restrict_to_nodes(self.get_sub_hypergraph_nodes(time)) \
                .remove_edges(self.get_sup_hypergraph_edges(time)).dual()
        else:
            return self.H.restrict_to_nodes(self.get_sub_hypergraph_nodes(time)) \
                .remove_edges(self.get_sup_hypergraph_edges(time))

    def compute_feature_steady_persistence(self, feature, above_max_diagonal_gap=False,
            gap_number=0, display_progress=False, dual=False):
        """Compute steady persistence of a feature. Recall that an object
        is steady if it lives through consecutive sublevel sets of
        the filtration induced by the weights of the hupergraph.
        """
        # feature should be a function that takes a sub-hypergraph
        # (hypergraph-filtered) and gives the set of its featured sets
        if TQDM_FOUND and display_progress:
            self.feature_sets = [feature(self.get_sub_hypergraph(t, dual=dual)) for t in tqdm(self.time_range)]
        else:
            self.feature_sets = [feature(self.get_sub_hypergraph(t, dual=dual)) for t in self.time_range]
        # compute cornerpoints:
        self.steady_cornerpoints = []
        current_feature_set = {} # dictionary
        for i in range(len(self.time_range)):
            new_feature_set = self.feature_sets[i]
            for object, birth in current_feature_set.copy().items(): # use copy in order to safely delete items during iteration
                if object not in new_feature_set:
                    self.steady_cornerpoints.append(
                        CornerPoint(0, birth, self.time_range[i],
                            label = str(object), object = object
                        ))
                    current_feature_set.pop(object)

            for object in new_feature_set:
                if object not in current_feature_set:
                    current_feature_set[object] = self.time_range[i]

        for object, birth in current_feature_set.items():
            self.steady_cornerpoints.append(
                CornerPoint(0, birth, INFINITY,
                    label = str(object), object = object
                ))#object.name

        self.steady_pd = PersistenceDiagram(cornerpoints = self.steady_cornerpoints,
            xmax = self.time_range[-1])
        if above_max_diagonal_gap:
            _,_ = self.steady_pd.get_nth_widest_gap(n = gap_number)
            self.steady_gap_number = gap_number


    def compute_ranging_from_steady_persistence(self, above_max_diagonal_gap=False, gap_number=0):
        """Compute ranging persistence of a feature from the previous
        steady persistence computation. Make sure that this function is
        called after calling `self.compute_feature_steady_persistence(...)`
        """
        self.ranging_cornerpoints = []
        ranging_corner_dict = {}
        for cp in self.steady_cornerpoints:
            if cp.object not in ranging_corner_dict:
                ranging_corner_dict[cp.object] = (cp.birth, cp.death)
            else:
                (b,d) = ranging_corner_dict[cp.object]
                ranging_corner_dict[cp.object] = (min(b,cp.birth) , max(d,cp.death))

        for object, (b,d) in ranging_corner_dict.items():
            self.ranging_cornerpoints.append(
                CornerPoint(0, b, d,
                    label = str(object), object = object
                ))

        self.ranging_pd = PersistenceDiagram(cornerpoints = self.ranging_cornerpoints,
            xmax = self.time_range[-1])
        if above_max_diagonal_gap:
            _,_ = self.ranging_pd.get_nth_widest_gap(n = gap_number)
            self.ranging_gap_number = gap_numb

    def plot_filtration(self, nb_plot = None, dual = False, collapse = False,
            with_node_labels = True, with_edge_labels = True, pos = None,
            edges_kwargs={}, nodes_kwargs={},
            node_labels_kwargs={}, edge_labels_kwargs={}):
        """Plots all the sub hypergraphs of self.H given by considering the sublevel
        sets of the function defined on the weighted edges and nodes
        """
        if pos is None:
            if collapse:
                if dual:
                    pos = hnx.drawing.rubber_band.layout_node_link(self.H.dual().collapse_nodes_and_edges())
                else:
                    pos = hnx.drawing.rubber_band.layout_node_link(self.H.collapse_nodes_and_edges())
            else:
                if dual:
                    pos = hnx.drawing.rubber_band.layout_node_link(self.H.dual())
                else:
                    pos = hnx.drawing.rubber_band.layout_node_link(self.H)
        # for i, (node, posi) in enumerate(pos.items()):
        #     print(str(i)+' '+str(node))
        #     # print(posi)
        #     pos[node] = [i*1.0, 0.0]

        edgecolors = {}
        if dual:
            temp_colors = [plt.cm.tab10(i % 10) for i in range(len(self.H.dual().edges))]
        else:
            temp_colors = [plt.cm.tab10(i % 10) for i in range(len(self.H.edges))]
        for i, edge in enumerate(self.H.edges):
            edgecolors[edge] = temp_colors[i]
        edges_kwargs['edgecolors'] = edgecolors

        if dual:
            edges_kwargs, nodes_kwargs = nodes_kwargs, edges_kwargs
            edges_labels_kwargs, nodes_labels_kwargs = node_labels_kwargs, edge_labels_kwargs

        n = len(self.time_range)
        if nb_plot == None:
            nb_plot = n
        k = 3
        if nb_plot % 3 != 0:
            if nb_plot % 4 == 0:
                k = 4
            if nb_plot % 5 == 0:
                k = 5
        if nb_plot == 4:
            k = 2
        fig, self.ax_arr = plt.subplots(int( (nb_plot-1)/k)+1,k)
        self.ax_arr = self.ax_arr.ravel()
        for i in range(nb_plot):
            if i == nb_plot-1:
                t = self.time_range[-1]
            else:
                t = self.time_range[int(i*(n-1.0)/(nb_plot-1.0))]
            sub_H = self.get_sub_hypergraph(t, dual=dual)
            draw_sub_hypergraph(sub_H, collapse = collapse, pos = pos, ax = self.ax_arr[i],
                        title = '',#"t="+str(t),
                        with_node_labels = with_node_labels,
                        with_edge_labels = with_edge_labels,
                        edges_kwargs=edges_kwargs, nodes_kwargs=nodes_kwargs,
                        node_labels_kwargs=node_labels_kwargs, edge_labels_kwargs=edge_labels_kwargs)

def draw_sub_hypergraph(hypergraph, collapse = False, pos = None, ax = None,
        title = None, with_node_labels = True, with_edge_labels = True,
        edges_kwargs={}, nodes_kwargs={},
        node_labels_kwargs={}, edge_labels_kwargs={}):
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

    if collapse:
        hnx.draw(hypergraph.collapse_nodes_and_edges(),
            with_node_counts=True,with_edge_counts=True,
            pos = pos, ax = ax,
            with_node_labels = with_node_labels, with_edge_labels = with_edge_labels,
            edges_kwargs=edges_kwargs, nodes_kwargs=nodes_kwargs,
            node_labels_kwargs=node_labels_kwargs, edge_labels_kwargs=edge_labels_kwargs,
            node_radius = 5,label_alpha = 0.65)
    else:
        hnx.draw(hypergraph, pos = pos, ax = ax,
            with_node_labels = with_node_labels, with_edge_labels = with_edge_labels,
            edges_kwargs=edges_kwargs, nodes_kwargs=nodes_kwargs,
            node_labels_kwargs=node_labels_kwargs, edge_labels_kwargs=edge_labels_kwargs,
            node_radius = 5,label_alpha = 0.65)
