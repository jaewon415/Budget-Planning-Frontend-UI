# !/usr/bin/env python
# coding: utf-8

from typing import List
import pandas as pd
import copy
import neo4j_python
import decimal
from datetime import datetime
import time
##############################
####  Common 
##############################

neo4j_passwd = '#####'
bolt_address = '#####'

def getChildrenPropertyInTheHierarchy(division):
    budget_graph = neo4j_python.Graph(bolt_address, "neo4j", neo4j_passwd)
    x = budget_graph.getChildrenPropertyInTheOrganizationHierarchy(division)
    result = []
    for i in x:
        plan_name = i['a']['plan_name']
        plan_version = i['a']['version']
        plan_base_period = i['a']['plan_base_period']
        output =  division + '(' + str(plan_version) +',' + plan_base_period + '):' + plan_name
        result.append(output)
        # print(plan_version)
    # [{'a': {'plan_constraints': "[{'hierarchyOne': 'None', 'inequality': 'None', 'values': 'None', 'operator': 'None', 'hierarchyTwo': 'None'}]", 'division': 'A1_1', 'plan_base_period': 'Yearly', 'end_plan_date': '2022/04/27', 'name': 'Info', 'start_plan_date': '2022/04/06', 'version': 3, 'plan_name': 'hello new world', 'plan_description': 'Hello new world', 'plan_created': '4/27/2022, 3:51:13 PM'}}, {'a': {'plan_constraints': "[{'hierarchyOne': 'None', 'inequality': 'None', 'values': 'None', 'operator': 'None', 'hierarchyTwo': 'None'}]", 'division': 'A1_1', 'plan_base_period': 'Yearly', 'end_plan_date': '2022/04/27', 'name': 'Info', 'start_plan_date': '2022/04/06', 'version': 1, 'plan_name': 'Budgets for Christmas', 'plan_created': '4/27/2022, 1:15:11 PM', 'plan_description': 'Christmas'}}]
    # print(x)
    return result

    
def commitOperator(savedBudgetPlan: List[dict], 
                   plan_name, plan_created, plan_base_period,
                   start_plan_date, end_plan_date, plan_description, plan_constraints, division, budgetNameEdit, budgetNameView, userName, last_edit, who_changed):
    """
    This function will grab the budget plan data from the server
    and forward the data to the graph database.
    @param savedBudgetPlan: [{date: int, ..., id: int, hierarchy: []}]
    """
    budget_graph = neo4j_python.Graph(bolt_address, "neo4j", neo4j_passwd)
    
    savedBudgetPlan_df = pd.DataFrame(savedBudgetPlan)
    hierarchies = [element['hierarchy'] for element in savedBudgetPlan]
    hierarchies_by_len = sorted(hierarchies, key=len, reverse=False)
    
    budgetPlanString = ''
    for hierarchy in hierarchies_by_len:
        rows = savedBudgetPlan_df[savedBudgetPlan_df.hierarchy.map(tuple).isin([tuple(hierarchy)])]
        hierarchy_depth = len(hierarchy)
        del rows['hierarchy'], rows['id']
        
        attributes = rows.to_dict(orient='records')[0]
        attributes = { 'D_' + k: v for k, v in attributes.items() }
        attributes = { k.replace('-','_'): v for k, v in attributes.items() }
        identifier = 'budget' + str(hierarchy_depth)
        name = hierarchy[-1]
        attributes['name'] = name

        attributesOnly = '{'
        for k, v in attributes.items():
            if k != 'name':
                attributesOnly = attributesOnly + str(k) + ':' + str(v) + ','
            else:
                attributesOnly = attributesOnly + str(k) + ':' + "\"" + v + "\""+ ','
        attributesOnly = attributesOnly[:len(attributesOnly) -1] + '}'
        budgetPlanString = budgetPlanString + ',' + '(:' + identifier + ' ' + attributesOnly + ')'

    budgetPlanString = 'CREATE' + budgetPlanString[1:]
    budget_graph.createBudgetPlanNodes(budgetPlanString)

    version = budget_graph.createVersionNode(str(savedBudgetPlan), plan_name, plan_created, plan_base_period, start_plan_date, end_plan_date, plan_description, plan_constraints, division, budgetNameEdit, budgetNameView, userName, last_edit, who_changed)
    
    budget_graph.createBudgetInformationNode(version, plan_name, plan_created, plan_base_period, start_plan_date, end_plan_date, plan_description, plan_constraints, division, budgetNameEdit, budgetNameView, userName, last_edit, who_changed)

    for hierarchy in hierarchies_by_len:
        rows = savedBudgetPlan_df[savedBudgetPlan_df.hierarchy.map(tuple).isin([tuple(hierarchy)])]
        hierarchy_depth = len(hierarchy)
        del rows['hierarchy'], rows['id']
        identifier = 'budget' + str(hierarchy_depth)
        name = hierarchy[-1]

        if hierarchy_depth == 1:
            budget_graph.createBudgetInformationRelationship(version)

        if hierarchy_depth > 1:
            superior_name = hierarchy[-2]
            superior_identifier = 'budget' + str(hierarchy_depth - 1)
            budget_graph.createBudgetPlanRelationship(identifier, name, superior_identifier, superior_name, version)
    return version

##############################
####  History Page
##############################

def getHistoryOperator():
    """
    This function will get history of old budget graph from the version graph database
    """
    budget_graph = neo4j_python.Graph(bolt_address, "neo4j", neo4j_passwd)
    version_history = budget_graph.getHistoryOfVersionGraph()
    return version_history

def retrieveOperator(version):
    """
    @param version: float data type
    This function will first get all available versions from the budget database 
    and checks if specified version is in that list of versions. Bring back the old
    budget graph from the version if it is not already in the budget database.
    """
    budget_graph = neo4j_python.Graph(bolt_address, "neo4j", neo4j_passwd)
    versions_from_neo4j_database = budget_graph.getAllVersionsInBudgetGraph()
    version_collection = [ver['version'] for ver in versions_from_neo4j_database]
    if version in version_collection:
        return 'fail'
    else:
        data = budget_graph.retrieveBudgetGraph(version)[0]['a']
        plan_base_period = data['plan_base_period']
        start_plan_date = data['start_plan_date']
        end_plan_date = data['end_plan_date']
        plan_created = datetime.now().strftime("%-m/%-d/%Y, %-I:%M:%S %p")
        plan_name = data['plan_name']
        division = data['division']
        budgetNameEdit = data['budgetNameEdit']
        budgetNameView = data['budgetNameView']
        userName = data['userName']
        last_edit = data['last_edit']
        plan_description = data['plan_description']
        plan_constraints = data['plan_constraints']
        userName = data['userName']
        who_changed = data['who_changed']
        data = eval(data['history'])
        version = commitOperator(data, plan_name, plan_created, plan_base_period, start_plan_date, end_plan_date, plan_description, plan_constraints, division, budgetNameEdit, budgetNameView, userName, last_edit,who_changed)
        return 'success'

##############################
####  Plan Page
##############################

def commitEdittedBudgetPlanOperator(savedBudgetPlan: List[dict], 
                   plan_name, plan_created, plan_base_period,
                   start_plan_date, end_plan_date, plan_description, plan_constraints, version, division, budgetNameEdit, budgetNameView, userName, last_edit, who_changed):
    """
    This function will grab the budget plan data from the server
    and forward the data to the graph database.
    @param savedBudgetPlan: [{date: int, ..., id: int, hierarchy: []}]
    """

    budget_graph = neo4j_python.Graph(bolt_address, "neo4j", neo4j_passwd)
    
    savedBudgetPlan_df = pd.DataFrame(savedBudgetPlan)
    hierarchies = [element['hierarchy'] for element in savedBudgetPlan]
    hierarchies_by_len = sorted(hierarchies, key=len, reverse=False)
    
    budgetPlanString = ''
    for hierarchy in hierarchies_by_len:
        rows = savedBudgetPlan_df[savedBudgetPlan_df.hierarchy.map(tuple).isin([tuple(hierarchy)])]
        hierarchy_depth = len(hierarchy)
        del rows['hierarchy'], rows['id']
        
        attributes = rows.to_dict(orient='records')[0]
        attributes = { 'D_' + k: v for k, v in attributes.items() }
        attributes = { k.replace('-','_'): v for k, v in attributes.items() }
        identifier = 'budget' + str(hierarchy_depth)
        name = hierarchy[-1]
        attributes['name'] = name

        attributesOnly = '{'
        for k, v in attributes.items():
            if k != 'name':
                attributesOnly = attributesOnly + str(k) + ':' + str(v) + ','
            else:
                attributesOnly = attributesOnly + str(k) + ':' + "\"" + v + "\""+ ','
        attributesOnly = attributesOnly[:len(attributesOnly) -1] + '}'
        budgetPlanString = budgetPlanString + ',' + '(:' + identifier + ' ' + attributesOnly + ')'

    budgetPlanString = 'CREATE' + budgetPlanString[1:]
    
    budget_graph.createBudgetPlanNodes(budgetPlanString)

    budget_graph.setVersionNode(str(savedBudgetPlan), version)
    budget_graph.createBudgetInformationNode(version, plan_name, plan_created, plan_base_period, start_plan_date, end_plan_date, plan_description, plan_constraints, division, budgetNameEdit, budgetNameView, userName, last_edit, who_changed)

    for hierarchy in hierarchies_by_len:
        rows = savedBudgetPlan_df[savedBudgetPlan_df.hierarchy.map(tuple).isin([tuple(hierarchy)])]
        hierarchy_depth = len(hierarchy)
        del rows['hierarchy'], rows['id']
        identifier = 'budget' + str(hierarchy_depth)
        name = hierarchy[-1]

        if hierarchy_depth == 1:
            budget_graph.createBudgetInformationRelationship(version)

        if hierarchy_depth > 1:
            superior_name = hierarchy[-2]
            superior_identifier = 'budget' + str(hierarchy_depth - 1)
            budget_graph.createBudgetPlanRelationship(identifier, name, superior_identifier, superior_name, version)

def commitOperatorForMerge(version, firstVersion, secondVersion):
    """
    This function will create and delete version necessary for the merging process
    @param version: new version for merge node
    @param firstVersion: a version for first budget plan
    @param seoncdVersion: a version for second budget plan
    """
    budget_graph = neo4j_python.Graph(bolt_address, "neo4j", neo4j_passwd)
    budget_graph.connectBudgetVersionRelationship(version, firstVersion, secondVersion)
    # budget_graph.deleteBudgetGraph(firstVersion)
    # budget_graph.deleteBudgetGraph(secondVersion)


def deleteOperator(version):
    """
    @param version: float data type
    This function will delete budget plan from the budget plan graph database
    """
    budget_graph = neo4j_python.Graph(bolt_address, "neo4j", neo4j_passwd)
    budget_graph.deleteBudgetGraph(version)

def cloneBudgetOperator(savedBudgetPlan: List[dict], 
                   plan_name, plan_created, plan_base_period,
                   start_plan_date, end_plan_date, plan_description, plan_constraints, version, division, budgetNameEdit, budgetNameView, userName, last_edit, who_changed):
    """
    This function will grab the budget plan data from the server
    and forward the data to the graph database.
    @param savedBudgetPlan: [{date: int, ..., id: int, hierarchy: []}]
    """
    budget_graph = neo4j_python.Graph(bolt_address, "neo4j", neo4j_passwd)

    previous_version = version
    print(previous_version)
    currentMaxVersion = budget_graph.getBudgetVersionForClone(previous_version)
    print(currentMaxVersion)
    if currentMaxVersion is None:
        # print('here')
        decimal_places = abs(decimal.Decimal(str(version).rstrip('0')).as_tuple().exponent)
        decimal_points = round(0.1 ** (decimal_places + 1), decimal_places + 1)
        version = round(version + decimal_points, decimal_places + 1)
    else:
        # print('here2')
        decimal_places = abs(decimal.Decimal(str(currentMaxVersion).rstrip('0')).as_tuple().exponent)
        decimal_points = round(0.1 ** (decimal_places), decimal_places)
        version = round(currentMaxVersion + decimal_points, decimal_places)
    print(version)
    budget_graph.createVersionNodeForClone(str(savedBudgetPlan), plan_name, plan_created, plan_base_period, start_plan_date, end_plan_date, plan_description, plan_constraints, version, division, budgetNameEdit, budgetNameView, userName, last_edit, who_changed)
    budget_graph.createVersionRelationshipForClone(version, previous_version)
    
    savedBudgetPlan_df = pd.DataFrame(savedBudgetPlan)
    hierarchies = [element['hierarchy'] for element in savedBudgetPlan]
    hierarchies_by_len = sorted(hierarchies, key=len, reverse=False)
    
    budgetPlanString = ''
    for hierarchy in hierarchies_by_len:
        rows = savedBudgetPlan_df[savedBudgetPlan_df.hierarchy.map(tuple).isin([tuple(hierarchy)])]
        hierarchy_depth = len(hierarchy)
        del rows['hierarchy'], rows['id']
        
        attributes = rows.to_dict(orient='records')[0]
        attributes = { 'D_' + k: v for k, v in attributes.items() }
        attributes = { k.replace('-','_'): v for k, v in attributes.items() }
        identifier = 'budget' + str(hierarchy_depth)
        name = hierarchy[-1]
        attributes['name'] = name

        attributesOnly = '{'
        for k, v in attributes.items():
            if k != 'name':
                attributesOnly = attributesOnly + str(k) + ':' + str(v) + ','
            else:
                attributesOnly = attributesOnly + str(k) + ':' + "\"" + v + "\""+ ','
        attributesOnly = attributesOnly[:len(attributesOnly) -1] + '}'
        budgetPlanString = budgetPlanString + ',' + '(:' + identifier + ' ' + attributesOnly + ')'

    budgetPlanString = 'CREATE' + budgetPlanString[1:]

    budget_graph.createBudgetPlanNodes(budgetPlanString)

    budget_graph.setVersionNode(str(savedBudgetPlan), version)
    budget_graph.createBudgetInformationNode(version, plan_name, plan_created, plan_base_period, start_plan_date, end_plan_date, plan_description, plan_constraints, division, budgetNameEdit, budgetNameView, userName, last_edit, who_changed)

    for hierarchy in hierarchies_by_len:
        rows = savedBudgetPlan_df[savedBudgetPlan_df.hierarchy.map(tuple).isin([tuple(hierarchy)])]
        hierarchy_depth = len(hierarchy)
        del rows['hierarchy'], rows['id']
        identifier = 'budget' + str(hierarchy_depth)
        name = hierarchy[-1]

        if hierarchy_depth == 1:
            budget_graph.createBudgetInformationRelationship(version)

        if hierarchy_depth > 1:
            superior_name = hierarchy[-2]
            superior_identifier = 'budget' + str(hierarchy_depth - 1)
            budget_graph.createBudgetPlanRelationship(identifier, name, superior_identifier, superior_name, version)

def getAllBudgetGraphPropertiesFromDatabase():
    """
    This function will returns properties from the information node in the neo4j graph database
    The return format is [{'data': {'plan_base_period': 'Yearly', 'version': 1, 'plan_name': 'December Plan'...}]
    """
    budget_graph = neo4j_python.Graph(bolt_address, "neo4j", neo4j_passwd)
    budget_properties = budget_graph.getBudgetGraphProperties()
    return budget_properties

def saveAsOperator(version, form):
    """
    @param version: float data type 
    @param form: dictionary data structure type {'plan_name': 'December Plan', ...}
    This function triggers updates the changes to the graph database.
    """
    budget_graph = neo4j_python.Graph(bolt_address, "neo4j", neo4j_passwd)
    budget_graph.updateBudgetGraphProperties(version, form)
    budget_graph.updateVersionGraphProperties(version, form)

def getVersionBudgetGraph(version):
    """
    @param version: float data type 
    This function will return rows, columns, and properties for react server
    """
    budget_graph = neo4j_python.Graph(bolt_address, "neo4j", neo4j_passwd)
    node_paths, result = budget_graph.getBudgetGraphWithSpecifiedVersion(version)
    # attributes = { 'D_' + k: v for k, v in attributes.items() }
    # Make Row Information
    id = 0
    rows_list = []
    for paths in node_paths:
        hierarchies = []
        path = paths['nodes']
        require_budget = copy.deepcopy(path[-1])
        require_budget = { k.replace('D_', ''): v for k, v in require_budget.items() }
        require_budget = { k.replace('_','-'): v for k, v in require_budget.items() }
        
        # print(require_budget)
        del require_budget['name']
        for each in path:
            hierarchies.append(each['name'])
        require_budget['hierarchy'] = hierarchies
        require_budget['id'] = id
        id = id + 1
        rows_list.append(require_budget)

    # Make Property Information
    infoProperty = result[0]['info']
    end_plan_date = infoProperty['end_plan_date']
    start_plan_date = infoProperty['start_plan_date']
    plan_base_period = infoProperty['plan_base_period']
    # print(end_plan_date)
    # print(start_plan_date)
    # start_plan_date = '2017-08-03'
    # end_plan_date = '2017-10-03'
    # start_plan_date = '2016-08-03'
    # end_plan_date = '2017-01-03'
    plan_created = infoProperty['plan_created']
    plan_name = infoProperty['plan_name']
    plan_description = infoProperty['plan_description']
    plan_constraints = infoProperty['plan_constraints']
    view = infoProperty['view']
    edit = infoProperty['edit']
    # print(infoProperty)

    userName = infoProperty['userName']
    last_edit = infoProperty['last_edit']

    division = infoProperty['division']

    property_list = {'plan_base_period':plan_base_period, 'start_plan_date':start_plan_date, 
                     'end_plan_date':end_plan_date, 'plan_created':plan_created, 'plan_name':plan_name, 
                     'plan_description':plan_description, 'plan_constraints': plan_constraints, 
                     'view': view, 'edit':edit, 'division': division,
                     'userName': userName, 'last_edit':last_edit}


    # Make Column Information
    if plan_base_period == 'Monthly':
        startToEndPeriod = pd.period_range(start_plan_date, end_plan_date, freq='M')
    elif plan_base_period == 'Quarterly':
        startToEndPeriod = pd.period_range(start_plan_date, end_plan_date, freq='Q')
    else:
        startToEndPeriod = pd.period_range(start_plan_date, end_plan_date, freq='Y')
    startToEndPeriod = list(startToEndPeriod)
    startToEndPeriod = [str(i) for i in startToEndPeriod]
    
    periods = node_paths[0]['nodes'][0]
    del periods['name']
    periods = list(periods.keys())
    periods = sorted(periods)

    columns_list = []
    for row in periods:
        row = row.split('D_')[1]
        row = row.replace('_', '-')
        columns_dict = dict()
        columns_dict['field'] = row
        columns_dict['headerName'] = row
        columns_dict['width'] = 100
        if row not in startToEndPeriod:
            columns_dict['editable'] = 0
            columns_dict['cellClassName'] = 'super-app-theme--cell'
        else:
            columns_dict['editable'] = 1
        columns_dict['align'] = 'right'
        columns_dict['headerAlign'] = 'center'
        columns_dict['type'] = 'number'
        columns_list.append(columns_dict)
    return rows_list, columns_list, property_list



