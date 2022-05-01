### Stream lit main

import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np
import chart_studio.plotly as py
import plotly.offline as po
import plotly.graph_objs as pg
import matplotlib.pyplot as plt
import plotly.express as px



st.title("Climate Change Dashboard: Global Impact")
st.title("Anandi Gupta")

"""
Anything written in docstrings like this will show up in our app.\n
"""

### Set url names

#URLs - IMF API
#Surface temp
url1 = "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Indicator_3_1_Climate_Indicators_Annual_Mean_Global_Surface_Temperature/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json"

#Climate related disasters
url2b = "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Indicator_11_1_Physical_Risks_Climate_related_disasters_frequency/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json"
url2 = "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Indicator_11_1_Physical_Risks_Climate_related_disasters_frequency/FeatureServer/0/query?where=1%3D1&outFields=Country,ISO2,ISO3,Indicator,Code,Unit,F2016,F2017,F2018,F2019,F2020,F2021,Source&outSR=4326&f=json"

#inform risk
url3 = "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Indicator_11_3_Physical_Risks__Index_for_Risk_Management/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json"

## URLs - Our world in data
#Emissions
url4 = "https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv"

#URLs - WHO API
#risk of premature death from NCD
url6 = "https://ghoapi.azureedge.net/api/NCDMORT3070"

#Diarrheoa deaths from inadequate water
url7 = "https://ghoapi.azureedge.net/api/WSH_10_WAT"

#Malnutrition - Prevalence of underweight children under 5 years of age   (% weight-for-age <-2 SD) (%)
url8 = "https://ghoapi.azureedge.net/api/NUTRITION_WA_2"


######## Read in data from IMF API
def read_in_imf_api(url):

    r = requests.get(url)
    # 1 Return JSON encoded response (converts JSON to Python dictionary)
    x = r.json()
    # 2 convert to df based on keys
    df = pd.DataFrame.from_dict(r.json()["features"])
    # 3 normalize as output is nested dictionary
    output = pd.json_normalize(df['attributes'])
    #return df
    return output

## load and adjust data
#surface temp data
df_surf_temp = read_in_imf_api(url1)
df_surf_temp['five_year_avg'] = (df_surf_temp.F2016 + df_surf_temp.F2017 + df_surf_temp.F2018 + df_surf_temp.F2019 + df_surf_temp.F2020)/5

#Disaster data
df_disasters = read_in_imf_api(url2)
df_disasters = df_disasters[df_disasters['Indicator'] == "Climate related disasters frequency, Number of Disasters: TOTAL"].reset_index()
df_disasters = df_disasters.replace(np.nan, 0)
df_disasters['five_year_avg'] = (df_disasters.F2016+ df_disasters.F2017 + df_disasters.F2018 + df_disasters.F2019 + df_disasters.F2020)/5

df_disasters_viz = read_in_imf_api(url2b)

if st.checkbox("Global Climate Change Trends", key="section1"):
    st.header("Global Climate Change Trends")
    answer0 = st.selectbox(label="Choose indicator",
    options=("CO2 Emissions", "Surface Temperatures", "Climate Disasters"))

    if answer0 == "CO2 Emissions":
        df_emissions_viz = pd.read_csv(url4)
        df_emissions_viz = df_emissions_viz[df_emissions_viz['country'] == "World"]
        df_emissions_viz = df_emissions_viz[df_emissions_viz['year'] > 1980].reset_index()
        fig = px.bar(df_emissions_viz, x=df_emissions_viz['year'], y=df_emissions_viz['co2'], labels={'co2':'Global CO2 Emissions', "year": "Year"},
                 title='CO2 Emissions Over Time')
        st.plotly_chart(fig, use_container_width=True)

    elif answer0 == "Surface Temperatures":
        df_surf_viz = df_surf_temp[df_surf_temp['Country'] == "World"]
        df_surf_viz = pd.wide_to_long(df_surf_viz, stubnames='F', i=['Indicator'], j='year',
                        sep='', suffix=r'\w+').reset_index()
        df_surf_viz= df_surf_viz.rename(columns = {'F':'Temperature_Change'})
        df_surf_viz = df_surf_viz[df_surf_viz['year'] > 1980]
        fig = px.bar(df_surf_viz, x=df_surf_viz['year'], y=df_surf_viz['Temperature_Change'], labels={'Temperature_Change':'Temperature Change (Degrees Celsius)', "year": "Year"},
                 title='Temperature Changes Over Time (Relative to 1951-1980 Baseline Period)')
        st.plotly_chart(fig, use_container_width=True)

    elif answer0 == "Climate Disasters":
        df_disasters_viz = df_disasters_viz.groupby(['Indicator']).sum().reset_index()
        df_disasters_viz = pd.wide_to_long(df_disasters_viz, stubnames='F', i=['Indicator'], j='year',
                        sep='', suffix=r'\w+').reset_index()
        df_disasters_viz = df_disasters_viz[df_disasters_viz['Indicator'] != "Climate related disasters frequency, Number of Disasters: TOTAL"]
        df_disasters_viz.loc[(df_disasters_viz["Indicator"] == "Climate related disasters frequency, Number of Disasters: Drought"), "disaster_type"] = "Drought"
        df_disasters_viz.loc[(df_disasters_viz["Indicator"] == "Climate related disasters frequency, Number of Disasters: Flood"), "disaster_type"] = "Flood"
        df_disasters_viz.loc[(df_disasters_viz["Indicator"] == "Climate related disasters frequency, Number of Disasters: Extreme temperature"), "disaster_type"] = "Extreme temperature"
        df_disasters_viz.loc[(df_disasters_viz["Indicator"] == "Climate related disasters frequency, Number of Disasters: Landslide"), "disaster_type"] = "Landslide"
        df_disasters_viz.loc[(df_disasters_viz["Indicator"] == "Climate related disasters frequency, Number of Disasters: Storm"), "disaster_type"] = "Storm"
        df_disasters_viz.loc[(df_disasters_viz["Indicator"] == "Climate related disasters frequency, Number of Disasters: Wildfire"), "disaster_type"] = "Wildfire"
        fig = px.bar(df_disasters_viz, x=df_disasters_viz['year'], y=df_disasters_viz['F'], color=df_disasters_viz['disaster_type'], labels={'F':'Number of Disasters', 'year': 'Year', 'disaster_type': 'Type of Disaster'},
                 title='Climate Disasters Over Time', width=900, height=500)
        st.plotly_chart(fig, use_container_width=True)


# st.write(df_surf_temp.head())


# ###### 0b Add styling to the table using pandas Styler object

# st.dataframe(df.style.highlight_max(axis=0,color="orange"))
#
#
# #########  1 Add plots

if st.checkbox("Direct Effects of Climate Change", key="section3"):
    st.header("Direct Effects of Climate Change")

    # "### Select box"
    answer1 = st.selectbox(label="Choose indicator",
    options=("Changes in Surface Temperature (relative to 1951-1980 baseline)", "Climate Disasters"))

    answer2 = st.selectbox(label="Choose time period",
    options=("F2016", "F2017", "F2018", "F2019", "F2020", "five_year_avg"))

    def cc_effects(dataset, var):
        data = dict(type='choropleth',
                locations = dataset['ISO3'],
                z = dataset[var],
                text = dataset['Country'])

        layout = dict(title = answer1,
                  geo = dict(showframe = False,
                           projection = {'type':'robinson'},
                           showlakes = True,
                           lakecolor = 'rgb(0,191,255)'))
        x = pg.Figure(data = [data], layout = layout)
        st.plotly_chart(x, use_container_width=True)

    if answer1 == "Changes in Surface Temperature (relative to 1951-1980 baseline)":
        cc_effects(df_surf_temp, answer2)

    elif answer1 =="Climate Disasters":
        cc_effects(df_disasters, answer2)
#     alt_plot = alt.Chart(wb).mark_circle().encode(x="log_gdp",
#     y="lifeExp",
#     color="continent",
#     tooltip=["year", "country"]).interactive()
#     alt_plot
#
# elif st.checkbox("Show GDP and Life Exp Plot, colored by continent and size by pop", key="plot3"):
#     alt_plot = alt.Chart(wb).mark_circle().encode(x="log_gdp",
#     y="lifeExp",
#     color="continent",
#     size="pop",
#     tooltip=["year", "country"]).interactive()
#     alt_plot



#

#
# # """
# # # #### Import World Bank data from gapminder
# # # """
# from gapminder import gapminder
# wb = gapminder
# #
# # # """
# # # `from gapminder import gapminder`\n
# # # `wb = gapminder`\n
# # # `print(wb)`
# # # """
# #
# st.dataframe(wb)
# #
# import numpy as np
# wb["log_gdp"] = np.log(wb["gdpPercap"])
# #
# import altair as alt
#
# alt_plot = alt.Chart(wb).mark_circle().encode(x="log_gdp",
# y="lifeExp",
# color="continent",
# size="pop",
# tooltip=["year", "country"]).interactive()
#
# st.altair_chart(alt_plot, use_container_width=True)
# #
#
# ############ 2 Maps and data
#
# # """
# # ## Plot data on a map using `st.map()`
# # """
#
# # import numpy as np
#
# map_data = pd.DataFrame(
#     np.random.randn(500, 2) / [50, 50] + [38.90912467404927, -77.07519972156327],
#     columns=['lat', 'lon'])
#
# st.map(map_data)
#
#
# ########## 3 Add interactive slider
#
# # "### Slider"
#
# x = st.slider("x") # as users interact, it changes the state of x variable and renders new state
# st.write(x, "times 10 is", x*10)
#
# ######### 4 Add interactive submission button
#
# # "### Button"
#
# # if st.button("Click to submit"):
# #     st.write("Thank you for your submission. We'll be in touch!")
#
# ######## 5 Add interactive dropdown selection box
#
# "### Select box"
# answer = st.selectbox(label="What is your favorite programming language?",
# options=("R", "SQL", "Python", "Java", "Go", "C++"))
# st.write("Here are some resources for ", answer)
#
# ####### 6 Take user input
#
# # "### User input"
# # st.text_input("What do you like most about analytics?", key="analytics_like")
#
# ####### 7 Show/hide plots
#
# # "### Check box to show or hide plot"
#
# import altair as alt
# from gapminder import gapminder
# import numpy as np
# wb = gapminder
# wb["log_gdp"] = np.log(wb["gdpPercap"])
#
# if st.checkbox("Show GDP and Life Exp Plot"):
#     alt_plot = alt.Chart(wb).mark_circle().encode(x="log_gdp",
#     y="lifeExp",
#     tooltip=["year", "country"]).interactive()
#     alt_plot
#
#
# ####### 8 Build a dashboard of plots ######
#
# # import altair as alt
# # from gapminder import gapminder
# # import numpy as np
# wb = gapminder
# wb["log_gdp"] = np.log(wb["gdpPercap"])
#
# # "### Check box to select among plots"
#
# if st.checkbox("Show GDP and Life Exp Plot", key="plot1"):
#     alt_plot = alt.Chart(wb).mark_circle().encode(x="log_gdp",
#     y="lifeExp",
#     tooltip=["year", "country"]).interactive()
#     alt_plot
#
# elif st.checkbox("Show GDP and Life Exp Plot, colored by continent", key="plot2"):
#     alt_plot = alt.Chart(wb).mark_circle().encode(x="log_gdp",
#     y="lifeExp",
#     color="continent",
#     tooltip=["year", "country"]).interactive()
#     alt_plot
#
# elif st.checkbox("Show GDP and Life Exp Plot, colored by continent and size by pop", key="plot3"):
#     alt_plot = alt.Chart(wb).mark_circle().encode(x="log_gdp",
#     y="lifeExp",
#     color="continent",
#     size="pop",
#     tooltip=["year", "country"]).interactive()
#     alt_plot
