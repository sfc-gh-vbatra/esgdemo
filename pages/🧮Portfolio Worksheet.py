from distutils import errors
from distutils.log import error
import streamlit as st
import pandas as pd 
import numpy as np
import altair as alt
from itertools import cycle

import functools
from pathlib import Path

from st_aggrid import AgGrid
from st_aggrid.shared import JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

#from snowflake.snowpark.session import Session
#from snowflake.snowpark.functions import *
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL
import snowflake.connector
import numpy as np
import pandas as pd

st.set_page_config(
    page_title="Protfolio Re-Allocation Worksheet",
    layout = "wide"
    
)

st.markdown(""" <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

st.markdown(""" <style> .font {
font-size:50px ; font-family: 'Cooper Black'; color: #FF9633;} 
</style> """, unsafe_allow_html=True)
st.markdown('<p class="font">Portfolio Reallocation Worksheet</p>', unsafe_allow_html=True)




def main() -> pd.DataFrame:
    
    engine = create_engine(URL(
    account = st.secrets["account"],
    user = st.secrets["user"],
    password = st.secrets["password"],
    database = st.secrets["database"],
    schema = st.secrets["schema"],
    warehouse = st.secrets["warehouse"],
    role=st.secrets["role"]
    ))
    try:
        connection = engine.connect()
        df1 = pd.read_sql_query("SELECT portfolio as PORTFOLIO, ticker, internal_esg_score, materiality_esg_rank,materiality_adj_insight, materiality_ind_pctl , market_cap, \
        round(100 * RATIO_TO_REPORT(total_shares*price) OVER (PARTITION BY portfolio),1) AS allocation\
        FROM frostbyte_esg.analytics.daily_portfolio_detail_v\
        where date='2022-04-07'\
        ORDER BY portfolio,allocation desc;", engine)

        return df1
    finally:
        connection.close()
        engine.dispose()

#@st.cache()
#def get_data():
#    df =session.sql("SELECT portfolio, ticker, internal_esg_score, materiality_esg_rank,materiality_adj_insight, materiality_ind_pctl , market_cap, \
#        round(100 * RATIO_TO_REPORT(total_shares*price) OVER (PARTITION BY portfolio),1) AS allocation\
#    FROM frostbyte_esg.analytics.daily_portfolio_detail_v\
#    where date='2022-04-07'\
#    ORDER BY portfolio,allocation desc").toPandas()
    
#    return df
#df1 = get_data()
df1 = main()
df1.columns = df1.columns.str.upper()



from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode



#Example controlers
#st.sidebar.subheader("Portfolio Re-allocation Worksheet")

#sample_size = st.sidebar.number_input("rows", min_value=10, value=30)
grid_height =  400

#return_mode = st.sidebar.selectbox("Return Mode", list(DataReturnMode.__members__), index=1)
#return_mode_value = DataReturnMode.__members__[return_mode]
return_mode_value = 'FILTERED'

#update_mode = st.sidebar.selectbox("Update Mode", list(GridUpdateMode.__members__), index=len(GridUpdateMode.__members__)-1)
#update_mode_value = GridUpdateMode.__members__[update_mode]

update_mode_value = 'MODEL_CHANGED'

#enterprise modules
enable_enterprise_modules = True
enable_sidebar = True


#features
fit_columns_on_grid_load = True

enable_selection= True
selection_mode = 'multiple'
use_checkbox = True
groupSelectsChildren = True
groupSelectsFiltered = True
rowMultiSelectWithClick = True

enable_pagination = True
paginationPageSize=15
paginationAutoSize=True

gb = GridOptionsBuilder.from_dataframe(df1)

#customize gridOptions
gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc='sum', editable=True)
#gb.configure_column("date_only", type=["dateColumnFilter","customDateTimeFormat"], custom_format_string='yyyy-MM-dd', pivot=True)
#gb.configure_column("date_tz_aware", type=["dateColumnFilter","customDateTimeFormat"], custom_format_string='yyyy-MM-dd HH:mm zzz', pivot=True)

gb.configure_column("ALLOCATION", type=["numericColumn","numberColumnFilter","customNumericFormat"], precision=2, aggFunc='sum')
gb.configure_column("PORTFOLIO", filter=False, hide=True)
gb.configure_column("TICKER", checkboxSelection=True)
#gb.configure_column("banana", type=["numericColumn", "numberColumnFilter", "customNumericFormat"], precision=1, aggFunc='avg')
#gb.configure_column("chocolate", type=["numericColumn", "numberColumnFilter", "customCurrencyFormat"], custom_currency_symbol="R$", aggFunc='max')

#configures last row to use custom styles based on cell's value, injecting JsCode on components front end
cellsytle_jscode = JsCode("""
function(params) {
        if (params.value == 'Below Average') {
            return {
                'color': 'black',
                'backgroundColor': 'pink'
            }
        } else if (params.value == 'Laggard') {
            return {
                'color': 'white',
                'backgroundColor': 'crimson'
            }
        } else {
            return {
                'color': 'black',
                'backgroundColor': 'white'
            }
        }
    };
""")
gb.configure_column("MATERIALITY_ESG_RANK", cellStyle=cellsytle_jscode)

if enable_sidebar:
    gb.configure_side_bar('filters')

if enable_selection:
    gb.configure_selection(selection_mode)
    if use_checkbox:
        gb.configure_selection(selection_mode, use_checkbox=True, groupSelectsChildren=groupSelectsChildren, groupSelectsFiltered=groupSelectsFiltered)
    if ((selection_mode == 'multiple') & (not use_checkbox)):
        gb.configure_selection(selection_mode, use_checkbox=False, rowMultiSelectWithClick=rowMultiSelectWithClick, suppressRowDeselection=suppressRowDeselection)

# if enable_pagination:
#     if paginationAutoSize:
#         gb.configure_pagination(paginationAutoPageSize=True)
#     else:
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=paginationPageSize)

gb.configure_grid_options(domLayout='normal')
gridOptions = gb.build()

#Display the grid
#st.header("Portfolio Reallocation Worksheet")
# st.markdown("""
#     AgGrid can handle many types of columns and will try to render the most human readable way.  
#     On editions, grid will fallback to string representation of data, DateTime and TimeDeltas are converted to ISO format.
#     Custom display formating may be applied to numeric fields, but returned data will still be numeric.
# """)
portfolio_select = st.selectbox('Pick a Portfolio',df1['PORTFOLIO'].unique(),key='sb1')
if 'sb1' not in st.session_state:
    st.session_state['sb1'] = '"SnowCap FinTech Portfolio"'
#st.session_state
#st.write(portfolio_select)
df1 = df1[df1['PORTFOLIO']==st.session_state.sb1]
#sum_contrib = df1['ALLOCATION'].sum().round()
#gridOptions['pinnedTopRowData'] = [{'ALLOCATION':sum_contrib, 'TICKER':'TOTAL % ALLOCATED'}]

c1 = st.empty()
with c1.container():

    grid_response = AgGrid(
    df1, 
    gridOptions=gridOptions,
    height=grid_height, 
    width='100%',
    data_return_mode=return_mode_value, 
    update_mode=update_mode_value,
    fit_columns_on_grid_load=fit_columns_on_grid_load,
    allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
    enable_enterprise_modules=enable_enterprise_modules
    )

df = grid_response['data']



selected = grid_response['selected_rows']  

st.metric('Total Allocation % :',np.round(df['ALLOCATION'].sum(),0),delta=None)  
if not selected:
     st.warning('Please select at least one TICKER to change',icon="⚠️")   
     st.stop()


selected_df = pd.DataFrame(selected)   



btn = False  
        

if np.round(df['ALLOCATION'].sum()) != 100:
    st.write('Sum of all allocations must equal 100')
    st.stop()
else:
    
    if selected :
        
            if selected_df.empty:
                st.write(selected_df)
            else:
                selected_df['ALLOCATION'] = pd.to_numeric(selected_df['ALLOCATION'], errors='ignore')
                df2 = df1.merge(selected_df, on=['TICKER'], how='inner')
                df1ind = df1.set_index('TICKER')
                df1ind.update(selected_df.set_index('TICKER'))
                placeholder = st.empty()
                #df2['ALLOCATION_x'] = pd.to_numeric(df2['ALLOCATION_x'], errors='ignore') 
                #df2['ALLOCATION_y'] = pd.to_numeric(df2['ALLOCATION_y'], errors='ignore')
                df2.rename(columns = {'ALLOCATION_x':'OLD ALLOCATION','ALLOCATION_y':'NEW ALLOCATION'}, inplace = True)
                with placeholder.container():    
                    if not df2['OLD ALLOCATION'].equals(df2["NEW ALLOCATION"]): 
                        st.write("New Allocations")
                    #st.write(selected_df[['TICKER','ALLOCATION']])
                        AgGrid(df2[['TICKER','OLD ALLOCATION','NEW ALLOCATION']], width=200, height=100 )
                        btn = st.button("Confirm New Allocations")
    if btn:
        placeholder.empty()
        c1.empty()
        with c1.container():
            AgGrid(
    df1ind.reset_index(), 
    gridOptions=gridOptions,
    height=grid_height, 
    width='100%',
    data_return_mode=return_mode_value, 
    update_mode=update_mode_value,
    fit_columns_on_grid_load=fit_columns_on_grid_load,
    allow_unsafe_jscode=True, #Set it to True to allow jsfunction to be injected
    enable_enterprise_modules=enable_enterprise_modules, key='one'
    )
            st.success('Portfolio Successfully Updated!', icon ='✅')
   
#if __name__ == "__main__":
#    st.set_page_config(
#        "SnowCap ESG Worksheet",
#        "📊",
#        initial_sidebar_state="expanded",
#        layout="wide",
#    )
#    main()
            
 