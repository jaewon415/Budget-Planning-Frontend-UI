# #!/usr/bin/env python
# #coding: utf-8

import warnings
warnings.filterwarnings("ignore")

from flask import Flask, request
from flask_cors import CORS

import pandas as pd 
import copy
import planning_operator
import json
import export_variables
from datetime import datetime
import csv, glob

import numpy as np
from numpy import power, sqrt, mean, std
import scipy.stats
from scipy.stats import linregress
from collections import defaultdict
import collections, functools, operator
import disaggregation

import re
import mysql.connector

app = Flask(__name__)
CORS(app)

GROUPS = export_variables.GROUPS
HEADER = export_variables.HEADER
COLUMNS_CLONE = export_variables.COLUMNS_CLONE
HISTORY_COLUMN = export_variables.HISTORY_COLUMN
ORGANIZATION_HIERARCHY = export_variables.ORGANIZATION_HIERARCHY

path = '/Sample Data/*.csv'
mysql_passwd = '######'
mysql_dbname = '######'

@app.route('/signIn', methods=['POST'])
def signIn():
    
    data = request.get_json()
    email = data['email']
    password = data['password']
    print(email, password)
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd=mysql_passwd,
        database= mysql_dbname,
        auth_plugin='mysql_native_password'
    )

    cur = mydb.cursor()

    sql = "SELECT * FROM UserAccount WHERE Email = %s AND Password = %s"
    val = (email, password)
    cur.execute(sql, val)
        
    myresult = cur.fetchall()
    columns = cur.column_names
    if len(myresult) != 0:
        print(columns)
        division_idx = columns.index('Division')
        firstName_idx = columns.index('FirstName')
        lastName_idx = columns.index('LastName')
        print(myresult)
        firstName = myresult[0][firstName_idx]
        lastName = myresult[0][lastName_idx]
        name = firstName + ' ' + lastName
        division = myresult[0][division_idx]
        print(name)
        return json.dumps([division, 'Success', name], ensure_ascii=False)
    else:
        return json.dumps([[], 'Fail', []], ensure_ascii=False)


@app.route('/signUp', methods=['POST'])
def signUp():
    
    data = request.get_json()
    # print(data)
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd= mysql_passwd,
        database= mysql_dbname
    )

    firstName = data['firstName']
    lastName = data['lastName']
    email = data['email']
    password = data['password']
    division = data['division']

    if any([x.strip() == '' for x in list(data.values())]):
        print('Error!')
        return json.dumps('Fail', ensure_ascii=False)
    else:
        mycursor = mydb.cursor()
        sql = "INSERT INTO UserAccount (FirstName, LastName, Email, Password, Division) VALUES (%s, %s, %s, %s, %s)"
        val = (firstName, lastName, email, password, division)
        mycursor.execute(sql, val)
        mydb.commit()
        print("record inserted.")
    return json.dumps('Success', ensure_ascii=False)


@app.route('/editViewCreatePlans', methods=['POST'])
def getEditViewCreatePlans():
    division = request.get_json()['division']
    available_department = ORGANIZATION_HIERARCHY[division]
    available_department.sort()
    return json.dumps(available_department, ensure_ascii=False)

@app.route('/getCreateRollupPlans', methods=['POST'])
def getCreateRollupPlans():
    result = []
    division = request.get_json()['division']
    available_department = ORGANIZATION_HIERARCHY[division]
    if len(available_department) > 0:
        for i in available_department:
            div_version_name = planning_operator.getChildrenPropertyInTheHierarchy(i)
            result.extend(div_version_name)
    return json.dumps(result, ensure_ascii=False)

@app.route('/getVersionInfoForHome', methods=['POST'])
def getVersionInfoForHome():
    """
    This function will get request data from the plan page when use clicks on the save as button.
    It will grab form data from the budget graph database and returns them to react server
    The request data format: {'version': 1}
    @return a array with form information 
    """

    firstVersion = float(request.get_json()['firstBudgetVersion'])
    # secondVersion = float(request.get_json()['secondBudgetVersion'])

    first_result, first_columns, first_properties = planning_operator.getVersionBudgetGraph(firstVersion)
    # second_result, second_columns, second_properties = planning_operator.getVersionBudgetGraph(secondVersion)
    plan_base_period = first_properties['plan_base_period']
    # print(first_properties)
    
    findMaxDate = copy.deepcopy(first_result[0])
    del findMaxDate['hierarchy']
    del findMaxDate['id']
    findMaxDate = max(list(findMaxDate.keys()))
    budget_data = budgetOperationFileToList(path)

    operation_data_with_period_df = addBasePeriodColumnToOperationDataset(budget_data, plan_base_period)
    # operation_data_with_period_df = operation_data_with_period_df[operation_data_with_period_df['use_date'] < start_plan_date]
    periods = list(set(operation_data_with_period_df['period']))
    periods.sort() 
    # print(plan_base_period)
    start_plan_date = periods[0]
    end_plan_date = findMaxDate

    if plan_base_period == 'Monthly':
        startToEndPeriod = pd.period_range(start_plan_date, end_plan_date, freq='M')
    elif plan_base_period == 'Quarterly':
        startToEndPeriod = pd.period_range(start_plan_date, end_plan_date, freq='Q')
    else:
        startToEndPeriod = pd.period_range(start_plan_date, end_plan_date, freq='Y')
    startToEndPeriod = list(startToEndPeriod)
    startToEndPeriod = [str(i) for i in startToEndPeriod]

    by_period_and_data = operation_data_with_period_df.groupby('period').apply(lambda x: x.to_json(orient = 'records', force_ascii=False)).reset_index()
    by_period_and_data.columns = ['period', 'item']
    
    if startToEndPeriod[0] in list(by_period_and_data['period']):
        by_period_and_data = by_period_and_data[by_period_and_data['period'] != startToEndPeriod[0]]
    periods = imputeMissingPeriods(by_period_and_data, plan_base_period)
    
    periods.extend(startToEndPeriod)
    periods = list(set([i for i in periods if i <= findMaxDate]))
    periods.sort()
    columns_list = columnGenerator(periods, startToEndPeriod)
    groups = sorted(GROUPS, key=len, reverse=True)

    rows_list = []
    for row in by_period_and_data['item']:
        list_of_elements = eval(row)
        for elements in list_of_elements:
            rows_dict = dict()
            for z in periods:
                if z == elements['period']:
                    rows_dict[z] = 	elements['total_value']
                else:
                    rows_dict[z] = 	0

            rows_dict['category'] = elements['category']
            rows_dict['sub_category'] = elements['sub_category']
            rows_list.append(rows_dict)

    operation_and_superior_df = pd.DataFrame(rows_list)
    operation_and_superior_df = operation_and_superior_df.groupby(['category', 'sub_category'], as_index=False).sum()

    hierarchies = []
    for _, row  in operation_and_superior_df.iterrows():
        groups_copy = copy.deepcopy(GROUPS) # if not deep-copied here, it will keep incrementing
        category, sub_category = row['category'], row['sub_category']
        # print(category, sub_category)
        # print(groups_copy)
        categories = list(filter(lambda group: category in group, groups_copy))
        # if len(categories) > 0:
        categories = categories[0]
        categories.append(sub_category)         
        hierarchies.append(categories)
            # print(hierarchies)
        # else:
        #     hierarchies.append([])
    operation_and_superior_df['hierarchy'] = hierarchies
    # print(operation_and_superior_df)

    # This part will aggregate operation data information along the hierarchy
    for group in groups:
        get_operation_superior_string = group[-1]
        superior_data = operation_and_superior_df[operation_and_superior_df['category'] == get_operation_superior_string]
        superior_data_numbers = superior_data.drop(['category', 'sub_category', 'hierarchy'], axis=1)
        superior_data_numbers = superior_data_numbers.sum(axis = 0)
        superior_data_numbers = superior_data_numbers.to_dict()
        if len(group) > 1:
            superior_data_numbers['category'] = group[-2]
        else:
            superior_data_numbers['category'] = group[-1]
        superior_data_numbers['sub_category'] = get_operation_superior_string
        superior_data_numbers['hierarchy'] = group
        operation_and_superior_df = operation_and_superior_df.append(superior_data_numbers, ignore_index=True)
        
    operation_and_superior_df['id'] = range(0, len(operation_and_superior_df))
    operation_and_superior_dict = operation_and_superior_df.to_dict('records')
    # print(operation_and_superior_dict)
    # Delete sub_category and category before sending it to the website
    for i in operation_and_superior_dict:
        if 'sub_category' in i.keys():
            del i['sub_category']
        if 'category' in i.keys():
            del i['category']
    
    # print(periods)
    # print(startToEndPeriod)

    data_graph_chart_generator = []
    for i in operation_and_superior_dict:
        if len(i['hierarchy']) == 1:
            row = copy.deepcopy(i)
            del row['hierarchy']
            del row['id']
            get_periods = list(row.keys())
            get_periods.sort()
            for j in get_periods:
                each_points = dict()
                each_points['name'] = str(j)
                each_points['actual'] = row[j]
                data_graph_chart_generator.append(each_points)
            break
    # print()
    print(data_graph_chart_generator)
    print(first_result)
    for i in first_result:
        if len(i['hierarchy']) == 1:
            row = copy.deepcopy(i)
            # {'2017': 200000, '2016': 70057000, '2015': 36715600, 
            del row['hierarchy']
            del row['id']
            get_periods = list(row.keys())
            get_periods.sort()
            # print(get_periods)
            for j in get_periods:
                for z in data_graph_chart_generator:
                    if z['name'] == j:
                        z['budget'] = row[j]

    print(data_graph_chart_generator)

    make_cols = []
    sample_col = {'width': 150, 'editable': 0, 'align': 'right', 'headerAlign': 'center', 'type':'number'}
    for i in get_periods:
        each_dict_first = dict()
        each_dict_first['field'] = 'actual_' + str(i)
        each_dict_first['headerName'] = 'actual_' + str(i)
        each_dict_first.update(sample_col)
        make_cols.append(each_dict_first)
        each_dict_second = dict()
        each_dict_second['field'] = 'budget_' + str(i)
        each_dict_second['headerName'] = 'budget_' + str(i)
        each_dict_second.update(sample_col)
        make_cols.append(each_dict_second)
        each_dict_variance = dict()
        each_dict_variance['field'] = 'var_' + str(i)
        each_dict_variance['headerName'] = 'var_' + str(i)
        each_dict_variance.update(sample_col)
        make_cols.append(each_dict_variance)
        sample_col_p = {'width': 100, 'editable': 0, 'align': 'right', 'headerAlign': 'center'}
        each_dict_variance_p = dict()
        each_dict_variance_p['field'] = 'var%_' + str(i)
        each_dict_variance_p['headerName'] = 'var%_' + str(i)
        each_dict_variance_p.update(sample_col_p)
        make_cols.append(each_dict_variance_p)
        
    make_rows = []
    # print(operation_and_superior_dict)
    for i in operation_and_superior_dict:
        each_dict = dict()
        each_dict['id'] = i['id']
        each_dict['hierarchy'] = i['hierarchy']
        # print(i)
        for z in get_periods:
            each_dict['actual_' + str(z)] = i[str(z)]
            # if 'actual_' + str(z) in i.keys():
            #     each_dict['actual_' + str(z)] = i[str(z)]
            # else:
            #     each_dict['actual_' + str(z)] = 0
            checkBoolean = False
            for j in first_result:
                if i['hierarchy'] == j['hierarchy'] and not checkBoolean:
                    each_dict['budget_' + str(z)] = j[str(z)]
                    each_dict['var_' + str(z)] = j[str(z)] - i[str(z)]
                    checkBoolean = True
                    if (i[str(z)]) != 0:
                        each_dict['var%_' + str(z)] = str(round((j[str(z)] - i[str(z)]) * 100 / i[str(z)], 2)) + '%'
                    else:
                        if each_dict['var_' + str(z)] == 0:
                            each_dict['var%_' + str(z)] = str(0.0) + '%'
                        else:
                            each_dict['var%_' + str(z)] = str(100.0) + '%'
                    break
            if not checkBoolean:
                each_dict['budget_' + str(z)] = 0
                each_dict['var_' + str(z)] = 0 - i[str(z)]
                if (i[str(z)]) != 0:
                    each_dict['var%_' + str(z)] = str(round((0 - i[str(z)]) * 100 / i[str(z)], 2)) + '%'
                else:
                    if each_dict['var_' + str(z)] == 0:
                        each_dict['var%_' + str(z)] = str(0.0) + '%'
                    else:
                        each_dict['var%_' + str(z)] = str(100.0) + '%'
        make_rows.append(each_dict)

    # print(data_graph_chart_generator)
    data_bar_chart_generator = []
    # print(data_graph_chart_generator)
    for i in data_graph_chart_generator:
        each_points = dict()
        each_points['name'] = i['name']
        each_points['value'] = (i['budget'] - i['actual'])
        data_bar_chart_generator.append(each_points)

    return json.dumps([data_graph_chart_generator, data_bar_chart_generator, make_cols, make_rows], ensure_ascii=False)


@app.route('/getBudgetPlanPropertyForHome', methods=['POST'])
def getBudgetPlanDataPropertiesForHome():
    """
    This function will generate rows and columns using budget graph properties
    in the budget graph database. The rows and columns will be sent to react server
    to produce datagrid in the plan page
    """
    division = request.get_json()['division']
    properties = planning_operator.getAllBudgetGraphPropertiesFromDatabase()
    columns = COLUMNS_CLONE

    identifier = 1
    rows  = []
    for node in properties:
        node_properties = node['data']
        if division == node_properties['division'] or division in node_properties['view'] or division in node_properties['edit']:
            node_properties['id'] = identifier
            rows.append(node_properties)
            identifier = identifier + 1

    selected_column_field_names = ['plan_name', 'plan_created', 'plan_description']
    filtered_column = filter(lambda x: x['field'] in selected_column_field_names, columns)
    columns = list(filtered_column)
    version_list = []
    for i in rows:
        version = float(i['version'])
        version_list.append(version)

    return json.dumps(version_list, ensure_ascii=False)
    

@app.route('/formula', methods=['POST'])
def getFormula():
    # {'formula': '연구과제추진비2015= 연구과제추진비2016+ 간접비2017'}
    formula = request.get_json()['formula']
    values = request.json['apiRef_values']
    if formula != '':
        leftOperand = formula.split('=')[0].strip()
        rightOperand = formula.split('=')[1].split('+')
        rightOperand = [i.strip() for i in rightOperand]
        r = re.compile("([가-힣a-zA-Z]+)([0-9].*)")
        summation = []
        for val in rightOperand:
            m = r.match(val)
            hierarchy = m.group(1)
            period = m.group(2)
            for rows in values:
                hierarchies = rows['hierarchy']
                if len(hierarchies) != 1:
                    if hierarchies[-1] == hierarchy and hierarchies[-2] != hierarchy:
                        summation.append(rows[period])
                else:
                    if hierarchies[-1] == hierarchy:
                        summation.append(rows[period])

        m1 = r.match(leftOperand)
        hierarchy = m1.group(1)
        period = m1.group(2)
        matching_hierarchies = []
        for rows in values:
            hierarchies = rows['hierarchy']
            if len(hierarchies) != 1:
                if hierarchies[-1] == hierarchy and hierarchies[-2] != hierarchy: 
                    rows[period] = sum(summation)
                    matching_hierarchies.append(hierarchies)
            else:
                if hierarchies[-1] == hierarchy:
                    rows[period] = sum(summation)
                    matching_hierarchies.append(hierarchies)

        requested_data_df = pd.DataFrame(values)
        hierarchy_groups = copy.deepcopy(matching_hierarchies[0])
        hierarchy_groups_len = len(hierarchy_groups)
        period_of_interest = period
        for _ in range(0, hierarchy_groups_len - 1):
            hierarchy_groups.pop()
            superior_category_id = int(requested_data_df[requested_data_df.hierarchy.map(tuple).isin([tuple(hierarchy_groups)])]['id'])
            superior_category_hierarchy = list(requested_data_df[requested_data_df['id'] == superior_category_id]['hierarchy'])[0]
            subordinate_id = list(requested_data_df[requested_data_df['hierarchy'].apply(lambda x: set(superior_category_hierarchy).issubset(x) and len(x) <= len(superior_category_hierarchy) + 1)]['id'])
            subordinate_id.remove(superior_category_id)
            matching_row = requested_data_df.loc[requested_data_df['id'].isin(subordinate_id), period_of_interest]
            matching_row = pd.to_numeric(matching_row)
            requested_data_df.loc[requested_data_df['id']== superior_category_id, period_of_interest] = matching_row.sum() 
        requested_data_dict = requested_data_df.to_dict('records')

        return json.dumps(requested_data_dict, ensure_ascii=False)
    return json.dumps(values, ensure_ascii=False)

@app.route('/planPropertySaveAsForm', methods=['POST'])
def saveAsEdittedForm():
    """
    This function will get request data from the plan page when new form is submitted
    The request data format is as follows: {'form': {'plan_name': 'December Plan', ...}, 'version': 1}
    """
    form = request.get_json()['form']
    if len(form['plan_constraints']) != 0:
        constraints_comma = form['plan_constraints'].split(',')
        constraints_l = []
        for constr in constraints_comma:
            constraint = constr.strip().split(' ')
            each_dict = dict()
            each_dict['hierarchyOne'] = constraint[0].strip()
            each_dict['inequality'] = constraint[1].strip()
            each_dict['values'] = constraint[2].strip()
            each_dict['operators'] = constraint[3].strip()
            each_dict['hierarchyTwo'] = constraint[4].strip()
            constraints_l.append(each_dict)
            # each_dict['hierarchyOne']
        form['plan_constraints'] = str(constraints_l)
    version = float(request.get_json()['version'])
    planning_operator.saveAsOperator(version, form)
    return ('', 204)

@app.route('/saveAs', methods=['POST'])
def saveAsPlan():
    """
    This function will get request data from the plan page when use clicks on the save as button.
    It will grab form data from the budget graph database and returns them to react server
    The request data format: {'version': 1}
    @return a array with form information 
    """
    version = float(request.get_json()['version'])
    result, columns, properties = planning_operator.getVersionBudgetGraph(version)
    plan_base_period = properties['plan_base_period']
    start_plan_date, end_plan_date = properties['start_plan_date'], properties['end_plan_date']
    plan_created = properties['plan_created']
    plan_name, plan_description = properties['plan_name'], properties['plan_description']
    # print(properties['plan_constraints'])
    if len(properties['plan_constraints']) == 0:
        properties['plan_constraints'] = str([{'hierarchyOne': 'None', 'inequality': 'None', 'values': 'None', 'operator': 'None', 'hierarchyTwo': 'None'}])
    plan_constraints = eval(properties['plan_constraints'])
    # print(plan_constraints)
    constraints_string = ''
    for i in range(0, len(plan_constraints)):
        constraint = plan_constraints[i]['hierarchyOne'].strip() + ' ' + \
                     plan_constraints[i]['inequality'].strip() + ' '  + \
                     plan_constraints[i]['values'].strip() + ' '  + \
                     plan_constraints[i]['operator'].strip() + ' '  + \
                     plan_constraints[i]['hierarchyTwo'].strip()
                     
        # constraint = ' '.join(list(plan_constraints[i].values()))
        if 'None' not in constraint:
            constraints_string = constraints_string + constraint
            if i + 1 != len(plan_constraints):
                constraints_string = constraints_string + ', '
    return json.dumps([plan_name, plan_description, plan_created, plan_base_period, start_plan_date, end_plan_date, constraints_string], ensure_ascii=False)

@app.route('/editBudgetPlan', methods=['POST'])
def getEditBudgetPlan():
    """
    This function will send row and column data to react server 
    The request data format: {'version': 1}
    """
    version = float(request.get_json()['version'])
    division = request.get_json()['division']
    result, columns, properties = planning_operator.getVersionBudgetGraph(version)
    # print('here')
    print(properties)
    # print(columns)
    if division in properties['view'] and not division in properties['edit']:
        # print('here')
        for i in columns:
            i['editable'] = 0
            i['cellClassName'] = 'super-app-theme--cell'

    rows_list = []
    for i in result:
        each_dict = dict()
        each = copy.deepcopy(i)
        hierarchy = each['hierarchy']
        ids = each['id']
        del each['hierarchy']
        del each['id']
        each_dict['id'] = ids
        each_dict['hierarchy'] = hierarchy
        each_dict.update(each)
        each_dict['total'] = sum(each.values())
        rows_list.append(each_dict)

    total = {'field': 'total', 'headerName': 'Total', 'cellClassName': 'super-app-theme--cell', 'width': 100, 'editable': 0, 'align': 'right', 'headerAlign': 'center', 'type': 'number'}
    columns.append(total)

    return json.dumps([[columns, rows_list], properties], ensure_ascii=False)

@app.route('/retrieve', methods=['POST'])
def retrievePlan():
    """
    This function will bring back old budget graph from the version database
    and put it back to the budget database. When this process is complete, this function
    will send either success or fail message to react server
    The request data format: {'version': 1}
    """
    version = request.get_json()['version']
    status = planning_operator.retrieveOperator(version)
    if status == 'success':
        return 'success'
    else:
        return 'fail'

@app.route('/getVersionBudgetPlanInformation', methods=['GET'])
def getVersionBudgetHistory():
    """
    This function will make rows for the history data-grid and return
    generated rows and columns to the react server
    """
    properties = planning_operator.getAllBudgetGraphPropertiesFromDatabase()
    version_list = [i['data']['version'] for i in properties]
    # print(version_list)
    versions = planning_operator.getHistoryOperator()
    columns = HISTORY_COLUMN
    rows = []
    identifier = 1

    for row in versions:
        if row['data']['version'] in version_list:
            continue
        # print(row)
        dict_row = dict()
        dict_row['id'] = identifier
        dict_row['version'] = row['data']['version']
        dict_row['plan_name'] = row['data']['plan_name']
        dict_row['userName'] = row['data']['userName']
        dict_row['date_created'] = row['data']['date_created']
        dict_row['plan_base_period'] = row['data']['plan_base_period']
        dict_row['plan_description'] = row['data']['plan_description']
        rows.append(dict_row)
        identifier = identifier + 1
    return json.dumps([columns, rows], ensure_ascii=False)


@app.route('/getBudgetPlanProperty', methods=['POST'])
def getBudgetPlanDataProperties():
    """
    This function will generate rows and columns using budget graph properties
    in the budget graph database. The rows and columns will be sent to react server
    to produce datagrid in the plan page
    """
    division = request.get_json()['division']
    properties = planning_operator.getAllBudgetGraphPropertiesFromDatabase()
    columns = COLUMNS_CLONE
    # print(properties)

    identifier = 1
    rows  = []
    for node in properties:
        node_properties = node['data']
        if (division in node_properties['view']) or (division in node_properties['edit']):
            node_properties['id'] = identifier
            
            if division in node_properties['view'] and division not in node_properties['edit']:
                node_properties['view'] = 'Yes'
            else:
                node_properties['view'] = 'No'

            if division in node_properties['edit']:
                node_properties['edit'] = 'Yes'
                node_properties['view'] = 'Yes'
            else:
                node_properties['edit'] = 'No'
            rows.append(node_properties)
            identifier = identifier + 1

    selected_column_field_names = ['plan_name', 'userName','plan_base_period', 'last_edit','view', 'who_changed','edit', 'plan_created', 'plan_description']
    filtered_column = filter(lambda x: x['field'] in selected_column_field_names, columns)
    columns = list(filtered_column)
    # print(columns)
    for i in rows:
        version = float(i['version'])
        version_len = len(str(version))
        hierarchy_list = []
        for j in range(version_len - 2, -1, -1):
            val = round(version, j)
            if version != int(val):
                hierarchy_list.insert(0, val)
        if len(hierarchy_list) == 0:
            hierarchy_list.append(version)
        i['hierarchy'] = hierarchy_list

    selected_row_key_names = ['hierarchy', 'userName','plan_name', 'plan_base_period', 'last_edit', 'who_changed','view', 'edit', 'plan_created', 'plan_description', 'id']
    filtered_rows = [dict((k, i[k]) for k in selected_row_key_names if k in i) for i in rows]
    rows = filtered_rows
    # print(rows)
    return json.dumps([columns, rows], ensure_ascii=False)

@app.route('/cloneBudgetPlan', methods=['POST'])
def cloneBudgetPlan():
    """
    This function will clone budget plan from the budget database 
    The request data format: {'version': 1}
    """
    version = float(request.get_json()['version'])
    # division = request.get_json()['division']
    result, columns, properties = planning_operator.getVersionBudgetGraph(version)
    # print(properties)
    plan_base_period = properties['plan_base_period']
    start_plan_date = properties['start_plan_date']
    end_plan_date = properties['end_plan_date']
    plan_created = properties['plan_created']
    now  = datetime.now()
    plan_created = now.strftime("%-m/%-d/%Y, %-I:%M:%S %p")
    plan_name = properties['plan_name']
    plan_description = properties['plan_description']
    plan_constraints = properties['plan_constraints']     
    division = properties['division']
    budgetNameEdit = properties['edit']
    budgetNameView = properties['view']
    
    userName = request.get_json()['userName']
    userName = userName
    who_changed = userName
    last_edit = now.strftime("%-m/%-d/%Y, %-I:%M:%S %p")


    planning_operator.cloneBudgetOperator(result, plan_name, plan_created, plan_base_period, start_plan_date, end_plan_date, plan_description, plan_constraints, version, division, budgetNameEdit, budgetNameView, userName, last_edit, who_changed)
    
    properties = planning_operator.getAllBudgetGraphPropertiesFromDatabase()
    columns = COLUMNS_CLONE

    identifier = 1
    rows  = []
    for node in properties:
        node_properties = node['data']
        if (division in node_properties['view']) or (division in node_properties['edit']):
            node_properties['id'] = identifier
            
            if division in node_properties['view'] and division not in node_properties['edit']:
                node_properties['view'] = 'Yes'
            else:
                node_properties['view'] = 'No'

            if division in node_properties['edit']:
                node_properties['edit'] = 'Yes'
                node_properties['view'] = 'Yes'
            else:
                node_properties['edit'] = 'No'
            rows.append(node_properties)
            identifier = identifier + 1

    selected_column_field_names = ['plan_name', 'userName','plan_base_period', 'last_edit','view', 'who_changed','edit', 'plan_created', 'plan_description']
    filtered_column = filter(lambda x: x['field'] in selected_column_field_names, columns)
    columns = list(filtered_column)

    versions_list = [float(i['version']) for i in rows]
    for i in rows:
        version = float(i['version'])
        version_len = len(str(version))
        hierarchy_list = []
        for j in range(version_len - 2, -1, -1):
            val = round(version, j)
            if val in versions_list and version >= val:
                if version != int(val):
                    hierarchy_list.insert(0, val)
        if len(hierarchy_list) == 0:
            hierarchy_list.append(version)
        i['hierarchy'] = hierarchy_list
    # print(rows)
    selected_row_key_names = ['hierarchy', 'userName','plan_name', 'plan_base_period', 'last_edit', 'who_changed','view', 'edit', 'plan_created', 'plan_description', 'id']
    filtered_rows = [dict((k, i[k]) for k in selected_row_key_names if k in i) for i in rows]
    rows = filtered_rows
    
    return json.dumps([columns, rows], ensure_ascii=False)

@app.route('/delete', methods = ['POST'])
def deleteBudgetPlanFromDatabase():
    """
    This function will delete budget plan from the budget database 
    The request data format: {'version': 1}
    """
    version_to_delete = float(request.get_json()['version'])
    division = request.get_json()['division']
    planning_operator.deleteOperator(version_to_delete)

    properties = planning_operator.getAllBudgetGraphPropertiesFromDatabase()
    columns = COLUMNS_CLONE
    # print(properties)

    identifier = 1
    rows  = []
    for node in properties:
        node_properties = node['data']
        if (division in node_properties['view']) or (division in node_properties['edit']):
            node_properties['id'] = identifier
            
            if division in node_properties['view'] and division not in node_properties['edit']:
                node_properties['view'] = 'Yes'
            else:
                node_properties['view'] = 'No'

            if division in node_properties['edit']:
                node_properties['edit'] = 'Yes'
                node_properties['view'] = 'Yes'
            else:
                node_properties['edit'] = 'No'
            rows.append(node_properties)
            identifier = identifier + 1

    selected_column_field_names = ['plan_name', 'userName','plan_base_period', 'last_edit','view', 'who_changed','edit', 'plan_created', 'plan_description']
    filtered_column = filter(lambda x: x['field'] in selected_column_field_names, columns)
    columns = list(filtered_column)

    for i in rows:
        version = float(i['version'])
        # print(version)
        if str(version) != str(version_to_delete):
            # print('found')
            version_len = len(str(version))
            hierarchy_list = []
            for j in range(version_len - 2, -1, -1):
                val = round(version, j)
                if val != version_to_delete:
                    if version != int(val):
                        hierarchy_list.insert(0, val)
            if len(hierarchy_list) == 0:
                hierarchy_list.append(version)
            i['hierarchy'] = hierarchy_list

    selected_row_key_names = ['hierarchy', 'userName','plan_name', 'plan_base_period', 'last_edit', 'who_changed','view', 'edit', 'plan_created', 'plan_description', 'id']
    filtered_rows = [dict((k, i[k]) for k in selected_row_key_names if k in i) for i in rows]
    rows = filtered_rows
    # print(rows)
    return json.dumps([columns, rows], ensure_ascii=False)

@app.route('/mergeBudgetPlans', methods = ['POST'])
def mergeTwoBudgetPlans():
    """
    This function will merge two budget plans together
    The request data format: {'firstVersion': 1, 'secondVersion':1.1}
    """
    data = request.get_json()
    mergeType = data['mergeForm']['mergeType']
    firstVersion = float(data['firstVersion'])
    secondVersion = float(data['secondVersion'])
    first_result, first_columns, first_properties = planning_operator.getVersionBudgetGraph(firstVersion)
    second_result, second_columns, second_properties = planning_operator.getVersionBudgetGraph(secondVersion)

    getFirstColumns = []
    for i in first_columns:
        if i['editable'] == 1:
            getFirstColumns.append(i['field'])
    count = 0 
    new_list_of_dict_result = []

    if mergeType == 'budget':
        for f_row in first_result:
            f_data = copy.deepcopy(f_row)
            hierarchy = f_data['hierarchy']
            for s_row in second_result:
                s_data = copy.deepcopy(s_row)
                if s_data['hierarchy'] == hierarchy:
                    s_data.update({k: v for k, v in f_data.items() if v != 0})
                    s_data['id'] = count
                    new_list_of_dict_result.append(s_data)
                    break
            count = count + 1
        
        plan_base_period = first_properties['plan_base_period']
        start_plan_date = first_properties['start_plan_date']
        end_plan_date = first_properties['end_plan_date']
        plan_created = first_properties['plan_created']
        now  = datetime.now()
        plan_created = now.strftime("%-m/%-d/%Y, %-I:%M:%S %p")
        plan_name = first_properties['plan_name']
        plan_description = first_properties['plan_description']
        plan_constraints = first_properties['plan_constraints']
        division = first_properties['division']
        budgetNameEdit = first_properties['edit']
        budgetNameView = first_properties['view']
        
        last_edit = plan_created
        userName = first_properties['userName']
        who_changed = userName

    elif mergeType == 'second':
        for s_row in second_result:
            s_data = copy.deepcopy(s_row)
            hierarchy = s_data['hierarchy']
            for f_row in first_result:
                f_data = copy.deepcopy(f_row)
                if f_data['hierarchy'] == hierarchy:
                    f_data.update({k: v for k, v in s_data.items() if v != 0})
                    f_data['id'] = count
                    new_list_of_dict_result.append(f_data)
                    break
            count = count + 1

        plan_base_period = second_properties['plan_base_period']
        start_plan_date = second_properties['start_plan_date']
        end_plan_date = second_properties['end_plan_date']
        plan_created = second_properties['plan_created']
        now  = datetime.now()
        plan_created = now.strftime("%-m/%-d/%Y, %-I:%M:%S %p")
        plan_name = second_properties['plan_name']
        plan_description = second_properties['plan_description']
        plan_constraints = second_properties['plan_constraints']
        division = second_properties['division']
        budgetNameEdit = second_properties['edit']
        budgetNameView = second_properties['view']

        last_edit = plan_created
        userName = second_properties['userName']
        who_changed = userName

    elif mergeType == 'average':
        for f_row in first_result:
            f_data = copy.deepcopy(f_row)
            hierarchy = f_data['hierarchy']
            del f_data['hierarchy']
            del f_data['id']
            for s_row in second_result:
                s_data = copy.deepcopy(s_row)
                if s_data['hierarchy'] == hierarchy:
                    del s_data['hierarchy']
                    del s_data['id']
                    for j in f_data:
                        if j in getFirstColumns:
                            if f_data[j] != 0 and s_data[j] != 0:
                                f_data[j] = (s_data[j] + f_data[j]) / 2.0
                            elif f_data[j] != 0 and s_data[j] == 0:
                                f_data[j] = f_data[j]
                            else:
                                f_data[j] = s_data[j]
                        else:
                            f_data[j] = f_data[j]
                    f_data['hierarchy'] = hierarchy
                    f_data['id'] = count
                    new_list_of_dict_result.append(f_data)
                    break
            count = count + 1
        plan_base_period = first_properties['plan_base_period']
        start_plan_date = first_properties['start_plan_date']
        end_plan_date = first_properties['end_plan_date']
        plan_created = first_properties['plan_created']
        now  = datetime.now()
        plan_created = now.strftime("%-m/%-d/%Y, %-I:%M:%S %p")
        plan_name = first_properties['plan_name']
        plan_description = first_properties['plan_description']
        plan_constraints = first_properties['plan_constraints']
        division = first_properties['division']
        budgetNameEdit = first_properties['edit']
        budgetNameView = first_properties['view']

        last_edit = plan_created
        userName = first_properties['userName']
        who_changed = userName
    else:
        for f_row in first_result:
            f_data = copy.deepcopy(f_row)
            hierarchy = f_data['hierarchy']
            del f_data['hierarchy']
            del f_data['id']
            for s_row in second_result:
                s_data = copy.deepcopy(s_row)
                if s_data['hierarchy'] == hierarchy:
                    del s_data['hierarchy']
                    del s_data['id']
                    for j in f_data:
                        if j in getFirstColumns:
                            if f_data[j] != 0 and s_data[j] != 0:
                                f_data[j] = 0
                            elif f_data[j] != 0 and s_data[j] == 0:
                                f_data[j] = f_data[j]
                            else:
                                f_data[j] = s_data[j]
                        else:
                            f_data[j] = f_data[j]
                    f_data['hierarchy'] = hierarchy
                    f_data['id'] = count
                    new_list_of_dict_result.append(f_data)
                    break
            count = count + 1
        plan_base_period = first_properties['plan_base_period']
        start_plan_date = first_properties['start_plan_date']
        end_plan_date = first_properties['end_plan_date']
        plan_created = first_properties['plan_created']
        now  = datetime.now()
        plan_created = now.strftime("%-m/%-d/%Y, %-I:%M:%S %p")
        plan_name = first_properties['plan_name']
        plan_description = first_properties['plan_description']
        plan_constraints = first_properties['plan_constraints']
        division = first_properties['division']
        budgetNameEdit = first_properties['edit']
        budgetNameView = first_properties['view']

        last_edit = plan_created
        userName = first_properties['userName']
        who_changed = userName

    # print(new_list_of_dict_result)
    version = planning_operator.commitOperator(new_list_of_dict_result, plan_name, plan_created, plan_base_period, start_plan_date, end_plan_date, plan_description, plan_constraints, division,budgetNameEdit, budgetNameView, userName, last_edit, who_changed)
    # print(status)
    planning_operator.commitOperatorForMerge(version, firstVersion, secondVersion)
    return ('', 204)

@app.route('/create', methods = ['POST'])
def createInitialBudgetPlan():
    """
    This function creates new budget plan
    """

    data = request.get_json()

    
    start_plan_date = '2016-05-01'
    end_plan_date = '2016-05-30'

    base_period = data['combinedForm']['plan_base_period']
    plan_date = data['combinedForm']['plan_date']
    # print(data['combinedForm'])
    
    plan_constraints = data['combinedForm']['plan_constraints']

    plan_date[0] = '2019-08-03'
    plan_date[1] = '2019-09-03'
    budgetNameRollup = data['budgetNameRollup']
    if len(budgetNameRollup) > 0:
        l_result = []
        l_columns = []
        d_result = defaultdict()
        for budget in budgetNameRollup:
            leftOfParantheses = budget.split('(')
            division = leftOfParantheses[0]
            rightOfParantheses = leftOfParantheses[1].split('):')
            version = float(rightOfParantheses[0].split(',')[0])
            planning_period = rightOfParantheses[0].split(',')[1]
            plan_name = rightOfParantheses[1]

            result, columns, properties = planning_operator.getVersionBudgetGraph(version)
            l_result.extend(result)
            l_columns.extend(columns)
        
        for i in l_result:
            getHierarchy = i['hierarchy']
            deep_i = copy.deepcopy(i)
            del deep_i['id']
            del deep_i['hierarchy']
            if str(getHierarchy) not in d_result:
                d_result[str(getHierarchy)] = deep_i
            else:
                for j in deep_i:
                    if j in d_result[str(getHierarchy)]:
                        d_result[str(getHierarchy)][j] = d_result[str(getHierarchy)][j] + deep_i[j]
                    else:
                        d_result[str(getHierarchy)][j] = deep_i[j]
        
        d_result = dict(d_result)
        count = 0
        output = []
        for i, j in d_result.items():
            j['id'] = count
            j['hierarchy'] = eval(i)
            output.append(j)
            count = count + 1
        # print(output)

        first_result = copy.deepcopy(output[0])
        del first_result['id']
        del first_result['hierarchy']
        periods = list(first_result.keys())
        periods.sort()
        # print(periods)

        if base_period == 'Monthly':
            startToEndPeriod = pd.period_range(start_plan_date, end_plan_date, freq='M')
        elif base_period == 'Quarterly':
            startToEndPeriod = pd.period_range(start_plan_date, end_plan_date, freq='Q')
        else:
            startToEndPeriod = pd.period_range(start_plan_date, end_plan_date, freq='Y')
        startToEndPeriod = list(startToEndPeriod)
        startToEndPeriod = [str(i) for i in startToEndPeriod]

        columns_list = columnGenerator(periods, startToEndPeriod)

        rows_list = []
        for i in output:
            each_dict = dict()
            each = copy.deepcopy(i)
            hierarchy = each['hierarchy']
            ids = each['id']
            del each['hierarchy']
            del each['id']
            each_dict['id'] = ids
            each_dict['hierarchy'] = hierarchy
            each_dict.update(each)
            each_dict['total'] = sum(each.values())
            rows_list.append(each_dict)

        return json.dumps([columns_list, rows_list], ensure_ascii=False)

    budget_data = budgetOperationFileToList(path)

    operation_data_with_period_df = addBasePeriodColumnToOperationDataset(budget_data, base_period)
    operation_data_with_period_df = operation_data_with_period_df[operation_data_with_period_df['use_date'] < start_plan_date]

    # print(start_plan_date)
    # print(end_plan_date)
    if base_period == 'Monthly':
        startToEndPeriod = pd.period_range(start_plan_date, end_plan_date, freq='M')
    elif base_period == 'Quarterly':
        startToEndPeriod = pd.period_range(start_plan_date, end_plan_date, freq='Q')
    else:
        startToEndPeriod = pd.period_range(start_plan_date, end_plan_date, freq='Y')
    startToEndPeriod = list(startToEndPeriod)
    startToEndPeriod = [str(i) for i in startToEndPeriod]

    # print(startToEndPeriod)
    print(operation_data_with_period_df)
    by_period_and_data = operation_data_with_period_df.groupby('period').apply(lambda x: x.to_json(orient = 'records', force_ascii=False)).reset_index()
    by_period_and_data.columns = ['period', 'item']
    
    if startToEndPeriod[0] in list(by_period_and_data['period']):
        by_period_and_data = by_period_and_data[by_period_and_data['period'] != startToEndPeriod[0]]
    periods = imputeMissingPeriods(by_period_and_data, base_period)
    
    # firstOfStart = startToEndPeriod[0]
    # if firstOfStart > str(periods[len(periods) - 1]):
    #     if base_period == 'Monthly':
    #         fillPeriodGap = pd.period_range(periods[len(periods) - 1], firstOfStart, freq='M')
    #     elif base_period == 'Quarterly':
    #         fillPeriodGap = pd.period_range(periods[len(periods) - 1], firstOfStart, freq='Q')
    #     else:
    #         fillPeriodGap = pd.period_range(periods[len(periods) - 1], firstOfStart, freq='Y')
    #     fillPeriodGap = list(fillPeriodGap)
    #     fillPeriodGap = [str(i) for i in fillPeriodGap]
    #     periods.extend(fillPeriodGap)
    
    periods.extend(startToEndPeriod)
    periods.sort()
    columns_list = columnGenerator(periods, startToEndPeriod)
    # print(periods)
    # print(startToEndPeriod)
    groups = sorted(GROUPS, key=len, reverse=True)

    rows_list = []
    for row in by_period_and_data['item']:
        list_of_elements = eval(row)
        for elements in list_of_elements:
            rows_dict = dict()
            for z in periods:
                if z == elements['period']:
                    rows_dict[z] = 	elements['total_value']
                else:
                    rows_dict[z] = 	0

            rows_dict['category'] = elements['category']
            rows_dict['sub_category'] = elements['sub_category']
            rows_list.append(rows_dict)

    operation_and_superior_df = pd.DataFrame(rows_list)
    operation_and_superior_df = operation_and_superior_df.groupby(['category', 'sub_category'], as_index=False).sum()
    # print(operation_and_superior_df)
    hierarchies = []
    for _, row  in operation_and_superior_df.iterrows():
        groups_copy = copy.deepcopy(GROUPS) # if not deep-copied here, it will keep incrementing
        category, sub_category = row['category'], row['sub_category']
        print(category, sub_category)
        categories = list(filter(lambda group: category in group, groups_copy))[0]
        categories.append(sub_category)         
        hierarchies.append(categories)
    operation_and_superior_df['hierarchy'] = hierarchies

    # This part will aggregate operation data information along the hierarchy
    for group in groups:
        get_operation_superior_string = group[-1]
        superior_data = operation_and_superior_df[operation_and_superior_df['category'] == get_operation_superior_string]
        superior_data_numbers = superior_data.drop(['category', 'sub_category', 'hierarchy'], axis=1)
        superior_data_numbers = superior_data_numbers.sum(axis = 0)
        superior_data_numbers = superior_data_numbers.to_dict()
        if len(group) > 1:
            superior_data_numbers['category'] = group[-2]
        else:
            superior_data_numbers['category'] = group[-1]
        superior_data_numbers['sub_category'] = get_operation_superior_string
        superior_data_numbers['hierarchy'] = group
        operation_and_superior_df = operation_and_superior_df.append(superior_data_numbers, ignore_index=True)
        
    operation_and_superior_df['id'] = range(0, len(operation_and_superior_df))
    operation_and_superior_dict = operation_and_superior_df.to_dict('records')
    
    # Delete sub_category and category before sending it to the website
    for i in operation_and_superior_dict:
        if 'sub_category' in i.keys():
            del i['sub_category']
        if 'category' in i.keys():
            del i['category']
    
    rows_list = []
    for i in operation_and_superior_dict:
        each_dict = dict()
        each = copy.deepcopy(i)
        hierarchy = each['hierarchy']
        ids = each['id']
        del each['hierarchy']
        del each['id']
        each_dict['id'] = ids
        each_dict['hierarchy'] = hierarchy
        each_dict.update(each)
        each_dict['total'] = sum(each.values())
        rows_list.append(each_dict)
    # print(operation_and_superior_dict)

    # print(operation_and_superior_dict)
    return json.dumps([columns_list, rows_list], ensure_ascii=False)

@app.route('/commitEdittedBudget', methods = ['POST'])
def commitEdittedBudgetPlan():
    """
    This function will commit editted budget plan 
    """
    data = request.get_json()['state']
    version = data['viewVersion']
    version = float(version[len(version) - 1])
    # print(data)
    who_changed = data['userName']
    
    ###
    form_data = data['combinedForm']
    plan_constraint = form_data['plan_constraints']
    data_grid = copy.deepcopy(data['apiRef_values'])
    for i in data_grid:
        del i['total']

    if isinstance(plan_constraint, str):
        plan_constraint = eval(plan_constraint)

    for constraint in plan_constraint:
        hierarchyOne = constraint['hierarchyOne']
        hierarchyTwo = constraint['hierarchyTwo']
        inequality = constraint['inequality']
        values = constraint['values']
        operators = constraint['operator']
        
        constraint_values = list(constraint.values())
        if any(x == 'None' for x in constraint_values):
            break
        else:
            temp = dict()
            for row in data_grid:
                row_copy = copy.deepcopy(row)
                hierarchy = row_copy['hierarchy'][-1]
                del row_copy['hierarchy']
                del row_copy['id']
                if hierarchy == hierarchyOne:
                    total = sum(list(row_copy.values()))
                    temp['hierarchyOne'] = total
                if hierarchy == hierarchyTwo:
                    total = sum(list(row_copy.values()))
                    temp['hierarchyTwo'] = total
            if len(list(temp.keys())) > 1:
                evaluateBool = str(temp['hierarchyOne']) + inequality + str(temp['hierarchyTwo']) + operators + values  
                if not eval(evaluateBool):
                    return json.dumps(['fail', constraint], ensure_ascii=False)
    ###

    result, columns, properties = planning_operator.getVersionBudgetGraph(version)
    # print(properties)
    plan_base_period = properties['plan_base_period']
    start_plan_date = properties['start_plan_date']
    end_plan_date = properties['end_plan_date']
    plan_created = properties['plan_created']
    plan_name = properties['plan_name']
    plan_description = properties['plan_description']
    plan_constraints = properties['plan_constraints']
    division = properties['division']
    budgetNameEdit = properties['edit']
    budgetNameView = properties['view']
    userName = properties['userName']
    # last_edit = properties['last_edit']
    last_edit = datetime.now()
    last_edit = last_edit.strftime("%-m/%-d/%Y, %-I:%M:%S %p")

    planning_operator.deleteOperator(version)
    for i in data['apiRef_values']:
        del i['total']
    status = planning_operator.commitEdittedBudgetPlanOperator(data['apiRef_values'], plan_name, plan_created, plan_base_period, start_plan_date, end_plan_date, plan_description, plan_constraints, version, division, budgetNameEdit, budgetNameView, userName, last_edit, who_changed)
    return ('', 204)

@app.route('/commit', methods=['POST'])
def commitWorkingBudget():
    """
    This function will get the saved budget from the frontend
    and produce a corresponding graph on the neo4j graph database,
    both on budge and version side. 
    """
    data = request.get_json()['state']
    form_data = data['combinedForm']
    plan_name = form_data['plan_name']
    plan_created = form_data['plan_created']
    plan_base_period = form_data['plan_base_period']
    
    form_data['plan_date'][0] = '2018-08-03'
    form_data['plan_date'][1] = '2018-09-03'
    start_plan_date = form_data['plan_date'][0]
    end_plan_date = form_data['plan_date'][1]
    # start_plan_date = datetime.strptime(form_data['plan_date'][0][:10], '%Y-%m-%d').strftime('%Y/%m/%d')
    # end_plan_date = datetime.strptime(form_data['plan_date'][1][:10], '%Y-%m-%d').strftime('%Y/%m/%d')
    
    plan_description = form_data['plan_description']
    # plan_constraints = form_data['plan_constraints']
    division = data['division']

    userName = data['userName']
    last_edit = plan_created
    who_changed = userName
    # last_edit = datetime.now()
    # last_edit = last_edit.strftime("%-m/%-d/%Y, %-I:%M:%S %p")

    budgetNameEdit = data['budgetNameEdit']
    budgetNameEdit.append(division)
    budgetNameView = data['budgetNameView']
    budgetNameView.append(division)
    
    plan_constraint = form_data['plan_constraints']
    # print(plan_constraint)
    data_grid = copy.deepcopy(data['apiRef_values'])
    for i in data_grid:
        del i['total']
    # print(plan_constraint)
    if isinstance(plan_constraint, str):
        plan_constraint = eval(plan_constraint)

    for constraint in plan_constraint:
        # print(constraint)
        hierarchyOne = constraint['hierarchyOne']
        hierarchyTwo = constraint['hierarchyTwo']
        inequality = constraint['inequality']
        values = constraint['values']
        operators = constraint['operator']
        # print(constraint)
        constraint_values = list(constraint.values())
        if any(x == 'None' for x in constraint_values):
            break
        else:
            temp = dict()
            for row in data_grid:
                row_copy = copy.deepcopy(row)
                hierarchy = row_copy['hierarchy'][-1]
                del row_copy['hierarchy']
                del row_copy['id']
                if hierarchy == hierarchyOne:
                    total = sum(list(row_copy.values()))
                    temp['hierarchyOne'] = total
                if hierarchy == hierarchyTwo:
                    total = sum(list(row_copy.values()))
                    temp['hierarchyTwo'] = total
            if len(list(temp.keys())) > 1:
                print('hello')
                # [{'hierarchyOne': '간접비', 'inequality': '<=', 'values': '0.1', 'operator': '*', 'hierarchyTwo': '직접비'}, {'hierarchyOne': '시설장비비', 'inequality': '<=', 'values': '0.05', 'hierarchyTwo': '직접비', 'operator': '*'}]
                evaluateBool = str(temp['hierarchyOne']) +  " " + inequality +  " " + str(temp['hierarchyTwo']) +  " " + str(operators) +  "  " + str(values)
                if not eval(evaluateBool):
                    return json.dumps(['fail', constraint], ensure_ascii=False)
    
    for i in data['apiRef_values']:
        del i['total']
    planning_operator.commitOperator(data['apiRef_values'], plan_name, plan_created, plan_base_period, start_plan_date, end_plan_date, plan_description, plan_constraint, division, budgetNameEdit, budgetNameView, userName, last_edit, who_changed)
    return('', 204)

@app.route("/disaggregate", methods=["POST"])
def planDisaggregate():
    requested_data_form = request.get_json()['form']
    individual_constraints = request.get_json()['constraints']
    requested_data_values = request.get_json()['apiRef_values']
    referential_period = requested_data_form['referential']
    constraint_form = request.get_json()['combinedForm']

    locked_item = requested_data_form['lock']

    periodOfInterest = requested_data_form['periodOfInterest']
    referential_period = requested_data_form['referential']
    hierarchyOfInterest = requested_data_form['hierarchyOfInterest']
    plannedAmount = float(requested_data_form['amount'])
    disaggregationType = requested_data_form['disaggregateType']

    if isinstance(constraint_form['plan_constraints'], str):
        plan_constraints = eval(constraint_form['plan_constraints'])
    else:
        plan_constraints = constraint_form['plan_constraints']

    if disaggregationType == 'Referential':
        requested_data_values = disaggregation.referential(requested_data_values, hierarchyOfInterest, periodOfInterest, plannedAmount, referential_period)
    elif disaggregationType == 'Proportional':
        requested_data_values = disaggregation.proportional(requested_data_values, hierarchyOfInterest, periodOfInterest, plannedAmount)
    elif disaggregationType == 'Average':
        requested_data_values = disaggregation.average(requested_data_values, hierarchyOfInterest, periodOfInterest, plannedAmount)
    else:
        requested_data_values = disaggregation.interval(requested_data_values, hierarchyOfInterest, periodOfInterest, plannedAmount, plan_constraints, individual_constraints, locked_item)
    
    rows_list = []
    for i in requested_data_values:
        each_dict = dict()
        each = copy.deepcopy(i)
        hierarchy = each['hierarchy']
        ids = each['id']
        del each['hierarchy']
        del each['id']
        del each['total']
        each_dict['id'] = ids
        each_dict['hierarchy'] = hierarchy
        each_dict.update(each)
        each_dict['total'] = sum(each.values())
        rows_list.append(each_dict)
    return json.dumps(rows_list, ensure_ascii=False)

@app.route('/reaggregate',  methods = ['POST'])
def aggregateAlongTheHierarchy():
    """
    This function will aggregate values along the hierarchy
    editRowsModel': {'14': {'2016Q3': {'value': 50}}}
    editRowData': {'2016Q3': {'value': 50}}
    """
    requested_data = request.get_json()['state']
    editted_rows_model = requested_data['editRowsModel']
    data = requested_data['apiRef_values']


    matching_id = int(list(editted_rows_model.keys())[0])
    period_of_interest = str(list(editted_rows_model[str(matching_id)].keys())[0])

    requested_data_df = pd.DataFrame(data)
    hierarchy_groups = copy.deepcopy(list(requested_data_df[requested_data_df['id'] == matching_id]['hierarchy'])[0])
    hierarchy_groups_len = len(hierarchy_groups)
    for _ in range(0, hierarchy_groups_len - 1):
        hierarchy_groups.pop()
        superior_category_id = int(requested_data_df[requested_data_df.hierarchy.map(tuple).isin([tuple(hierarchy_groups)])]['id'])
        superior_category_hierarchy = list(requested_data_df[requested_data_df['id'] == superior_category_id]['hierarchy'])[0]
        subordinate_id = list(requested_data_df[requested_data_df['hierarchy'].apply(lambda x: set(superior_category_hierarchy).issubset(x) and len(x) <= len(superior_category_hierarchy) + 1)]['id'])
        subordinate_id.remove(superior_category_id)
        matching_row = requested_data_df.loc[requested_data_df['id'].isin(subordinate_id), period_of_interest]
        matching_row = pd.to_numeric(matching_row)
        requested_data_df.loc[requested_data_df['id']== superior_category_id, period_of_interest] = matching_row.sum() 
    requested_data_dict = requested_data_df.to_dict('records')
    # print(requested_data_dict)

    rows_list = []
    for i in requested_data_dict:
        each_dict = dict()
        each = copy.deepcopy(i)
        hierarchy = each['hierarchy']
        ids = each['id']
        del each['hierarchy']
        del each['id']
        del each['total']
        each_dict['id'] = ids
        each_dict['hierarchy'] = hierarchy
        each_dict.update(each)
        each_dict['total'] = sum(each.values())
        rows_list.append(each_dict)

    return json.dumps(rows_list, ensure_ascii=False)

def imputeMissingPeriods(data, base_period):
    """
    This function will fill in the gap in between periods
    @param data: pandas dataframe
    @param base_period: base period string from the form
    """
    if base_period == 'Monthly':
        periods = pd.period_range(min(data['period']), max(data['period']), freq='M')
    elif base_period == 'Quarterly':
        periods = pd.period_range(min(data['period']), max(data['period']), freq='Q')
    else:
        periods = pd.period_range(min(data['period']), max(data['period']), freq='Y')
    return list(periods.astype(str))


def addBasePeriodColumnToOperationDataset(budget_data, base_period):
    """
    This function will add period column to the operation dataset
    @param budget_data: list of list containing budget dataset
    @base_period: string indicating base period from the form
    """
    operation_df = pd.DataFrame(budget_data, columns = HEADER)
    operation_df['use_date'] = pd.to_datetime(operation_df['use_date'])
    if base_period == 'Monthly':
        operation_df['period'] = operation_df['use_date'].dt.to_period('M')
    elif base_period == 'Quarterly':
        operation_df['period'] = operation_df['use_date'].dt.to_period('Q')
    else:
        operation_df['period'] = operation_df['use_date'].dt.to_period('Y')

    operation_df[['use_date']] = operation_df[['use_date']].astype(str)
    operation_df[['period']] = operation_df[['period']].astype(str)
    # print(operation_df['total_value'])
    operation_df['total_value'] = operation_df['total_value'].str.replace(',', '').astype(int)
    operation_df['supply_value'] = operation_df['supply_value'].str.replace(',', '').astype(int)
    operation_df['vat'] = operation_df['vat'].str.replace(',', '').astype(int)

    return operation_df

def columnGenerator(periods, startToEndPeriod, width = 100, 
                    align = 'right', headerAlign = 'center', 
                    datatype = 'number'):
    """
    This function will generate columns for the datagrid.
    @param periods List[str]: list of periods that will represent each column
    @param startToEndPeriod: list of periods that can be editted
    """
    columns_list = []
    for row in periods:
        columns_dict = dict()
        columns_dict['field'] = row
        columns_dict['headerName'] = row
        columns_dict['width'] = width
        if row not in startToEndPeriod:
            columns_dict['editable'] = 0
            columns_dict['cellClassName'] = 'super-app-theme--cell'
        else:
            columns_dict['editable'] = 1
        columns_dict['align'] = align
        columns_dict['headerAlign'] = headerAlign
        columns_dict['type'] = datatype
        columns_list.append(columns_dict)
    
    total = {'field': 'total', 'headerName': 'Total', 'cellClassName': 'super-app-theme--cell', 'width': 100, 'editable': 0, 'align': 'right', 'headerAlign': 'center', 'type': 'number'}
    columns_list.append(total)
    # print(columns_list)
    return columns_list

def budgetOperationFileToList(path):
	"""
	This function takes operation level budget (detail budget usage) data
	and returns a list in which each index of the list represents each file. The research
	files could be 간접비, 인건비, 연구과제추진비, 연구활동비, 연구시설장비비 in csv format.
	@param path: path to budget csv folder
	@return budget_files_into_list: list of list including each budget3 file 
	"""
	budgetFilesInList = []
	filePaths = glob.glob(path) # list of research file paths 
	for file in filePaths:
		csvreader = csv.reader(open(file))
		next(csvreader) # skip header
		rows = [row for row in csvreader] # budget3 file instances
		budgetFilesInList.extend(rows)
	return budgetFilesInList

if __name__ == "__main__":
    app.run(debug=True)

