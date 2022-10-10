import functools
from pathlib import Path

import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.shared import JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objs as go

import snowflake.connector
import streamlit_wordcloud as wc
import random


from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL
from wordcloud import WordCloud
from wordcloud import ImageColorGenerator
from wordcloud import STOPWORDS




chart = functools.partial(st.plotly_chart, use_container_width=True)    
COMMON_ARGS = {
    "color": "ticker",
    "color_discrete_sequence": px.colors.sequential.Blues,
    "hover_data": [
        "portfolio",
        "internal_esg_score",
        "materiality_adj_insight", 
        "materiality_esg_rank", 
        "all_categories_adj_insight",
        "all_categories_esg_rank",
    ],
}

chart1 = functools.partial(st.plotly_chart, use_container_width=True) 



@st.experimental_memo

def filter_data(
    df1: pd.DataFrame, account_selections: list[str], symbol_selections: list[str]
) -> pd.DataFrame:
    
    df1 = df1.copy()
    df1 = df1[
        df1.portfolio.isin(account_selections) & df1.ticker.isin(symbol_selections)
    ]

    return df1


def main() -> None:
    st.header("SnowCap ESG Portfolio Performance Review :snowflake:")
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
        df1 = pd.read_sql_query("SELECT a.portfolio, a.ticker, security_name,  max(internal_esg_score) internal_esg_score,\
            materiality_adj_insight,materiality_esg_rank, all_categories_adj_insight,all_categories_esg_rank,price, round(market_cap) market_cap,\
            round(total_shares*price) portfolio_value,round(change_in_shares*price) portfolio_value_change\
              FROM DAILY_PORTFOLIO_DETAIL_V a,\
            (select ticker,max(date) date from daily_portfolio_detail_v group by ticker) b\
            where a.ticker=b.ticker and a.date=b.date\
            group by a.portfolio, a.ticker, security_name, price, market_cap,\
            materiality_adj_insight,materiality_esg_rank, all_categories_adj_insight,all_categories_esg_rank,\
            portfolio_value, portfolio_value_change;", engine)
        df2 = pd.read_sql_query("select ticker,date, price, max(internal_esg_score) internal_esg_score,\
         materiality_adj_insight, all_categories_adj_insight, materiality_esg_rank, all_categories_esg_rank\
        from daily_portfolio_detail_v\
        where date >='2019-12-31'\
        group by ticker,date, price,materiality_adj_insight, all_categories_adj_insight, materiality_esg_rank, all_categories_esg_rank\
        order by date;", engine)
        word_df = pd.read_sql_query("select entity,array_agg(contact) WITHIN GROUP (ORDER BY entity ASC) sentiment \
            from (SELECT entity_ticker as entity,\
        f.value AS contact\
        FROM frostbyte_esg.analytics.russell3000_10k_esg_v p,\
        lateral flatten(input => p.event_hits) f)\
        group by entity;", engine)

        df3 = pd.read_sql_query("SELECT dpd.date,dpd.portfolio,ROUND(SUM(dpd.total_shares * dpd.price)) AS market_value\
        FROM frostbyte_esg.analytics.daily_portfolio_detail_v dpd WHERE  dpd.date >= '2019-01-01' \
        GROUP BY dpd.date, dpd.portfolio ORDER BY dpd.date DESC, dpd.portfolio;",engine)

        #word_cnt = pd.read_sql_query("select id,contact,count(contact) cnt from (\
        #SELECT entity_ticker as id,\
        #f.value AS contact\
        #FROM frostbyte_esg.analytics.russell3000_10k_esg_v p,\
        #lateral flatten(input => p.event_hits) f)\
        #group by id, contact\
        #order by id",engine)
        #word_cnt.columns=['color','text','values']


    
    finally:
        connection.close()
        engine.dispose()
    
    #with st.expander("How to Use This"):
    #    st.write(Path("README.md").read_text())

    #st.subheader("Upload your CSV from Fidelity")
    #uploaded_data = st.file_uploader(
    #    "Drag and Drop or Click to Upload", type=".csv", accept_multiple_files=False
    #)

    #if uploaded_data is None:
    #   st.info("Using example data. Upload a file above to use your own data!")
    #uploaded_data = open("example.csv", "r")
    #else:
    #    st.success("Uploaded your file!")

    #df = pd.read_csv(uploaded_data)
    #with st.expander("Raw Dataframe"):
    #    st.write(df)

    #df = clean_data(df)
    #with st.expander("Cleaned Data"):
    #st.write(df)

    

    def handle_click(new_selection):
        st.session_state['ticker_select']= new_selction
    
    st.sidebar.subheader("Filter Displayed Portfolios")

    accounts = list(df1.portfolio.unique())
    account_selections = st.sidebar.multiselect(
        #"Select Portfolios to View", options=accounts, default = accounts
        "Select Portfolios to View", options=accounts, default = ["SnowCap Next Generation Portfolio","SnowCap Robotics Portfolio", "SnowCap FinTech Portfolio"]
    )

    
    st.sidebar.subheader("Filter Displayed Tickers")

    symbols = list(df1.loc[df1.portfolio.isin(account_selections), "ticker"].unique())
    if 'ticker_select' not in st.session_state:
        st.session_state['ticker_select'] = ["GOOG","SNOW","TSLA","SQ","NKE"]+random.sample(symbols,5)
    #st.write(st.session_state['ticker_select'])
    symbol_selections = st.sidebar.multiselect(

        "Select Ticker Symbols to View", options=symbols,default= st.session_state['ticker_select'],
        key = 'ticker_select'
    )
    
    
    
    df1 = filter_data(df1, account_selections, symbol_selections)
    #df2 = filter_data(df2,  symbol_selections)
    
    df2 = df2[df2.ticker.isin(symbol_selections)]

    word_df =  word_df[word_df.entity.isin(symbol_selections)]


    
    

    
       
    def draw_line_portfolio() -> None:
        fig = px.line(data_frame=df3, x='date',y='market_value', 
            color='portfolio')
        fig.update_layout(xaxis={"categoryorder": "total descending", "showgrid":False},yaxis={"title_text":"Market Value of Portfolio","showgrid":False},
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        chart(fig)
    st.subheader("Overall Portfolio Performance Trend")
    draw_line_portfolio()
   
    st.subheader("Latest Internal and Benchmark ESG Data by Ticker")
    cellsytle_jscode = JsCode(
        """
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
    """
    )

    gb = GridOptionsBuilder.from_dataframe(df1)
    gb.configure_columns(
        (
            
            
            "materiality_esg_rank",
            "all_categories_esg_rank",
            
        
        ),
        cellStyle=cellsytle_jscode,
    )
    gb.configure_pagination()
    gb.configure_columns(("portfolio", "ticker"), pinned=True)
    gridOptions = gb.build()

    AgGrid(df1, gridOptions=gridOptions, allow_unsafe_jscode=True)

    def draw_bar(y_val: str) -> None:
        fig = px.bar(df1, y=y_val, x="ticker", **COMMON_ARGS)
        fig.update_layout(barmode="stack", xaxis={"categoryorder": "total descending"},paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        chart(fig)



    

    def draw_line() -> None:
        fig = px.line(data_frame=df2, x='date',y=['materiality_adj_insight','internal_esg_score',"all_categories_adj_insight"], 
            facet_col="ticker")
        fig.update_layout(xaxis={"categoryorder": "total descending"},yaxis={"title_text":"ESG Score"},
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        chart(fig)
    
    def draw_group_bar() -> None:
        fig = go.Figure(data=[go.Bar(name='Int Esg Score', x=df1.ticker, y=df2.internal_esg_score),\
        go.Bar(name='Materiality Adj Score', x=df1.ticker, y=df2.materiality_adj_insight),
        go.Bar(name='All Categories Adj Score', x=df1.ticker, y=df2.all_categories_adj_insight),])
        # Change the bar mode
        fig.update_layout(barmode='group',paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        chart(fig)  

    def draw_multi_line() -> None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x = df2.date,y= df2.internal_esg_score,
                    mode='lines',
                    name='Internal_ISG_Score'))
        fig.add_trace(go.Scatter(x = df2.date,y= df2.materiality_adj_insight,
                    mode='lines+markers',
                    name='Materiality Adj Insight'))
        fig.add_trace(go.Scatter(x = df2.date,y= df2.all_categories_adj_insight,    
                    mode='markers', name='All Categories Adj Insight'))

        chart(fig) 

    account_plural = "s" if len(account_selections) > 1 else ""

    

    st.subheader(f"Value of Portfolio{account_plural} for selected Tickers")
    totals = df1.groupby("portfolio", as_index=False).sum()
    if len(account_selections) > 1:
        st.metric(
            "Total of All Portfolios",
            f"${totals.portfolio_value.sum()/1000000:.2f} M",
            f"{totals.portfolio_value_change.sum():.2f}",
        )
    for column, row in zip(st.columns(len(totals)), totals.itertuples()):
        column.metric(
            row.portfolio,
            f"${row.portfolio_value/1000000:.2f} M",
            f"{row.portfolio_value_change:.2f}",
        )

    fig = px.bar(
        totals,
        y="portfolio",
        x="portfolio_value",
        color="portfolio",
        color_discrete_sequence=px.colors.sequential.Blues,
    )
    fig.update_layout(barmode="stack", xaxis={"categoryorder": "total descending"},paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    chart(fig)

    

    st.sidebar.subheader('Add Charts')
    
    tvap = st.sidebar.checkbox('Ticker Value Across Portfolio')
    if tvap:
        st.subheader("Total Value of each Ticker across portfolios")
        draw_bar("portfolio_value")

    tpp = st.sidebar.checkbox('Ticker Value per Portfolio')
    if tpp:
        
        st.subheader("Value of each Ticker per Portfolio")
        fig = px.sunburst(
        df1, path=["portfolio", "ticker"], values="portfolio_value", **COMMON_ARGS
        )
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        chart(fig)


    
    ett = st.sidebar.checkbox('ESG Score Trend by Ticker',True)
    if ett:
        st.subheader("ESG Score Trend by Ticker")
        draw_line()
   
    ecib = st.sidebar.checkbox('ESG Score Internal vs Benchmark',True)

    if ecib:
        st.subheader("ESG Score Comparison - Internal vs Benchmark")
        draw_group_bar()

    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.subheader("ESG Sentiment Word Cloud")
    stopwords = set(STOPWORDS)
    stopwords.update(["intellectual","property"])
    for index,row in word_df.iterrows():
        
        wordcloud = WordCloud(stopwords=stopwords,background_color="white", width=800, height=400).generate(row[1])
        
        plt.figure( figsize=(20,20))
        plt.tight_layout(pad=0)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        st.write(row[0])
        st.pyplot()
    
    #return_obj = wc.visualize(word_cnt_list, per_word_coloring=False)

if __name__ == "__main__":
    st.set_page_config(
        "SnowCap ESG",
        "📊",
        initial_sidebar_state="expanded",
        layout="wide",
    )
    main()

