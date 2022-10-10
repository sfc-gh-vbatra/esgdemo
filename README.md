
ESG data has been curated by the FROSTBYTE team. Instructions to prepare the data, background, demo video can be found here.
https://github.com/snowflakecorp/frostbytes/tree/main/Industry%20-%20Financial%20Services/Enriching%20Analysis%20with%20ESG
Please make sure you follow the instruction to curate the data. Streamlit ESG app uses the views in the Analytics schema.

You can run the app without needing to maintain it for yourself from the link below, but the recommendation is to learn the Frostbyte ESG data elements, their processing and transformation.

https://sfc-gh-vbatra-esgdemo-esgwelcome-t3zdz1.streamlitapp.com/

<br>
This app is only tested with Python 3.9.12. Please use that version.

### Clone this repository

*git clone https://github.com/sfc-gh-vbatra/esgdemo*

Change your working directory to esgdemo

*cd esgdemo*


### Create your python environment
*conda create --name anyenvname*
<br>
*conda activate anyenvname*
<br>
*conda install python=3.9.12*

### Install dependencies

*pip install -r requirements.txt*


### Rename the secrets.toml and update account information
<br>
Rename .streamlit/secrets.toml.generic to .streamlt/secrets.toml and enter your account's credentials. Generic toml file has template role, database and schema. Make sure you are using role DATA_ENGINEER_ESG or a role that has read access to views in Analytics schema

### Running the demo
*streamlit run esg.py*

