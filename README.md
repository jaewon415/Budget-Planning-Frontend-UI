# Budget Planning

<p align="center">
  <img width="642" alt="Screen Shot 2022-07-03 at 9 26 40 AM" src="https://user-images.githubusercontent.com/17026620/177019940-83ca5947-7324-44e4-8183-eff67aca3a73.png">
  
</p>

<!-- <p align="center">
<img width="290"  src="https://user-images.githubusercontent.com/17026620/177019707-678a8a31-10f3-4761-9999-2f12582eaac3.png">
</p>

- **Version Control**: Application has version control functionalities implemented, such as merge, clone, retrieve, etc. 
- **Access Control**: Planner can choose who can edit the budget and who can view the budget (and rolling-up the budget).
- **Excel-Like**: Supports redo, undo, write formula, revert, etc on the hierarchical spreadsheet.
- **Disaggregation**: Referential, Interval, proportional, and row-average disaggregate operators are implemented -->

There are five main pages in the budget planning UI:
-	**Home Page**: Budget planners typically don’t stick with just one budget because there are too many uncertainties about the future. The whole point of a budget is to set expectations over a certain period of time and measure performance against the actual. This page will allow a planner to compare actual against budget to measure year-to-date performance and make strategic decisions accordingly.

-	**Create Page**: Making a budget plan is the first step toward the budget process. The planner can think of this process as designing a template for the budget plan – the planning period may be in months, quarters, or even years. The planner should complete the form on the create page with the right information. The required entries are the name of the budget plan, the planning duration, the base planning period, and the plan description (constraints, access control, and roll-up if applicable)

-	**Plan Page**: The plan page reduces the time to create and delete a budget plan while adding more reliability to the budget data. The planner can merge, clone, and edit plans in the plan graph database and speed up the budgeting process. That said, one can only process one budget at a time – the planner cannot clone multiple budget plans in one click.

-	**Table Page**: This page is not on the navigation bar on the left, but one can navigate to the table page by creating a budget plan from the create page or clicking the edit plan button on the plan page. The budget spreadsheet on this page can take numeric values and text formulas like that of excel. 

-	**History Page**: The history page gives the planner access to old copies of the budget plans and shows the number of each version as well as who created each version and when. The planner can restore the old budget plan from this page.


## Installation & Dependencies

**React**
- npm init
- npm install (download everything on the package.json file)

**Python**
- pip install neo4j==4.4.3
- pip install mysql-connector-python==2.2.9
- pip install pandas==1.4.2
- pip install Flask==2.1.2
- pip install Flask-Cors==3.0.10
- pip install numpy

## How To Start
1. Define a label for your hierarchical structure in export_variables.py
2. Create two graph databases; one for version, another for actuals (need to change the username of the database)
3. Change the bolt-listen-address, name, password in the neo4j_python.Graph() & mysql.connector.connect() functions (*.py)
4. Change the path variable in the flask_server.py
5. python flask_server.py
6. npm start

## Excel vs. Budget Planning App

**Dependent on the creator**: Excel spreadsheets are typically dependent on one person who constructed the budget and who updates them every year. Most challenges with Excel come from the fact that there is lack of knowledge transfer when the person that created the spreadsheet leaves the company.

**Inefficient**: Excel is unfortunately vulnerable to human error, as it relies on manual data entry to create budgets and plans. If any part of the data is entered incorrectly, it may throw off the entire plan, which could have a devastating impact on the company. There is a lot of work spent on modifying and correcting Excel spreadsheets.

**One User-Oriented**: Excel is difficult for multiple users entering and analysing data at the same time. The file becomes more prone to error when multiple users are editing and accessing the data at the same time. Budgeting often requires consolidating data from across the organization.

## Key Functionalities

### I. Create a budget plan
<p align="center">
  <img width="350" height="250" src="https://user-images.githubusercontent.com/17026620/177019136-70a1aba0-7c75-4263-85af-40f1a4e44af2.png">
</p>

To create a plan, the planner must fill out the required information (*) on the form, and all inputs should also be valid. For instance, the date should be in mm/dd/yyyy format, and constraints should have all entries filled out. 

**Select Start of the Plan and End of the Plan**: It is a defined date interval for the budget plan. The End of the Plan date cannot be earlier than the Start of the Plan.
 
**Select Base Planning Period**: It is a defined time interval for the budget plan columns. The planner can choose from the following options: Monthly, Quarterly, and Yearly.

**Add Constraints**: Some constraints on a budget plan may be necessary. For instance, the labor cost should not be more than some percentage of the overall budget. 

**Select Roll-up plan**s: Like how every location in the organization is represented as part of the organization structure hierarchy, the budget plans of entities can also be a part of the budget plan of the larger entity. The planner can create a new roll-up budget plan and edit the plan as one would do with other budget plans. A roll-up plan will consolidate multiple budget plans from its subordinate organization. 

**Access Control**:  Allow planners in the division/department to view or edit the budget plan in the lower level of the organization hierarchy. 

### II. Manipulate a budget plan

<p align="center">
  <img width="358" alt="image" src="https://user-images.githubusercontent.com/17026620/177019177-885737b4-4d87-4f00-96fa-7c70b6d080c7.png">
</p>

**Clone**: This operation will generate an identical budget plan that is already in the graph database.

**Delete**: This operation will delete a budget plan from the plan graph database. Deleting the plan from the plan graph database will not affect the version node in the history database. 

**Edit plan**: The planner can edit the budget plan. The current page will redirect to the Table page when clicked. The planner can then edit the plan as one would do with other budget plans.

**Save as**: This will allow the planner to make changes to the initial budget information such as constraints, plan start and end date, etc.

<p align="center">
  <img width="324" alt="image" src="https://user-images.githubusercontent.com/17026620/177019191-8f8b4d04-5262-48ea-824c-08f7942feea6.png">
</p>

**Merge**: This operation will merge two budget plans into one budget plan.

### III. Edit Hierarchical Spreadsheet

Save: This operation will save the changes made on the working spreadsheet to the plan graph database.

Revert: This operation will reset the modifications made to the working spreadsheet. It will copy what was in the working spreadsheet before any edit was made to the table. No matter what is in the working spreadsheet, everything will be cleared out. 

Undo/Redo: The undo function is used to reverse a mistake, such as deleting the wrong word in a sentence. The redo function restores any actions that were previously undone using an undo.

Disaggregation: The application provdies a variety of data spreading methods that you can use to distribute numeric data to cells. For example, you can use data spreading to evenly distribute a value across a range of cells or to increment all values in a range of cells by a desired percentage. The methods that are available in the disaggregation dialog box.

- Referential Disaggregation: This method disaggregates a value to its immediate subordinate categories by some reference values in the previous planning period.
- Proportional disaggregation: This method disaggregates a value to its immediate subordinate categories evenly.
- Row average: This method uses the average of each budget data in the planning period to fill out the budget value of interest.
- Interval Disaggregation: Different from the traditional method where the planner had to work top-down to disaggregate the target, the interval disaggregation operation automates the disaggregation process using the prediction interval of linear regression on the hierarchical data.

### IV. Retrive a budget plan


<p align="center">
  <img width="362" alt="image" src="https://user-images.githubusercontent.com/17026620/177019293-0b333c60-4315-4264-9668-53c7df2cf92c.png">
</p>

Retrieve operation will bring back the old budget plan (blue) from the version history graph database to the plan graph database.

## References
