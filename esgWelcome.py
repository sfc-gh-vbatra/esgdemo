import streamlit as st
def run():
    st.set_page_config(
        page_title="SnowCap ESG",
        page_icon="📊",
    )

    st.write("# Welcome to Snowflake ESG Demo!")
    #st.image('https://user-images.githubusercontent.com/68337675/175331008-930f9346-c4f0-4d1f-9793-ce3216215281.png')
  

    

    st.subheader('Business Value:')

    st.write('With Snowflake as the single source of truth, organizations are able to harmonize internal system data with external 3rd party data sources directly from the Snowflake Marketplace. With native support for semi-structured data, Data Engineers are able to simplify JSON pipelines and flatten object data at runtime with analytical views.')

    st.subheader('Technical Value:')

    st.write('Receiving Data from the Snowflake Marketplace from your existing vendors simplifies ingestion pipelines for your Data Engineers. On top of this, native support for Semi-Structured Data like JSON or XML streamlines data transformations allowing for your teams to focus on more value added tasks.')
    st.subheader('Data Flow:')

    st.image('https://user-images.githubusercontent.com/68337675/163210701-d4e4d6fb-af58-471c-bbb3-88470f2def3d.png')
        
    
    

    
if __name__ == "__main__":
    run()
