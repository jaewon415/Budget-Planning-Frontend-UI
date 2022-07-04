# !/usr/bin/env python
# coding: utf-8

from neo4j import GraphDatabase

class Graph:
    def __init__(self, uri, user, password):
        """
        This function takes in three parameters to connect graph database engine.
        @param uri: path to localhost or server address
        @param user: the name of the database under budget project
        @param password: the password of the database under budget3 project
        @return None	
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()    

    ################################
    ####   Common Functions 
    ################################

    def getChildrenPropertyInTheOrganizationHierarchy(self, division):
        """
        This function create relationship between budget information
        """
        with self.driver.session(database='neo4j') as session:
            result = session.write_transaction(self._getChildrenPropertyInTheOrganizationHierarchy, division)
        return result
        
    @staticmethod
    def _getChildrenPropertyInTheOrganizationHierarchy(tx, division):
        """
       This function create relationship between budget information
        """
        query = "MATCH (a:budget0 {name: 'Info', division: $division})" + \
                "RETURN a"
        result = tx.run(query, division = division)
        return result.data()

    def createBudgetInformationRelationship(self, version):
        """
        This function create relationship between budget information
        """
        with self.driver.session(database='neo4j') as session:
            query = "MATCH (a:budget0 {name: 'Info', version: $version}) WHERE not ((a)--())" + \
                "MATCH (b:budget1) WHERE not ((b)--())" + \
                "MERGE (a)-[r:includes]->(b)"
            session.run(query, version = version)
            # session.write_transaction(self._createBudgetInformationRelationship, version)
        self.driver.close()
    @staticmethod
    def _createBudgetInformationRelationship(tx, version):
        """
       This function create relationship between budget information
        """
        query = "MATCH (a:budget0 {name: 'Info', version: $version}) WHERE not ((a)--())" + \
                "MATCH (b:budget1) WHERE not ((b)--())" + \
                "MERGE (a)-[r:includes]->(b)"
        tx.run(query, version = version)

    def createBudgetInformationNode(self, version, plan_name, plan_created, plan_base_period,
                   start_plan_date, end_plan_date, plan_description, plan_constraints, division, budgetNameEdit, budgetNameView, userName, last_edit, who_changed):
        """
        This function creates budget information node
        """
        with self.driver.session(database='neo4j') as session:
            session.write_transaction(self._createBudgetInformationNode, version, plan_name, plan_created, plan_base_period,
                   start_plan_date, end_plan_date, plan_description, plan_constraints, division, budgetNameEdit, budgetNameView, userName, last_edit, who_changed)
        self.driver.close()

    @staticmethod
    def _createBudgetInformationNode(tx, version, plan_name, plan_created, plan_base_period,
                   start_plan_date, end_plan_date, plan_description, plan_constraints, division, budgetNameEdit, budgetNameView, userName, last_edit, who_changed):
        """
        This function creates budget information nodes
        """
        query = "CREATE (a: budget0 {name: 'Info', version: $version , plan_name: $plan_name, plan_created: $plan_created, plan_base_period: $plan_base_period, start_plan_date: $start_plan_date, end_plan_date: $end_plan_date, plan_description: $plan_description, plan_constraints: $plan_constraints, division: $division, edit: $budgetNameEdit, view: $budgetNameView, userName: $userName, last_edit: $last_edit, who_changed:$who_changed})" 
        tx.run(query, {'version': version, 'plan_name': plan_name, 'plan_created': plan_created, 'plan_base_period':plan_base_period, 'start_plan_date': start_plan_date, 'end_plan_date': end_plan_date, 'plan_description': plan_description, 'plan_constraints': str(plan_constraints), 'division': division, 'budgetNameEdit': budgetNameEdit, 'budgetNameView': budgetNameView, 'userName': userName, 'last_edit': last_edit, 'who_changed': who_changed})

    def createVersionNode(self, history, plan_name, plan_created, plan_base_period,
                   start_plan_date, end_plan_date, plan_description, plan_constraints, division, budgetNameEdit, budgetNameView, userName, last_edit, who_changed):
        """
        This function creates version node
        """
        with self.driver.session(database='version') as session:
            result = session.write_transaction(self._getVersion)
            if result[0]['max'] is None:
                version = 1
                session.write_transaction(self._createVersionNode, version, history, plan_name, plan_created, plan_base_period, start_plan_date, end_plan_date, plan_description, plan_constraints, division, budgetNameEdit, budgetNameView, userName, last_edit, who_changed)
            else: 
                version = int(result[0]['max']) + 1
                session.write_transaction(self._createVersionNode, version, history, plan_name, plan_created, plan_base_period, start_plan_date, end_plan_date, plan_description, plan_constraints, division, budgetNameEdit, budgetNameView, userName, last_edit, who_changed)
        return version

    @staticmethod
    def _getVersion(tx):
        result = tx.run('MATCH (n:version) WITH max(n.version) AS max RETURN max')
        return result.data()

    @staticmethod
    def _createVersionNode(tx, ver, history, plan_name, plan_created, plan_base_period, start_plan_date, end_plan_date, plan_description, plan_constraints, division, budgetNameEdit, budgetNameView, userName, last_edit, who_changed):
        """
        This function creates version node
        """
        version = ver
        query = "MERGE (n:version {version: $version, history: $history, plan_name: $plan_name, date_created: $plan_created, plan_base_period: $plan_base_period, start_plan_date: $start_plan_date, end_plan_date: $end_plan_date, plan_description: $plan_description, plan_constraints: $plan_constraints, division: $division, edit: $budgetNameEdit, view: $budgetNameView, userName: $userName, last_edit: $last_edit, who_changed: $who_changed})"
        tx.run(query, {'version': version, 'history': history, 'plan_name': plan_name, 'plan_created': plan_created, 'plan_base_period':plan_base_period, 'start_plan_date': start_plan_date, 'end_plan_date': end_plan_date, 'plan_description': plan_description, 'plan_constraints': str(plan_constraints), 'division': division, 'budgetNameEdit': budgetNameEdit, 'budgetNameView':budgetNameView, 'userName': userName, 'last_edit': last_edit, 'who_changed': who_changed})
    
    # def createBudgetPlanNodes(self, identifier, name, attributes):
    #     """
    #     This function creates budget nodes
    #     """
    #     with self.driver.session(database='neo4j') as session:
    #         session.write_transaction(self._createBudgetPlanNodes, identifier, name, attributes)

    # @staticmethod
    # def _createBudgetPlanNodes(tx, identifier, name, attributes):
    #     """
    #     This function creates budget nodes
    #     """
    #     query = "CREATE (a:" + identifier + " {name: $name}) SET a += $attributes" 
    #     tx.run(query, {'name': name, 'attributes': attributes})

    def createBudgetPlanNodes(self, query):
        """
        This function creates budget nodes
        """
        with self.driver.session(database='neo4j') as session:
            session.write_transaction(self._createBudgetPlanNodes, query)

    @staticmethod
    def _createBudgetPlanNodes(tx, query):
        """
        This function creates budget nodes
        """
        query = query
        tx.run(query)

    def removeConstraintTrigger(self):
        """
        This function creates budget nodes
        """
        with self.driver.session(database='neo4j') as session:
            session.write_transaction(self._removeConstraintTrigger)
        self.driver.close()

    @staticmethod
    def _removeConstraintTrigger(tx):
        """
        This function creates budget nodes
        """
        query = 'call apoc.trigger.removeAll()'
        tx.run(query)
    
    def createConstraintTrigger(self, query):
        """
        This function creates budget nodes
        """
        with self.driver.session(database='neo4j') as session:
            session.run(query)
        #     session.write_transaction(self._createConstraintTrigger, query)
        self.driver.close()

    # @staticmethod
    # def _createConstraintTrigger(tx, query):
    #     """
    #     This function creates budget nodes
    #     """
    #     query = query
    #     tx.run(query)

    def createCheckCount(self):
        """
        This function creates budget nodes
        """
        with self.driver.session(database='neo4j') as session:
            result = session.write_transaction(self._createCheckCount)
            session.close()
        return result

    @staticmethod
    def _createCheckCount(tx):
        """
        This function creates budget nodes
        """
        query = 'match (n) where not (n)--() RETURN count(n) AS count'
        result = tx.run(query)
        return result.data()[0]

    def createBudgetPlanRelationship(self, identifier, name, superior_identifier, superior_name, version):
        """
        This function creates budget relationships
        """
        with self.driver.session(database='neo4j') as session:
            session.write_transaction(self._createBudgetPlanRelationship, identifier, name, superior_identifier, superior_name, version)
        self.driver.close()
    @staticmethod
    def _createBudgetPlanRelationship(tx, identifier, name, superior_identifier, superior_name, version):
        """
        This function creates budget relationships
        """
        query = "MATCH (c:budget0 {version: $version})-[*]->(a:" + superior_identifier + " {name: $superior_name})" + \
                "MATCH (b:" + identifier + " {name: $name}) WHERE not ((b)--())" + \
                "MERGE (a)-[r:includes]->(b)"
        tx.run(query, {'name': name, 'superior_name': superior_name, 'version': version})
    
    ################################
    ####   History Page 
    ################################
    
    def getHistoryOfVersionGraph(self):
        """
        This function will get properties from the version database
        """
        with self.driver.session(database='version') as session:
            result = session.read_transaction(self._getHistoryOfVersionGraph)
        return result

    @staticmethod
    def _getHistoryOfVersionGraph(tx):
        query = 'MATCH (data:version) RETURN data'
        result = tx.run(query)
        return result.data()

    def getAllVersionsInBudgetGraph(self):
        """
        This function will get all available versions from the neo4j budget graph database
        """
        with self.driver.session(database='neo4j') as session:
            result = session.read_transaction(self._getAllVersionsInBudgetGraph)
        return result

    @staticmethod
    def _getAllVersionsInBudgetGraph(tx):
        query = 'MATCH (a:budget0) WITH a.version AS version RETURN version'
        result = tx.run(query)
        return result.data()

    def retrieveBudgetGraph(self, version):
        """
        This function will retrieve specified version property from the version graph database
        """
        with self.driver.session(database='version') as session:
            result = session.read_transaction(self._retrieveBudgetGraph, version)
        return result

    @staticmethod
    def _retrieveBudgetGraph(tx, version):
        query = 'MATCH (a:version {version:$version}) RETURN a'
        result = tx.run(query, version = version)
        return result.data()
    ################################
    ####   Plan Page 
    ################################


    def setVersionNode(self, history, version):
        """
        This function will set new history information back to the specified version graph
        """
        with self.driver.session(database='version') as session:
            session.write_transaction(self._setVersionNode, history, version)
    
    @staticmethod
    def _setVersionNode(tx, history, version):
        query = "MATCH (n:version {version: $version}) "  + \
                "SET n.history = $history"
        tx.run(query, version = version, history = history)


    def connectBudgetVersionRelationship(self, version, firstVersion, secondVersion):
        """
        @param version: new version nodes
        @param firstVersion: first version node
        @param secondVersion: second version node
        This function will connect each version (first and second) to newly produced version
        """
        with self.driver.session(database='version') as session:
            session.write_transaction(self._connectBudgetVersionRelationship, version, firstVersion, secondVersion)
    
    @staticmethod
    def _connectBudgetVersionRelationship(tx, version, firstVersion, secondVersion,):
        """
        @param version: new version nodes
        @param firstVersion: first version node
        @param secondVersion: second version node
        This function will connect each version (first and second) to newly produced version
        """
        query = 'MATCH (a:version {version: $firstVersion}) ' + \
                'MATCH (b:version {version: $version}) ' + \
                'MERGE (a)-[r:versioned]->(b)'
        tx.run(query, version = version, firstVersion =firstVersion)

        query = 'MATCH (a:version {version: $secondVersion}) ' + \
                'MATCH (b:version {version: $version}) ' + \
                'MERGE (a)-[r:versioned]->(b)'
        tx.run(query, version = version, secondVersion =secondVersion)

    def deleteBudgetGraph(self, version):
        """
        @param version: float data type
        This function will delete budget plan in the budget graph database
        """
        with self.driver.session(database='neo4j') as session:
            session.write_transaction(self._deleteBudgetGraph, version)
    
    @staticmethod
    def _deleteBudgetGraph(tx, version):
        query = 'MATCH p=(n:budget0 {version: $version})-[*..]->() DETACH DELETE p'
        tx.run(query, version = version)

    def createVersionNodeForClone(self, history, plan_name, plan_created, plan_base_period,
                   start_plan_date, end_plan_date, plan_description, plan_constraints, version, division, budgetNameEdit, budgetNameView, userName, last_edit, who_changed):
        """
        This function creates version node
        """
        with self.driver.session(database='version') as session:
            session.write_transaction(self._createVersionNodeForClone, history, plan_name, plan_created, plan_base_period,
                   start_plan_date, end_plan_date, plan_description, plan_constraints, version, division, budgetNameEdit, budgetNameView, userName, last_edit, who_changed)

    @staticmethod
    def _createVersionNodeForClone(tx, history, plan_name, plan_created, plan_base_period, start_plan_date, end_plan_date, plan_description, plan_constraints, version, division, budgetNameEdit, budgetNameView, userName, last_edit, who_changed):
        """
        This function creates vergetBudgetVersionForClonesion node
        """
        query = "MERGE (n:version {version: $version, history: $history, plan_name: $plan_name, date_created: $plan_created, plan_base_period: $plan_base_period, start_plan_date: $start_plan_date, end_plan_date: $end_plan_date, plan_description: $plan_description, plan_constraints: $plan_constraints, division: $division, budgetNameEdit: $budgetNameEdit, budgetNameView: $budgetNameView, userName: $userName, last_edit: $last_edit, who_changed: $who_changed})"
        tx.run(query, {'version': version, 'history': history, 'plan_name': plan_name, 'plan_created': plan_created, 'plan_base_period':plan_base_period, 'start_plan_date': start_plan_date, 'end_plan_date': end_plan_date, 'plan_description': plan_description, 'plan_constraints': str(plan_constraints), 'division': division, 'budgetNameEdit': budgetNameEdit, 'budgetNameView': budgetNameView, 'userName': userName, 'last_edit': last_edit, 'who_changed': who_changed})

    def createVersionRelationshipForClone(self, version, previous_version):
        """
        This function version relationship for clone operator
        """
        with self.driver.session(database='version') as session:
            session.write_transaction(self._createVersionRelationshipForClone, version, previous_version)

    @staticmethod
    def _createVersionRelationshipForClone(tx, version, previous_version):
        """
        This function version relationship for clone operator
        """
        query = "MATCH (a:version {version: $previous_version})" + \
                "MATCH (b:version {version: $version})" + \
                "MERGE (a)-[r:versioned]->(b)"
        tx.run(query, previous_version = previous_version, version = version)
    
    def getBudgetVersionForClone(self, previous_version):
        """
        This function returns version 
        """
        with self.driver.session(database='version') as session:
            result = session.write_transaction(self._getBudgetVersionForClone, previous_version)
        return result

    @staticmethod
    def _getBudgetVersionForClone(tx, previous_version):
        """
        This function creates budget information version
        """
        query = "MATCH (a:version {version:$previous_version}) " + \
                "MATCH p=((a)-[*1]->(b)) " + \
                "WHERE b.version > floor($previous_version) " + \
                "WITH MAX(b.version) AS max " + \
                "RETURN max"
        result = tx.run(query, previous_version = previous_version)
        return result.data()[0]['max']

    def getBudgetGraphProperties(self):
        """
        This function will return budget graph in the graph database
        """
        with self.driver.session(database='neo4j') as session:
            result = session.read_transaction(self._getBudgetGraphProperties)
        return result

    @staticmethod
    def _getBudgetGraphProperties(tx):
        query = 'MATCH (data:budget0) RETURN data'
        result = tx.run(query)
        return result.data()

    def getBudgetGraphWithSpecifiedVersion(self, version):
        """
        @param version: float type 
        This function will get specified budget graph from the graph database
        """
        with self.driver.session(database='neo4j') as session:
            result = session.read_transaction(self._getBudgetGraphWithSpecifiedVersion, version)
        return result

    @staticmethod
    def _getBudgetGraphWithSpecifiedVersion(tx, version):
        get_top_hierarchy_query = 'MATCH (a:budget1) WITH a.name AS name RETURN DISTINCT name'
        top_hierarchy = tx.run(get_top_hierarchy_query)
        top_hierarchy_identifier = top_hierarchy.data()[0]['name']
        
        get_meta_data_query = 'MATCH (a:budget0 {version: $version}) RETURN a AS info'
        meta_data = tx.run(get_meta_data_query, version = version)

        get_all_connected_to_top_hierarchy_node_query = 'MATCH (a:budget0 {version: $version})-[*]->(b:budget1 {name:$top_hierarchy_identifier})' + \
                                                        'WITH b MATCH p = (b)-[*0..]->()' + \
                                                        'WITH nodes(p) AS nodes RETURN nodes'
        all_connected_nodes = tx.run(get_all_connected_to_top_hierarchy_node_query, version = version, top_hierarchy_identifier = top_hierarchy_identifier)
        return all_connected_nodes.data(), meta_data.data()

    def updateBudgetGraphProperties(self, version, form):
        """
        @param version: float data type 
        @param form: dictionary data structure type {'plan_name': 'December Plan', ...}
        This function will update the changes made to the form on the budget graph database
        """
        with self.driver.session(database='neo4j') as session:
            session.write_transaction(self._updateBudgetGraphProperties, version, form)

    @staticmethod
    def _updateBudgetGraphProperties(tx, version, form):
        plan_name = form['plan_name']
        start_plan_date, end_plan_date = form['start_plan_date'], form['end_plan_date']
        plan_description = form['plan_description']
        plan_created = form['plan_created']
        plan_constraints = str(form['plan_constraints'])
        
        query = "MATCH (n:budget0 {version: $version}) "  + \
                "SET n.plan_name = $plan_name, " + \
                "n.start_plan_date = $start_plan_date, " + \
                "n.end_plan_date = $end_plan_date, " + \
                "n.plan_description = $plan_description, " + \
                "n.plan_created = $plan_created, " + \
                "n.plan_constraints = $plan_constraints"
        tx.run(query, version = version, plan_name = plan_name, start_plan_date = start_plan_date, end_plan_date = end_plan_date, plan_description = plan_description, plan_created = plan_created, plan_constraints = plan_constraints)

    
    def updateVersionGraphProperties(self, version, form):
        """
        @param version: float data type 
        @param form: dictionary data structure type {'plan_name': 'December Plan', ...}
        This function will update the changes made to the form on the version graph database
        """
        
        with self.driver.session(database='version') as session:
            session.write_transaction(self._updateVersionGraphProperties, version, form)

    @staticmethod
    def _updateVersionGraphProperties(tx, version, form):
        plan_name = form['plan_name']
        start_plan_date, end_plan_date = form['start_plan_date'], form['end_plan_date']
        plan_description = form['plan_description']
        plan_created = form['plan_created']
        plan_constraints = str(form['plan_constraints'])

        query = "MATCH (n:version {version: $version}) "  + \
                "SET n.plan_name = $plan_name, " + \
                "n.start_plan_date = $start_plan_date, " + \
                "n.end_plan_date = $end_plan_date, " + \
                "n.plan_description = $plan_description, " + \
                "n.plan_created = $plan_created, " + \
                "n.plan_constraints = $plan_constraints"
        tx.run(query, version = version, plan_name = plan_name, start_plan_date = start_plan_date, end_plan_date = end_plan_date, plan_description = plan_description, plan_created = plan_created, plan_constraints = plan_constraints)


