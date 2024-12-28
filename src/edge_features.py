try:
    import hypernetx as hnx
except ImportError:
    print("HyperNetX not found")
    #!pip install hypernetx --quiet 2> /dev/null
    #print("Installation complete; please rerun this cell in order for the rest of the cells to use HyperNetX.")
    exit()

############################# HELP FUNCTIONS ###################################

def compute_max_originality_values(H):
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

def compute_mean_originality_values(H):
    sum_intersections = {edge : 0 for edge in H.edges}
    processed_edge = set()
    for edge in H.edges:
        edge_nodes = set(H.incidence_dict[edge])
        processed_edge.add(edge)
        for neighbor in set(H.edge_neighbors(edge)).difference(processed_edge):
            d = len(edge_nodes.intersection(H.incidence_dict[neighbor]))
            sum_intersections[edge] += d
            sum_intersections[neighbor] += d
    #print(max_intersections)
    for e, n in sum_intersections.items():
        lneighb = len(H.edge_neighbors(e))
        if lneighb > 0:
            sum_intersections[e] = 1.0 - n/(lneighb*H.size(e))
        else:
            sum_intersections[e] = 1.0
    return sum_intersections

################################################################################

def max_originality_feature(H, t = 0.5):
    """
    Return the set of edges whose max-originality is greater than t.
    The max-originality of an edge e is:
    O(e) = 1 - max_{e'\in N(e)}|e \cap e'|/|e|
    """
    originalities = compute_max_originality_values(H)
    return {e for e, o in originalities.items() if o > t}

def mean_originality_feature(H, t = 0.75):
    """
    Return the set of edges whose mean-originality is greater than t.
    the mean-originality of an edge e is:
    o(e) = 1 - sum_{e'\in N(e)}|e \cap e'|/|N(e)||e|
    """
    originalities = compute_mean_originality_values(H)
    return {e for e, o in originalities.items() if o > t}

def local_max_size_feature(H):
    """
    Return the set of edges whose size is bigger than the size of
    their neighbor.
    """
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

def exclusivity_feature(H):
    """
    Return the set of edges that have an exclusivity,
    i.e the edges that contain a node that is not contained in another edge.
    """
    r = set()
    for e in H.edges:
        for n in H.incidence_dict[e]:
            if H.degree(n, s=1) == 1:
                r.add(e)
                break
    return r

def strict_hyperhub_feature(H):
    """
    Return the set of edges that have strictly more neighbors than their neighbors.
    """
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
