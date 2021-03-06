# Budget Planning

<p align="center">
  <img width="643" alt="Screen Shot 2022-07-03 at 9 26 40 AM" src="https://user-images.githubusercontent.com/17026620/177019940-83ca5947-7324-44e4-8183-eff67aca3a73.png">
  
</p>

<!-- <p align="center">
<img width="290"  src="https://user-images.githubusercontent.com/17026620/177019707-678a8a31-10f3-4761-9999-2f12582eaac3.png">
</p>

- **Version Control**: Application has version control functionalities implemented, such as merge, clone, retrieve, etc. 
- **Access Control**: Planner can choose who can edit the budget and who can view the budget (and rolling-up the budget).
- **Excel-Like**: Supports redo, undo, write formula, revert, etc on the hierarchical spreadsheet.
- **Disaggregation**: Referential, Interval, proportional, and row-average disaggregate operators are implemented -->

There are five main pages in the budget planning UI:
-	**Home Page**: Budget planners typically don’t stick with just one budget because there are too many uncertainties about the future. The whole point of a budget is to set expectations over a certain period of time and measure performance against the actual. This page will allow a planner to compare actual against budget to measure X-to-date performance and make strategic decisions accordingly.

-	**Create Page**: Making a budget plan is the first step toward the budget process. The planner can think of this process as designing a template for the budget plan – the planning period may be in months, quarters, or even years. The planner should complete the form on the create page with the right information. The required entries are the name of the budget plan, the planning duration, the base planning period, and the plan description (constraints, access control, and roll-up if applicable)

-	**Plan Page**: The plan page reduces the time to create and delete a budget plan while adding more reliability to the budget data. The planner can merge, clone, and edit plans in the plan graph database and speed up the budgeting process. That said, one can only process one budget at a time – the planner cannot clone multiple budget plans in one click.

-	**Table Page**: This page is not on the navigation bar on the left, but one can navigate to the table page by creating a budget plan from the create page or clicking the edit plan button on the plan page. The budget spreadsheet on this page can take numeric values and text formulas like that of excel. 

-	**History Page**: The history page gives the planner access to old copies of the budget plans and shows the number of each version as well as who created each version and when. The planner can restore the old budget plan from this page.


## Installation & Dependencies

**React**
```
npm init
npm install (package.json)
```
**Python**
```
pip install neo4j==4.4.3
pip install mysql-connector-python==2.2.9
pip install pandas==1.4.2
pip install Flask==2.1.2
pip install Flask-Cors==3.0.10
pip install numpy
```

## How To Start
1. Define a label for your hierarchical structure in `export_variables.py`
2. Create two graph databases; one for version, another for actuals (need to change the username of the database)
3. Change the bolt-listen-address, name, and password in the `neo4j_python.Graph()` & `mysql.connector.connect()` functions (*.py)
4. Change the `path` variable in the flask_server.py
5. `python flask_server.py`
6. `npm start`

## Data format 
- Define a category and its subcategory in the `export_variables.py`
  - Items are linked to each other in parent-child relationships
- Change the column names in the `flask_server.py`

<p align="center">
  <img width="496" alt="Screen Shot 2022-07-05 at 10 23 18 AM" src="https://user-images.githubusercontent.com/17026620/177231610-53b13a6c-4551-4cfa-8aaf-5a8c9644b74c.png">
</p>


## Key Functionalities

### I. Create a budget plan
<p align="center">
  <img width="290" height="210" src="https://user-images.githubusercontent.com/17026620/177019136-70a1aba0-7c75-4263-85af-40f1a4e44af2.png">
</p>

To create a plan, the planner must fill out the required information (*) on the form, and all inputs should also be valid. For instance, the date should be in mm/dd/yyyy format, and constraints should have all entries filled out. 

**Select Start of the Plan and End of the Plan**: It is a defined date interval for the budget plan. The End of the Plan date cannot be earlier than the Start of the Plan.
 
**Select Base Planning Period**: It is a defined time interval for the budget plan columns. The planner can choose from the following options: Monthly, Quarterly, and Yearly.

**Add Constraints**: Some constraints on a budget plan may be necessary. For instance, the labor cost should not be more than some percentage of the overall budget. 

**Select Roll-up plan**s: Like how every location in the organization is represented as part of the organization structure hierarchy, the budget plans of entities can also be a part of the budget plan of the larger entity. The planner can create a new roll-up budget plan and edit the plan as one would do with other budget plans. A roll-up plan will consolidate multiple budget plans from its subordinate organization. 

**Access Control**:  Allow planners in the division/department to view or edit the budget plan at the lower level of the organization hierarchy. 

### II. Manipulate a budget plan

<p align="center">
  <img width="358" alt="image" src="https://user-images.githubusercontent.com/17026620/177019177-885737b4-4d87-4f00-96fa-7c70b6d080c7.png">
</p>

**Clone**: This operation will generate an identical budget plan. When you clone a budget plan, you copy the plan from the graph database.

<p align="center">
  <img width="654" alt="image" src="https://user-images.githubusercontent.com/17026620/178139339-6402e093-b3fc-4f6d-b461-be8c1802e3b5.png">
</p>

1. On the budget planning application, navigate to the **plans** page.
2. Select a budget plan
3. Above the list of operations available, click CLONE to copy the budget plan

**Delete**: This operation will delete a budget plan from the plan graph database. Deleting the plan from the plan graph database will not affect the version node in the history database. 

<p align="center">
  <img width="672" alt="image" src="https://user-images.githubusercontent.com/17026620/178139352-1514e9d4-7967-4eee-96a9-cceaf4bacfac.png">
</p>

1. On the budget planning application, navigate to the **plans** page.
2. Select a budget plan
3. Above the list of operations available, click DELETE to delete the budget plan
4. To retrieve deleted budget plan, navigate to the **History** page.

**Edit plan**: The planner can edit the budget plan. The current page will redirect to the Table page when clicked. The planner can then edit the plan as one would do with other budget plans.

<p align="center">
  <img width="661" alt="image" src="https://user-images.githubusercontent.com/17026620/178139357-89c4c45c-698b-4a40-a4ae-4aa6a2a29453.png">
</p>

1. On the budget planning application, navigate to the **plans** page.
2. Select a budget plan
3. Above the list of operations available, click Edit
4. Upon click, it redirects to the hierarchical spreadsheet

**Save as**: This will allow the planner to make changes to the initial budget information such as constraints, plan start and end date, etc.

<p align="center">
  <img width="628" alt="image" src="https://user-images.githubusercontent.com/17026620/178139370-adbf2086-781b-4cc8-8e11-d598c2d705ca.png">
</p>

1. On the budget planning application, navigate to the **plans** page.
2. Select a budget plan
3. Above the list of operations available, click Save As
4. Plan Information box will show up on the right
5. Change the budget plan information such constraints and description
6. Click Save when you are done

**Retrieve**: This operation will bring back the old budget plan from the version history graph database to the plan graph database.

**Merge**: Some budget items in the project may need to be reduced or eliminated for a variety of reasons, ranging from This operation will merge two budget plans into one budget plan.

<p align="center">
  <img width="504" alt="image" src="https://user-images.githubusercontent.com/17026620/178139431-1cda17d6-9eb2-461a-8b45-95e4c874d4ad.png">
</p>

1. On the budget planning application, navigate to the **plans** page.
2. Select two budget plans
3. Above the list of operations available, click MERGE

### III. Edit Hierarchical Spreadsheet

**Save**: This operation will save the changes made on the working spreadsheet to the plan graph database.

**Revert**: This operation will reset the modifications made to the working spreadsheet. It will copy what was in the working spreadsheet before any edit was made to the table. No matter what is in the working spreadsheet, everything will be cleared out. 

**Undo/Redo**: The undo function is used to reverse a mistake, such as deleting the wrong word in a sentence. The redo function restores any actions that were previously undone using an undo.

**Disaggregation**: The application provides a variety of data spreading methods that you can use to distribute numeric data to cells. For example, you can use data spreading to distribute a value across a range of cells evenly or to increment all values in the hierarchical spreadsheet. The methods are available in the disaggregation dialog box.

<p align="center">
  <img width="498" alt="image" src="https://user-images.githubusercontent.com/17026620/178140198-c75bda0e-f38e-4c95-9a11-3617c5813aba.png">
</p>

1. Choose one disaggregation method from the list.
2. Write a category you would like to disaggregate 
3. Ignore if you have not selected referential disaggregation above; else write the name of the column you wish to take reference of
4. Type the planning month of your interest 
5. Enter the amount you would like to disaggregate 

Disaggregation methods available in this application are as follows::
- Referential Disaggregation: This method disaggregates a value to its immediate subordinate categories by some reference values in the previous planning period.
- Proportional disaggregation: This method disaggregates a value to its immediate subordinate categories evenly.
- Row average: This method uses the average of each budget data in the planning period to fill out the budget value of interest.
- Interval Disaggregation: Different from the traditional method, where the planner had to work top-down to disaggregate the target, the interval disaggregation operation automates the disaggregation process using the prediction interval of linear regression on the hierarchical data.

Constraints have as much importance to business planning. The quality of the plan boils down to how well one identifies the policies and requirements. For many real-world applications, however, the elements in the hierarchical structure share common constraints. This is the case for budget planning. For instance, the travel expense cannot exceed 20% of research activity expenses. Then planner has to think about the constraint on the travel expense when disaggregating a value. The budget planner can also add constraints in the disaggregation dialog box. This functionality is only bounded to interval disaggregation.


<p align="center">
  <img width="350" alt="image" src="https://user-images.githubusercontent.com/17026620/178140613-a3e38409-83c7-4d55-bf82-41852bc5e289.png">
</p>


<!-- 
### IV. Retrive a budget plan

<p align="center">
  <img width="362" alt="image" src="https://user-images.githubusercontent.com/17026620/177019293-0b333c60-4315-4264-9668-53c7df2cf92c.png">
</p>
 -->

## Excel vs. Budget Planning App

**Dependent on the creator**: Excel spreadsheets are typically dependent on one person who constructed the budget and who updates them every year. Most challenges with Excel come from the fact that there is a lack of knowledge transfer when the person that created the spreadsheet leaves the company.

**Inefficient**: Excel is unfortunately vulnerable to human error, as it relies on manual data entry to create budgets and plans. If any part of the data is entered incorrectly, it may throw off the entire plan, which could have a devastating impact on the company. There is a lot of work spent on modifying and correcting Excel spreadsheets.

**One User-Oriented**: Excel is difficult for multiple users to enter and analyze data at the same time. The file becomes more prone to error when multiple users are editing and accessing the data at the same time. Budgeting often requires consolidating data from across the organization.
