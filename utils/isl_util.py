from typing import Union
import pandas
import numpy as np
import isl
from utils.common import CSource



def isl_mat_to_numpy(mat: isl.mat):
  return np.array([[mat.get_element_val(i, j).get_num_si()
                    for j in range(mat.cols())]
                   for i in range(mat.rows())])


def display_constraints(data: Union[isl.basic_map, isl.basic_set]):
  if isinstance(data, isl.basic_map):
    titles = bmap_dim_titles(data)
    eqs = isl_mat_to_numpy(data.equalities_matrix(isl.dim_type.CST,
                           isl.dim_type.PARAM,
                           isl.dim_type.IN,
                           isl.dim_type.OUT,
                           isl.dim_type.DIV))
    df_eq = pandas.DataFrame(eqs, columns=titles, index=[
                             '' for i in eqs]) if len(eqs) else None
    ineqs = isl_mat_to_numpy(data.inequalities_matrix(isl.dim_type.CST,
                             isl.dim_type.PARAM,
                             isl.dim_type.IN,
                             isl.dim_type.OUT,
                             isl.dim_type.DIV))
    df_ineq = pandas.DataFrame(ineqs, columns=titles, index=[
                               '' for i in ineqs]) if len(ineqs) else None
    return (df_ineq, df_eq)
  else:
    titles = bset_dim_titles(data)

    eqs = isl_mat_to_numpy(data.equalities_matrix(isl.dim_type.CST,
                                                  isl.dim_type.PARAM,
                                                  isl.dim_type.SET,
                                                  isl.dim_type.DIV))
    df_eq = pandas.DataFrame(eqs, columns=titles, index=[
                             '' for i in eqs]) if len(eqs) else None
    ineqs = isl_mat_to_numpy(data.inequalities_matrix(isl.dim_type.CST,
                                                      isl.dim_type.PARAM,
                                                      isl.dim_type.SET,
                                                      isl.dim_type.DIV))
    df_ineq = pandas.DataFrame(ineqs, columns=titles, index=[
                               '' for i in ineqs]) if len(ineqs) else None
    return (df_ineq, df_eq)


def bset_dim_titles(m: isl.basic_set):
  names = ["CST"]
  for t in [isl.dim_type.PARAM,
            isl.dim_type.SET,
            isl.dim_type.DIV]:
    for i in range(m.dim(t)):
      name = f"v{i}"
      try:
        name = m.dim_name(t, i)
      except Exception:
        pass
      names.append(t.name + " " + name)
  return names


def bmap_dim_titles(m: isl.basic_map):
  names = ["CST"]
  for t in [isl.dim_type.PARAM,
            isl.dim_type.IN,
            isl.dim_type.OUT,
            isl.dim_type.DIV]:
    for i in range(m.dim(t)):
      name = f"v{i}"
      try:
        name = m.dim_name(t, i)
      except Exception:
        pass
      names.append(t.name + " " + name)
  return names


def schedule_to_code(domain: isl.union_map, schedule: isl.map):
  tree = isl.schedule.from_domain(domain)
  tree = tree.insert_partial_schedule(schedule.as_multi_union_pw_aff())

  printer = isl.printer.to_file_path('/tmp/1.c')
  printer.set_output_format(isl.format.C)
  builder = isl.ast_build()
  ast: isl.ast_node = builder.node_from(tree)
  options = isl.ast_print_options.alloc()
  ast.print(printer, options)
  printer.flush()

  return CSource('/tmp/1.c')
