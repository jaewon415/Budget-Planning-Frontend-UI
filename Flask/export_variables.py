# First Data
GROUPS = [['데이터사이언스대학원'],
            ['데이터사이언스대학원', '과제A'],
            ['데이터사이언스대학원', '과제A', '간접비'],
            ['데이터사이언스대학원', '과제A', '직접비'],
            ['데이터사이언스대학원', '과제A', '직접비', '연구과제추진비'],
            ['데이터사이언스대학원', '과제A', '직접비', '연구활동비'],
            ['데이터사이언스대학원', '과제A', '직접비', '인건비']
         ]


ORGANIZATION_HIERARCHY = {
    '관리부': ['총무과', '원무과', '시설팀'],
    '총무과': ['관리운영팀', '인사복지팀'],
    '원무과': ['고객지원팀', '재무관리팀', '심사관리팀'],
    '시설팀': []
}

HEADER = ['category', 'sub_category', 'claim_number', 
          'claim_identifier', 'use_date', 'claimant', 
          'department', 'total_value', 'supply_value', 
          'vat', 'for_what', 'type', 'misc'
         ]

HISTORY_COLUMN = [
        {'field': 'version', 'headerName': 'Version', 'width': 150, 'editable': 0, 'headerAlign': 'center', 'align': 'center'},
        {'field': 'plan_name', 'headerName': 'Plan Name', 'width': 150, 'editable': 0, 'headerAlign': 'center', 'align': 'center' },
        {'field': 'userName', 'headerName': 'Created By', 'width': 150, 'editable': 0, 'headerAlign': 'center', 'align': 'center' },
        {'field': 'date_created', 'headerName': 'Date Created', 'width': 200, 'editable': 0, 'headerAlign': 'center', 'align': 'center' },
        {'field': 'plan_base_period', 'headerName': 'Planning Period', 'width': 150, 'editable': 0, 'headerAlign': 'center', 'align': 'center' },
        {'field': 'plan_description', 'headerName': 'Description', 'width': 150, 'editable': 0, 'headerAlign': 'center', 'align': 'center' }
    ]

COLUMNS_CLONE = [
        {
         'field': 'plan_name',
         'headerName': 'Plan Name',
         'width': 150,
         'editable': 0,
         'headerAlign': 'center', 
         'align': 'center'    
        },
        {
         'field': 'userName',
         'headerName': 'Created By',
         'width': 150,
         'editable': 0,
         'headerAlign': 'center', 
         'align': 'center'    
        },
        {
         'field': 'plan_created',
         'headerName': 'Date Created',
         'width': 200,
         'editable': 0,
         'headerAlign': 'center', 
         'align': 'center' 
        },
        {
         'field': 'plan_base_period',
         'headerName': 'Planning Period',
         'width': 150,
         'editable': 0,
         'headerAlign': 'center', 
         'align': 'center' 
        },
        {
         'field': 'last_edit',
         'headerName': 'Last Edit',
         'width': 150,
         'editable': 0,
         'headerAlign': 'center', 
         'align': 'center' 
        },
        {
         'field': 'who_changed',
         'headerName': 'Last Edit By',
         'width': 150,
         'editable': 0,
         'headerAlign': 'center', 
         'align': 'center' 
        },
        {
         'field': 'edit',
         'headerName': 'Edit',
         'width': 150,
         'editable': 0,
         'headerAlign': 'center', 
         'align': 'center'   
        },
        {
         'field': 'view',
         'headerName': 'View',
         'width': 150,
         'editable': 0,
         'headerAlign': 'center', 
         'align': 'center'   
        },
        {
         'field': 'version',
         'headerName': 'Version',
         'width': 150,
         'editable': 0,
         'headerAlign': 'center', 
         'align': 'center'   
        },
        
        {
         'field': 'plan_description',
         'headerName': 'Description',
         'width': 150,
         'editable': 0,
         'headerAlign': 'center', 
         'align': 'center' 
        },
        {
         'field': 'start_plan_date',
         'headerName': 'Start Plan',
         'width': 150,
         'editable': 0,
         'headerAlign': 'center', 
         'align': 'center' 
        },
        {
         'field': 'end_plan_date',
         'headerName': 'End Plan',
         'width': 150,
         'editable': 0,
         'headerAlign': 'center', 
         'align': 'center' 
        },
        # {
        #  'field': 'base_period',
        #  'headerName': 'Base Period',
        #  'width': 150,
        #  'editable': 0,
        #  'headerAlign': 'center', 
        #  'align': 'center'    
        # },
    ]