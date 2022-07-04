import numpy as np
from scipy.stats import linregress
import scipy.stats
import copy


def referential(requested_data_values, hierarchyOfInterest, periodOfInterest, plannedAmount, referential_period):
    for row in requested_data_values:
        deep_row = copy.deepcopy(row)
        hierarchy = deep_row['hierarchy']
        del deep_row['hierarchy']
        del deep_row['id']

        if  hierarchy[-1] == hierarchyOfInterest:         
            periods = list(deep_row.keys())
            periods.sort()
            findPeriodOfInterest = periods.index(periodOfInterest)
            new_periods = periods[:findPeriodOfInterest]
            reference_period = referential_period
            previousValue = deep_row[reference_period]

            probabilityValue = (plannedAmount - previousValue) / previousValue
            probabilityValue = probabilityValue + 1
            break
    
    for row in requested_data_values:
        deep_copy_row = copy.deepcopy(row)
        hierarchy = deep_copy_row['hierarchy']
        del deep_copy_row['hierarchy']
        del deep_copy_row['id']
        if len(hierarchy) != 1 and hierarchy[-2] == hierarchyOfInterest:
            periods = list(deep_row.keys())
            periods.sort()
            # print(periods)
            findPeriodOfInterest = periods.index(periodOfInterest)
            new_periods = periods[:findPeriodOfInterest]
            # reference_period = new_periods[-1]
            reference_period = referential_period
            
            row[periodOfInterest] = probabilityValue * row[reference_period]
        if len(hierarchy) != 1 and hierarchy[-1] == hierarchyOfInterest:
            row[periodOfInterest] = plannedAmount
    return requested_data_values

def proportional(requested_data_values, hierarchyOfInterest, periodOfInterest, plannedAmount):
    hierarchy_list = []
    for row in requested_data_values:
        deep_copy_row = copy.deepcopy(row)
        hierarchy = deep_copy_row['hierarchy']
        del deep_copy_row['hierarchy']
        del deep_copy_row['id']
        if len(hierarchy) != 1 and hierarchy[-2] == hierarchyOfInterest:
            hierarchy_list.append(hierarchy[-1])
    
    for row in requested_data_values:
        deep_copy_row = copy.deepcopy(row)
        hierarchy = deep_copy_row['hierarchy']
        del deep_copy_row['hierarchy']
        del deep_copy_row['id']
        if len(hierarchy) != 1 and hierarchy[-2] == hierarchyOfInterest:
            row[periodOfInterest] = plannedAmount / len(hierarchy_list)
        if len(hierarchy) != 1 and hierarchy[-1] == hierarchyOfInterest:
            row[periodOfInterest] = plannedAmount
    return requested_data_values

def average(requested_data_values, hierarchyOfInterest, periodOfInterest, plannedAmount):
    hierarchy_list = []
    for row in requested_data_values:
        deep_copy_row = copy.deepcopy(row)
        hierarchy = deep_copy_row['hierarchy']
        del deep_copy_row['hierarchy']
        del deep_copy_row['id']
        periods = list(deep_copy_row.keys())
        periods.sort()
        periods_of_interest = [i for i in periods if i < periodOfInterest]
        y_l = list()
        if len(hierarchy) != 1 and hierarchy[-2] == hierarchyOfInterest:
            hierarchy_list.append(hierarchy[-1])
            for xs in periods_of_interest:
                y_l.append(deep_copy_row[xs])
            row[periodOfInterest] = np.mean(y_l)
        if len(hierarchy) != 1 and hierarchy[-1] == hierarchyOfInterest:
            hierarchy_list.append(hierarchyOfInterest)
            for xs in periods_of_interest:
                y_l.append(deep_copy_row[xs])
            row[periodOfInterest] = np.mean(y_l)
    return requested_data_values


def interval(requested_data_values, hierarchyOfInterest, periodOfInterest, plannedAmount, plan_constraints, individual_constraints, locked_item):
    max_value, min_value = [], []
    hierarchy_list = []

    for row in requested_data_values:
        if row['hierarchy'][len(row['hierarchy']) - 1] == hierarchyOfInterest:
            row[periodOfInterest] = plannedAmount
            break

    for row in requested_data_values:
        deep_copy_row = copy.deepcopy(row)
        hierarchy = deep_copy_row['hierarchy']
        del deep_copy_row['hierarchy']
        del deep_copy_row['id']
        if len(hierarchy) != 1 and hierarchy[-2] == hierarchyOfInterest and hierarchy[-1] not in locked_item:
            hierarchy_list.append(hierarchy[-1])
            periods = list(deep_copy_row.keys())
            periods.sort()
            periods_of_interest = [i for i in periods if i < periodOfInterest]
            y_l = list()
            for xs in periods_of_interest:
                y_l.append(deep_copy_row[xs])

            y_l = np.array(y_l, dtype=np.float64)
            x_l = np.array(list(range(0, len(periods_of_interest))), dtype=np.float64)
            n = len(x_l)
            b1, b0, r_value, p_value, std_err = linregress(x_l, y_l) # fit linear regression model
            yhat = b0 + b1 * (len(y_l) + 1)
            sse = np.sum((yhat - y_l) ** 2)
            mse = sse / (n - 2)
            tval = -scipy.stats.t.ppf(q=0.025, df = len(y_l))
            pred_se = (1 + (1 / n) + np.sum((len(x_l) + 1) - np.mean(x_l))**2 / np.sum((x_l - np.mean(x_l))**2))
            lower = yhat - tval * np.sqrt(mse * pred_se)
            upper = yhat + tval * np.sqrt(mse * pred_se)            
            max_value.append(upper)
            min_value.append(lower)

    if len(individual_constraints) != 0 and individual_constraints[0]['hierarchyOne'] != 'None':
        dom = domain_generator(hierarchy_list, periodOfInterest, min_value, max_value)
        constraints, arcs = constraints_arc_generator(individual_constraints, periodOfInterest, requested_data_values)
        consistency, domains = forward_checking(dom, constraints, arcs)
        new_min_value = []
        new_max_value = []
        new_hierarchy_list = []
        for k,v in domains.items():
            new_hierarchy_list.append(k)
            new_min_value.append(v[periodOfInterest][0])
            new_max_value.append(v[periodOfInterest][1])
        hierarchy_list = new_hierarchy_list
        min_value = new_min_value
        max_value = new_max_value
        
    np_max_array = np.array(max_value)
    np_min_array = np.array(min_value)

    if len(np_max_array) != 0:
        t = (plannedAmount - np.sum(np_min_array))/ (np.sum(np_max_array) - np.sum(np_min_array))
        result_value = []
        for i in range(0, len(np_max_array)):
            result_value.append(np_min_array[i] + (np_max_array[i] - np_min_array[i]) * t)
        # if any(val  < 0 for val in result_value):
        result_value = [round(i) for i in result_value]
        for i in range(0,len(hierarchy_list)):
            for j in requested_data_values:
                hierarchies = j['hierarchy']
                # print(hierarchies)
                if len(hierarchies) != 1 and hierarchies[-1] == hierarchyOfInterest:
                        j[periodOfInterest] = plannedAmount
                if len(hierarchies) != 1:
                    if hierarchies[-1] == hierarchy_list[i] and hierarchies[-2] == hierarchyOfInterest:
                        j[periodOfInterest] = round(result_value[i],2)
                else:
                    if hierarchies[-1] == hierarchy_list[i]:
                        j[periodOfInterest] = round(result_value[i], 2)
                    if hierarchies[-1] == hierarchyOfInterest:
                         j[periodOfInterest] = plannedAmount

    return requested_data_values


def domain_generator(hierarchyList, periodOfInterest, lower, upper):
    domains = {}
    for idx in range(0, len(hierarchyList)):
        domains[hierarchyList[idx]] = {periodOfInterest: [lower[idx], upper[idx]]}
    return domains

def constraints_arc_generator(constraint_on_column, periodOfInterest, values):
    constraints = {}
    arcs = []
    for idx in range(0, len(constraint_on_column)):
        constraint = constraint_on_column[idx]
        # CHECK only values
        if constraint['operator'] == 'None' and constraint['hierarchyTwo'] == 'None':
            hierarchyConstraintOne = constraint['hierarchyOne']
            arcs.append((hierarchyConstraintOne, hierarchyConstraintOne, periodOfInterest))
            if (hierarchyConstraintOne, hierarchyConstraintOne, periodOfInterest) not in constraints.keys():
                constraints[(hierarchyConstraintOne, hierarchyConstraintOne, periodOfInterest)] = [[constraint['inequality'], constraint['values']]]
            else:
                constraints[(hierarchyConstraintOne, hierarchyConstraintOne, periodOfInterest)].append([constraint['inequality'], constraint['values']])
        else: # CHECK One Way Constraint with Another Variables
            hierarchyConstraintOne = constraint['hierarchyOne']
            hierarchyConstraintTwo = constraint['hierarchyTwo']

            hierarchyConstraintTwoValue = [i[periodOfInterest] for i in values if i['hierarchy'][-1] == hierarchyConstraintTwo and i['hierarchy'][-2] != hierarchyConstraintTwo][0]

            arcs.append((hierarchyConstraintOne, hierarchyConstraintTwo, periodOfInterest))
            if (hierarchyConstraintOne, hierarchyConstraintTwo, periodOfInterest) not in constraints.keys():
                constraints[(hierarchyConstraintOne, hierarchyConstraintTwo, periodOfInterest)] = [[constraint['inequality'], constraint['values'], constraint['operator'], str(hierarchyConstraintTwoValue)]]
            else:
                constraints[(hierarchyConstraintOne, hierarchyConstraintTwo, periodOfInterest)].append([constraint['inequality'], constraint['values'], constraint['operator'], str(hierarchyConstraintTwoValue)])

    return constraints, arcs


def forward_checking(domains, constraints, arcs):
    domains = copy.deepcopy(domains)
    queue = arcs[:] # Add all the arcs to a queue
    consistency = {}
    while queue:
        (x, y, z) = queue.pop(0) # Make x arc consistent with y
        revised, new_domains = revise(x, y, z, domains, constraints) # If the x domain has changed
        domains = new_domains
        if revised:
            if x not in consistency.keys():
                consistency[x] = [True]
            else:
                consistency[x].append(True)
        else:
            if x not in consistency.keys():
                consistency[x] = [False]
            else:
                consistency[x].append(False)
            # domain is empty then consistent false
    return consistency, domains
        
def revise(x, y, z, domains, constraints):
    revised = False
    x_domain = domains[x][z] # Get x domains
    all_constraints = [v for k, v in constraints.items() if k[0] == x and k[1] == y and k[2] == z][0]
    for constraint in all_constraints:
        satisfied = False
        inequality = constraint[0]
        # print(constraint)
        # print(x, y, z)
        if x == y: # cyclic constraint on itself
            if inequality == '<' or inequality == '<=':
                if eval(str(x_domain[1]) + inequality + constraint[1]):
                    satisfied = True
            else:
                if eval(str(x_domain[0]) + inequality + constraint[1]):
                    satisfied = True
        else:
            if inequality == '<' or inequality == '<=':
                if eval(str(x_domain[1]) + inequality + constraint[1] + constraint[2] + constraint[3]):
                    satisfied = True
            else:
                if eval(str(x_domain[0]) + inequality + constraint[1] + constraint[2] + constraint[3]):
                    satisfied = True
        if not satisfied:
            if (x == y and inequality == '<') or (x == y and inequality == '<='):
                valueToEvaluated = constraint[1]
                x_domain[1] = float(valueToEvaluated)
            elif (x == y and inequality == '>') or (x == y and inequality == '>='):
                valueToEvaluated = constraint[1]
                x_domain[0] = float(valueToEvaluated)
            elif (x != y and inequality == '<') or (x != y and inequality == '<='):
                valueToEvaluated = eval(constraint[1] + constraint[2] + constraint[3]) 
                # print(valueToEvaluated)
                # print(x_domain)
                x_domain[1] = valueToEvaluated
                # print(x_domain)
            else:
                valueToEvaluated = eval(constraint[1] + constraint[2] + constraint[3]) 
                x_domain[0] = valueToEvaluated
            domains[x][z] = x_domain
            revised = True
    return revised, domains