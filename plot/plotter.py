import matplotlib.pyplot as _plt
from matplotlib import colormaps
from matplotlib import collections
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Circle
from matplotlib.ticker import MaxNLocator
from matplotlib.transforms import Affine2D
import isl
from plot.support import *
from typing import Tuple, List, Union, Deque
from dataclasses import dataclass


@dataclass
class ProcessorMap:
  Domain: isl.basic_set
  Range: range


def plot_set_points(set_datas: Union[isl.set, List[isl.set]], color="black", size=10, marker="o", scale=1, labels: List[str] = None, ax: _plt.Axes = None):
  """
  Plot the individual points of a two dimensional isl set.

  :param set_datas: The islpy.Set to plot.
  :param color: The color of the points.
  :param size: The diameter of the points.
  :param marker: The marker used to mark a point.
  :param scale: Scale the values.
  """
  if isinstance(set_datas, (isl.set, isl.basic_set, isl.union_set)):
    set_datas = [set_datas]
  if labels is None:
    labels = ["", ""]
    for set_data in set_datas:
      set_labels = []
      sp = set_data.get_space()
      for i in range(2):
        if sp.dim(isl.dim_type.SET) > i:
          if sp.has_dim_name(isl.dim_type.SET, i):
            set_labels.append(sp.get_dim_name(isl.dim_type.SET, i))
          else:
            set_labels.append("")
      set_labels.reverse()
      for i in range(2):
        if labels[i] == "" and i < len(set_labels):
          labels[i] = set_labels[i]
  if ax is None:
    ax: _plt.Axes = _plt.gca()
  for set_data in set_datas:
    points = bset_get_points(set_data, scale=scale)
    dimX = [x[1] for x in points]
    dimY = [x[0] for x in points]
    ax.plot(dimX, dimY, marker, markersize=size, color=color, lw=0)
  if labels is not None:
    ax.set_xlabel(labels[0])
    ax.set_ylabel(labels[1], rotation=0)
  ax.xaxis.set_major_locator(MaxNLocator(integer=True))
  ax.yaxis.set_major_locator(MaxNLocator(integer=True))


def _plot_arrow(start, end, graph, *args, **kwargs):
  """
  Plot an arrow from start to end.

  :param start: The start position.
  :param end: The end position.
  :param style: The line style to use (default is "->").
  :param width: The width of the line.
  :param color: The color of the line.
  """
  style = kwargs.pop("style", "->")
  width = kwargs.pop("width", 1)
  color = kwargs.pop("color", "black")
  shrink = kwargs.pop("shrink", 10)

  if (start == end):
    a, b = start
    graph.annotate("", xy=(a, b + .15), xycoords='data',
                   xytext=start, textcoords='data',
                   arrowprops=dict(arrowstyle=style,
                                   connectionstyle="arc3",
                                   shrinkA=0,
                                   shrinkB=0,
                                   linewidth=width,
                                   mutation_scale=15,
                                   color=color)
                   )
    return

  graph.annotate("", xy=end, xycoords='data',
                 xytext=start, textcoords='data',
                 arrowprops=dict(arrowstyle=style,
                                 connectionstyle="arc",
                                 shrinkA=shrink,
                                 shrinkB=shrink,
                                 linewidth=width,
                                 mutation_scale=15,
                                 color=color)
                 )


def plot_map(maps: Union[List[isl.union_map], isl.union_map], edge_style="-|>", edge_width=1,
             start_color="blue", end_color="orange", line_color="black", marker_size=7,
             scale=1, shrink=6):
  """
  Given a map from a two dimensional set to another two dimensional set this
  functions prints the relations in this map as arrows going from the input
  to the output element.

  :param map_datas: The islpy.Map to plot.
  :param color: The color of the arrows.
  :param edge_style: The style used to plot the arrows.
  :param edge_width: The width used to plot the arrows.
  :param shrink: The distance before around the start/end which is not plotted
                 to.
  :param scale: Scale the values.
  """

  bmap_datas: List[isl.basic_map] = []
  labels: List[str] = []
  if not isinstance(maps, list):
    maps = [maps]
  for umap in maps:
    umap.foreach_map(lambda map: map.foreach_basic_map(lambda bmap: bmap_datas.append(bmap)))

  # try get the labels
  if len(labels) == 0:
    labels = ["", ""]
    for bmap_data in bmap_datas:
      bmap_labels = []
      sp = bmap_data.get_space()
      for i in range(2):
        if sp.dim(isl.dim_type.OUT) > i:
          if sp.has_dim_name(isl.dim_type.OUT, i):
            bmap_labels.append(sp.get_dim_name(isl.dim_type.OUT, i))
          else:
            bmap_labels.append("")
      bmap_labels.reverse()
      for i in range(2):
        if labels[i] == "" and i < len(bmap_labels):
          labels[i] = bmap_labels[i]

  for bmap_data in bmap_datas:
    all_start: List[Tuple[int, int]] = []
    all_ends: List[Tuple[int, int]] = []
    start_points: List[isl.point] = []
    bmap_data.range().foreach_point(start_points.append)
    for start in start_points:
      end_points: List[isl.point] = []
      limited = bmap_data.intersect_range(isl.set(start))
      limited.domain().foreach_point(end_points.append)
      s = get_point_coordinates(start, scale)
      s.reverse()
      all_start.append(s)
      for end in end_points:
        e = get_point_coordinates(end, scale)
        e.reverse()
        all_ends.append(e)
        _plot_arrow(e,
                    s,
                    _plt, color=line_color, style=edge_style,
                    width=edge_width, shrink=shrink)
    _plt.plot([x[0] for x in all_start], [x[1]
              for x in all_start], "o", markersize=marker_size, color=start_color, lw=0)
    _plt.plot([p[0] for p in all_ends], [p[1]
              for p in all_ends], "o", markersize=marker_size, color=end_color, lw=0)
  ax: _plt.Axes = _plt.gca()
  if labels[0] is not None:
    _plt.xlabel(labels[0])
  if labels[1] is not None:
    _plt.ylabel(labels[1], rotation=0)
  ax.xaxis.set_major_locator(MaxNLocator(integer=True))
  ax.yaxis.set_major_locator(MaxNLocator(integer=True))


def plot_bset_shape(bset_data: isl.basic_set, show_vertices=True, color="gray",
                    alpha=1.0,
                    vertex_color=None,
                    vertex_marker="o", vertex_size=10,
                    scale=1, border=0, ax: _plt.Axes = None):
  """
  Given an basic set, plot the shape formed by the constraints that define
  the basic set.

  :param bset_data: The basic set to plot.
  :param show_vertices: Show the vertices at the corners of the basic set's
                        shape.
  :param color: The background color of the shape.
  :param alpha: The alpha value to use for the shape.
  :param vertex_color: The color of the vertex markers.
  :param vertex_marker: The marker used to draw the vertices.
  :param vertex_size: The size of the vertices.
  :param border: Increase the size of the area filled with the background
                 by the value given as 'border'.
  :param scale: Scale the values.
  """

  assert bset_data.is_bounded(), "Expected bounded set"

  if not vertex_color:
    vertex_color = color

  vertices = bset_get_vertex_coordinates(bset_data, scale=scale)

  if show_vertices:
    dimX = [x[1] for x in vertices]
    dimY = [x[0] for x in vertices]
    _plt.plot(dimX, dimY, vertex_marker, markersize=vertex_size,
              color=vertex_color)

  if len(vertices) == 0:
    return

  codes = [Path.LINETO] * len(vertices)
  codes[0] = Path.MOVETO
  pathdata = [(code, tuple(coord)) for code, coord in zip(codes, vertices)]
  pathdata.append((Path.CLOSEPOLY, (0, 0)))
  codes, verts = zip(*pathdata)
  t = Affine2D().translate(1, 0)
  path = Path(verts, codes)

  linewidth = 0
  fill = True

  if len(vertices) == 2:
    linewidth = 2
    fill = False

  pathes = []
  import math
  steps = 200
  for i in range(steps):
    pi = i * 2 * math.pi / steps
    offset = border
    x = math.sin(pi) * offset
    y = math.cos(pi) * offset
    t = Affine2D().translate(x, y)
    pathT = path.transformed(t)
    pathes.append(pathT)

  for p in pathes:
    path = Path.make_compound_path(path, p)

  if len(vertices) == 1:
    patch = Circle(vertices[0], border, color=color,
                   alpha=alpha)
  else:
    patch = PathPatch(path, alpha=alpha, linewidth=linewidth,
                      color=color, fill=fill)
  if ax is None:
    ax = _plt.gca()
  ax.add_patch(patch)


def plot_set_shapes(set_data, *args, **kwargs):
  """
  Plot a set of concex shapes for the individual basic sets this set consists
  of.

  :param set_data: The set to plot.
  """

  assert set_data.is_bounded(), "Expected bounded set"

  set_data.foreach_basic_set(lambda x: plot_bset_shape(x, **kwargs))


def plot_map_as_groups(bmap: isl.basic_map, processors_mapping: ProcessorMap = None, color="gray", alpha=1.0,
                       vertex_color=None, vertex_marker="o",
                       vertex_size=10, scale=1, border=0.15, ax: _plt.Axes = None):
  """
  Plot a map in groups of convex sets

  This function expects a map that assigns each domain element a single
  group id, such that each group forms a convex set of points. This function
  plots now each group as such a convex shape.

  This is e.g. useful to illustrate a tiling that is given as a between
  iteration vectors to tile ids.

  :param bmap: The map defining the groups of convex sets.
  :param processors_mapping: A map of the parallell executed processors hyperplanes.
  :param vertex_color: The color the vertices are plotted.
  :param vertex_size: The size the vertices are plotted.
  :param vertex_marker: The marker the vertices are plotted as.
  :param color: The color the shapes are plotted.
  :param border: Increase the size of the area filled with the background
                 by the value given as 'border'.
  :param alpha: The alpha the shapes are plotted.
  """

  if not vertex_color and color is str:
    vertex_color = color

  def plot_group_points(points: List[isl.point], region_color: str):
    for point in points:
      point_set = isl.basic_set(point)
      part_set: isl.set = bmap.intersect_range(point_set).domain()
      part_set_convex: isl.basic_set = part_set.convex_hull()

      # We currently expect that each group can be represented by a
      # single convex set.
      assert (part_set.is_equal(part_set_convex))

      part_set = part_set_convex

      # plot_set_points(part_set, color=vertex_color, size=vertex_size,
      #                 marker=vertex_marker, scale=scale)
      part_set = part_set.remove_divs()
      plot_bset_shape(part_set, color=region_color, alpha=alpha,
                      vertex_color=vertex_color,
                      vertex_size=vertex_size, vertex_marker=vertex_marker,
                      show_vertices=False, scale=scale, border=border, ax=ax)

  range: isl.set = bmap.range()
  if processors_mapping is None:
    points: List[isl.point] = []
    range.foreach_point(points.append)
    plot_group_points(points, color)
  else:
    colorbars = colormaps[color].resampled(len(processors_mapping.Range))
    for processor_id in processors_mapping.Range:
      processor_range = range.intersect(processors_mapping.Domain.intersect_params(
          isl.set(f"[P] -> {{ : P = {processor_id} }}")))
      points: List[isl.point] = []
      processor_range.foreach_point(points.append)
      plot_group_points(points, colorbars(processor_id))


def plot_domain(domain, dependences=None, tiling=None, space=None, processors_mapping: ProcessorMap = None,
                tile_color="skyblue", tile_alpha=1,
                vertex_color="black", vertex_size=10,
                vertex_marker="o", background=True,
                bg_vertex_color="lightgray", bg_vertex_size=10,
                bg_vertex_marker="o",
                dep_color="gray", dep_style="->", dep_width=1,
                shrink=6, border=0.15
                ):
  """
  Plot an iteration space domain and related information.


  :param domain: The domain of the iteration space
  :param dependences: The dependences between the different iterations
  :param tiling: A mapping from iteration space groups onto their corresponding
                 (possibly multi-dimensional) tile ID.
  :param processers_mapping: A processers mapping of the hyperplanes
  :param space: Show the data after mapping it to a new space.
  :param tile_color: The color to use for the tile shape.
  :param tile_alpha: The alpha value used for the tile background.
  :param vertex_color: The color of the vertex markers.
  :param vertex_marker: The marker used to draw the vertices.
  :param vertex_size: The size of the vertices.
  :param background: If a background should be printed.
  :param bg_vertex_color: The color of the vertex markers.
  :param bg_vertex_marker: The marker used to draw the vertices.
  :param bg_vertex_size: The size of the vertices.
  :param dep_color: The color used to plot the dependency arrows.
  :param dep_style: The style used to plot the dependency arrows.
  :param dep_width: The width used to plot the dependency arrows.
  :param shrink: The distance before around the start/end of the dependences
                 around which is not plotted.
  :param border: Increase the size of the area filled with the background
                 by the value given as 'border'.
  """

  if space:
    domain = domain.apply(space)
    if dependences:
      dependences = dependences.apply_range(space)
      dependences = dependences.apply_domain(space)
    if tiling:
      tiling = tiling.apply_domain(space)

  if background:
    hull = get_rectangular_hull(domain, 1)
    plot_set_points(hull, color=bg_vertex_color, size=bg_vertex_size,
                    marker=bg_vertex_marker)

  plot_set_points(domain, color=vertex_color, size=vertex_size,
                  marker=vertex_marker)

  if dependences:
    dependences = dependences.intersect_range(domain)
    dependences = dependences.intersect_domain(domain)
    if tiling:
      same_tile = tiling.apply_range(tiling.reverse())
      dependences = dependences.subtract(same_tile)
    plot_map(dependences, line_color=dep_color, edge_style=dep_style,
             edge_width=dep_width, shrink=shrink)

  if tiling:
    tiling = tiling.intersect_domain(domain)
    plot_map_as_groups(tiling, processors_mapping, color=tile_color, vertex_color=vertex_color,
                       vertex_size=vertex_size, vertex_marker=vertex_marker,
                       alpha=tile_alpha, border=border)


__all__ = ['plot_set_points', 'plot_bset_shape', 'plot_set_shapes',
           'plot_map', 'plot_map_as_groups', 'plot_domain']
