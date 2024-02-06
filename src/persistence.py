# borrowed from the following [Generalized Persistence Analysis](https://github.com/LimenResearch/gpa) tool, made by Mattia Bergomi.
import numpy as np
from math import sqrt
from collections import Counter
import colorsys

import matplotlib.pyplot as plt
### UTILS
"""Local Gudhi plot
"""
def __min_birth_max_death(persistence, band_boot=0.):
    """This function returns (min_birth, max_death) from the persistence.

    :param persistence: The persistence to plot.
    :type persistence: list of tuples(dimension, tuple(birth, death)).
    :param band_boot: bootstrap band
    :type band_boot: float.
    :returns: (float, float) -- (min_birth, max_death).
    """
    # Look for minimum birth date and maximum death date for plot optimisation
    max_death = 0
    min_birth = persistence[0][1][0]
    for interval in reversed(persistence):
        if float(interval[1][1]) != float('inf'):
            if float(interval[1][1]) > max_death:
                max_death = float(interval[1][1])
        if float(interval[1][0]) > max_death:
            max_death = float(interval[1][0])
        if float(interval[1][0]) < min_birth:
            min_birth = float(interval[1][0])
    if band_boot > 0.:
        max_death += band_boot
    return (min_birth, max_death)

"""
Only 13 colors for the palette
"""
palette = ['#ff0000', '#00ff00', '#0000ff', '#00ffff', '#ff00ff', '#ffff00',
           '#000000', '#880000', '#008800', '#000088', '#888800', '#880088',
           '#008888']

def show_palette_values(alpha=0.6):
    """This function shows palette color values in function of the dimension.

    :param alpha: alpha value in [0.0, 1.0] for horizontal bars (default is 0.6).
    :type alpha: float.
    :returns: plot the dimension palette values.
    """
    colors = []
    for color in palette:
        colors.append(color)

    y_pos = np.arange(len(palette))

    plt.barh(y_pos, y_pos + 1, align='center', alpha=alpha, color=colors)
    plt.ylabel('Dimension')
    plt.title('Dimension palette values')
    return plt

def plot_persistence_diagram(persistence=[], persistence_file='', alpha=0.6,
                             band_boot=0., max_plots=0, cornerpoints = None,
                             coloring = False, labeling=False, legending=False):
    """This function plots the persistence diagram with an optional confidence band.

    :param persistence: The persistence to plot.
    :type persistence: list of tuples(dimension, tuple(birth, death)).
    :param persistence_file: A persistence file style name (reset persistence if both are set).
    :type persistence_file: string
    :param alpha: alpha value in [0.0, 1.0] for points and horizontal infinity line (default is 0.6).
    :type alpha: float.
    :param band_boot: bootstrap band (not displayed if :math:`\leq` 0.)
    :type band_boot: float.
    :param max_plots: number of maximal plots to be displayed
    :type max_plots: int.
    :returns: plot -- A diagram plot of persistence.
    """
    if persistence_file != '':
        if os.path.isfile(persistence_file):
            # Reset persistence
            persistence = []
            diag = read_persistence_intervals_grouped_by_dimension(persistence_file=persistence_file)
            for key in diag.keys():
                for persistence_interval in diag[key]:
                    persistence.append((key, persistence_interval))
        else:
            print("file " + persistence_file + " not found.")
            return None

    if max_plots > 0 and max_plots < len(persistence):
        # Sort by life time, then takes only the max_plots elements
        persistence = sorted(persistence, key=lambda life_time:
                             life_time[1][1]-life_time[1][0], reverse=True)[:max_plots]

    (min_birth, max_death) = __min_birth_max_death(persistence, band_boot)
    ind = 0
    delta = ((max_death - min_birth) / 10.0)
    # Replace infinity values with max_death + delta for diagram to be more
    # readable
    infinity = max_death + delta
    axis_start = min_birth - delta
    plt.plot([axis_start,infinity],[axis_start, infinity], color='k',
             alpha=alpha)
    plt.axhline(infinity,linewidth=1.0, color='k', alpha=alpha)
    plt.text(axis_start, infinity, r'$\infty$', color='k', alpha=alpha)
    # bootstrap band
    if band_boot > 0.:
        plt.fill_between(x, x, x+band_boot, alpha=alpha, facecolor='red')
    if cornerpoints is not None:
        reversed_cornerpoints = reversed(cornerpoints)
    else:
        reversed_cornerpoints = [None] * len(persistence)

    # Draw points in loop
    for interval, cp in zip(reversed(persistence), reversed_cornerpoints):
        print("plotting ", interval)
        # modified by OneC2:
        if not coloring or cp is None:
            color = palette[interval[0]]
        else:
            color = cp.color

        if not labeling or cp is None:
            label = None
        else:
            label = cp.label
        print("color: ", color)
        print("label: ", label)

        if float(interval[1][1]) != float('inf'):
            print("finite death")
            print("interval: ", interval[1][0], interval[1][1])

            plt.plot(interval[1][0], interval[1][1], alpha=alpha,
                        color = color, label=label, marker='o')
            if labeling and not label is None:  # labeling added by OneC2:
                plt.annotate(label, # this is the text
                    (interval[1][0],interval[1][1]), # these are the coordinates to position the label
                    textcoords="offset points", # how to position the text
                    xytext=(0,10), # distance from text to points (x,y)
                    ha='center') # horizontal alignment can be left, right or center
            plt.plot([interval[1][0],interval[1][0]],[interval[1][1], interval[1][0]],
                     color = color, alpha = alpha/2,
                     linestyle="dashed")
            plt.plot([interval[1][0],interval[1][1]],[interval[1][1], interval[1][1]],
                     color = color, alpha = alpha/2,
                     linestyle="dashed")

        else:
            print("infinte death")
            print("interval: ", interval[1][0], infinity)

            plt.plot(interval[1][0], infinity, alpha=alpha,
                        color = color, label=label, marker='o')
            if labeling and not label is None:  # labeling added by OneC2:
                plt.annotate(label, # this is the text
                    (interval[1][0],infinity), # these are the coordinates to position the label
                    textcoords="offset points", # how to position the text
                    xytext=(0,10), # distance from text to points (x,y)
                    ha='center') # horizontal alignment can be left, right or center
            plt.plot([interval[1][0],interval[1][0]],[interval[1][0], infinity],
                     color = color, alpha = alpha)
        ind = ind + 1

    plt.title('Persistence diagram')
    plt.xlabel('Birth')
    plt.ylabel('Death')
    if legending: # modified by OneC2
        plt.legend()
    # Ends plot on infinity value and starts a little bit before min_birth
    plt.axis([axis_start, infinity, axis_start, infinity + delta])
    return plt

###############################################################################
## PERSISTENCE_DIAGRAM

class CornerPoint:
    """A point of a persistence diagram

    Attributes
    ----------

    k : int
        degree (used normally in homological contexts)
    birth : float
        birth of the homological class represented by the cornerpoint
    death : float
        death of the homological class represented by the cornerpoint
    label : string
        name of the cornerpoint
    color : string (hex color)
        color of the cornerpoint
    """
    def __init__(self, k, birth, death, label = None, color=None):
        self.k = k
        self.birth = birth if birth <= death else death
        self.death = death if death >= birth else birth
        self.persistence = abs(death - birth)
        self.label = label
        self.color = color
        self.above_the_gap = False

    @property
    def is_cornerline(self):
        """True if self is a cornerline
        """
        return self.persistence == np.inf

    @property
    def is_proper(self):
        """True if self is a proper cornerpoint (not a cornerline)
        """
        return self.persistence != np.inf

    def __eq__(self, other):
        """True if self and other are the same cornerpoint
        """

        return self.birth == other.birth and self.death == other.death

    def __hash__(self):
        return hash((self.k, self.birth, self.death, self.persistence))

    def __repr__(self):
        return "Birth: {}\nDeath: {}\nVertices: {}".format(self.birth,
                                                           self.death,
                                                           self.label)


class PersistenceDiagram(object):
    """A persistence diagram is a multiset of 2-dimensional points called
    cornerpoints. The class allows to create a persistence diagram in two ways:

    * Giving a filtered complex, in this case it is possible to compute the
    persistence and hence the cornerpoints by using methods of this class

    * Giving a list of cornerpoints (with repetitions)

    Attributes
    ----------
    filtered_complex : <gudhi.SimplexTree>
        A SimplexTree instance
    cornerpoints : list
        List of tuples of the form (k, (b, d))
    """
    def __init__(self, cornerpoints = None):
        self.cornerpoints = cornerpoints
        self.get_cornerpoints_multiset()
        self.get_persistence_from_cornerpoints()

    def get_cornerpoints(self, proper = True):
        if proper:
            self.get_proper_cornerpoints()
            cps = self.proper_cornerpoints
        else:
            cps = self.cornerpoints
        return np.asarray([[c.birth, c.death] for c in cps])

    def get_persistence_from_cornerpoints(self):
        """Gets persistence in gudhi format from self.cornerpoints
        """
        self.persistence_to_plot = [(c.k, (c.birth, c.death))
                                    for c in self.cornerpoints]

    def plot_gudhi(self, ax_handle, cornerpoints=None, persistence_to_plot = None,
                   coloring = False, labeling=False, legending=False):
        """plots the persistence diagram in ax_handle

        coloring : bool
            if True, display the colors of persistence diagram's points.
        labeling : bool
            if True, display the labels of persistence diagram's points.
        legending : bool
            if True, display the legend of the persistence diagram.
        """
        cornerpoints = cornerpoints or self.cornerpoints
        persistence_to_plot = persistence_to_plot or self.persistence_to_plot
        ax_handle = plot_persistence_diagram(persistence_to_plot,
                                             cornerpoints = cornerpoints,
                                             coloring = coloring,
                                             labeling=labeling,
                                             legending=legending)
        return ax_handle

    def get_cornerpoint_objects(self):
        """Creates a list of CornerPoint instances
        """
        self.cornerpoints = [CornerPoint(k, b, d) for (k, (b, d)) in self.persistence]
        self.cornerpoints.sort(key=lambda x: x.persistence)
        self.get_cornerpoints_multiset()

    def get_cornerpoints_multiset(self):
        """Organises cornerpoints as a multiset in the form
        cornerpoint : multiplicity and generate as many colors as cornerpoints
        to eventually colorcode them.

        """
        self.cornerpoints_multiset = Counter(self.cornerpoints)
        self.colors = generate_n_distinct_colors(len(self.cornerpoints_multiset))

    def get_proper_cornerpoints(self):
        """Gets the list of proper cornerpoints (the ones with persistence
        smaller than infinity).
        """
        self.proper_cornerpoints = [c for c in self.cornerpoints_multiset
                                            if c.is_proper and not np.isnan(c.persistence)]
        self.proper_cornerpoints.sort(key=lambda x: x.persistence)

    def get_nth_widest_gap(self, n = 0):
        """Computes the widest gap according to the definition originally given
        in [2]_

        Parameters
        ----------

        n : int
            nth gap to consider. 1 is maximal, 2 the second maximal gap
            et cetera

        .. [2] Kurlin, Vitaliy. "A fast persistence-based segmentation of noisy
              2D clouds with provable guarantees." Pattern recognition letters
              83 (2016): 3-12.
        """
        if not hasattr(self, "proper_cornerpoints"):
            self.get_proper_cornerpoints()
        self.gap_number = n
        diagonal_gaps = np.diff([p.persistence for p in self.proper_cornerpoints])
        dg_index = np.argmax(diagonal_gaps)
        dg_index = np.argsort(diagonal_gaps)[::-1][self.gap_number]
        self.proper_cornerpoints_above_gap = self.proper_cornerpoints[dg_index + 1 :]
        [setattr(c, 'above_the_gap', True) for c in self.proper_cornerpoints_above_gap]
        return self.proper_cornerpoints[dg_index], self.proper_cornerpoints[dg_index + 1]

    def get_n_most_persistent_cornerpoints(self, n):
        """Get the first n cornerpoints according to their poersistence
        """
        if not hasattr(self, "proper_cornerpoints"):
            self.get_proper_cornerpoints()
        self.proper_cornerpoints_reversed = self.proper_cornerpoints[::-1]
        return self.proper_cornerpoints[: n + 1]

    def plot_nth_widest_gap(self, ax_handle = None, n = 0):
        """Plots the widest gap on the persistence diagram already plotted in
        ax_handle
        """
        if ax_handle is None:
            fig, ax_handle = plt.subplots()
        if hasattr(self, 'gap_number'):
            n = self.gap_number
        l, u = self.get_nth_widest_gap(n = n)
        x = np.asarray(ax_handle.get_xlim())
        y_l =  x + l.persistence
        y_u = x + u.persistence
        ax_handle.plot(x, y_l, ls="--", c=".3")
        ax_handle.plot(x, y_u, ls="--", c=".3")
        ax_handle.fill_between(x, y_l, y_u, facecolor='yellow', alpha=0.7)
        ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
        ax_handle.set_title("Visualizing the {} widest gap".format(ordinal(n)))

    def mark_points_above_diagonal_gaps(self, ax_handle):
        """Marks the points above the widest gap by circling them in red
        """
        for c in self.proper_cornerpoints_above_gap:
            ax_handle.plot(c.birth, c.death, 'o', ms=14, markerfacecolor="None",
             markeredgecolor='red', markeredgewidth=5)


def generate_n_distinct_colors(n):
    """Generates n distinct colors
    """
    hsv_tuples = [(i * 1.0 / n, 0.5, 0.5) for i in range(n)]
    return map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples)
