import streamlit as st
import pandas as pd 
import numpy as np 
import pydeck as pdk
import plotly.graph_objects as go
import plotly.express as px

## Datasets

crime = pd.read_csv('data/crime_cleaned.csv')
victim_donut_data = pd.read_csv('data/victims_donut_data.csv', index_col = 0)
pop_area_count = pd.read_csv('data/pop_area_count.csv', index_col = 0)
crime_bar = pd.read_csv('data/la_crime_data.csv')
crime_type = pd.read_csv('data/crime_type.csv', index_col = 0)
crimeAreaDF = pd.read_csv('data/crimeDate_crimeTypes.csv', index_col = 0)
pop_data = pd.read_csv('data/Population_HV.csv')

crime_type['Date'] = pd.to_datetime(crime_type.Date)
## Functions

size_fr = 150
size_tr = 200

def map(data, lat, lon, zoom):
    st.write(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": lat,
            "longitude": lon,
            "zoom": zoom,
            "pitch": 50,
        },
        layers=[
            pdk.Layer(
                "HeatmapLayer", # HexagonLayer ScatterplotLayer HeatmapLayer
            
                data=data,
                get_position=["LON", "LAT"],
                # radius=100,
                # auto_highlight=True,
                # get_radius=100,          # Radius is given in meters
                # get_fill_color=[180, 0, 200, 140],
                pickable=True,
                opacity=0.5,
                # extruded=True,
                # coverage = 1
            ),
        ]
    ))

def ring(selected):
    data = victim_donut_data[victim_donut_data['AREA NAME'] == selected]
    labels = data['Vict Descent written']
    values = data['Count']

    layout =dict(#title=dict(text=selected),
                 legend = dict(orientation = 'h',
                                y = -0.15))

    # Use `hole` to create a donut-like pie chart
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6)], layout=layout)
    fig.update_layout(autosize=False, width=400, height=400)
    return fig

def bar_chart(selected):
    data = pop_area_count.loc[[selected,'Total Los Angeles'],['Population (approx.)', 'Avg. yearly crime count']]
    data['Avg. number of reported crimes per inhabitants per year'] = data['Avg. yearly crime count'] / data['Population (approx.)']
    data = data.reset_index()
    data = data.rename(columns={'Area name':'Area'})
    title = selected
    fig = px.bar(data, x='Area', y='Avg. number of reported crimes per inhabitants per year')#, title=title)
    return fig

def most_affected_area(data, year):
    # Apply the year filter
    data_selection = data[data['Year'] == year]
    
    # Define variables
    most_affected_area = data_selection.groupby('Area Name').count().sort_values('Year', ascending = False).index[0]
    crimes_occured_most = data_selection.groupby('Area Name').count().sort_values('Year', ascending = False)['Year'][0]
    # Plot it
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode = "number",
        value = crimes_occured_most,
        number={"font":{"size":40}},
        title = {"text": f"Area with the highest number<br>of crimes in {year_selected}<br><br><span style='font-size:1.8em;color:gray'>{most_affected_area}</span>"}
    ))
    fig.update_layout(autosize=False, width=size_fr, height=size_fr)
    
    return fig        

def crimes_occured_delta(data, year):
    # Define the variables
    crimes_occur_selected = len(data[(data['Year'] == year)])
    crimes_occur_bf_selected = len(data[(data['Year'] == year-1)])
    
    # Plot it
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = crimes_occur_selected,
        number={"font":{"size":40}}
        ))


    fig.update_layout(
        template = {'data' : {'indicator': [{
            'title': {'text': f"Number of Occured Crimes in {year}<br>compared to previuos year"},
            'delta' : {'reference': crimes_occur_bf_selected,
                      'decreasing.color' : 'green',
                      'increasing.color' : 'red'}}]
                             }})
    fig.update_layout(autosize=False, width=size_fr, height=size_fr)
    
    return fig

def least_affected_area(data, year):
      # Apply the year filter
    data_selection = data[data['Year'] == year]
    
    # Define dataframe for this plot
    
    
    # Define variables
    most_affected_area = data_selection.groupby('Area Name').count().sort_values('Year', ascending = False).index[-1]
    crimes_occured_most = data_selection.groupby('Area Name').count().sort_values('Year', ascending = False)['Year'][-1]
    # Plot it
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode = "number",
        value = crimes_occured_most,
        number={"font":{"size":40}},
        title = {"text": f"Area with the lowest number<br>of crimes in {year_selected}<br><br><span style='font-size:1.8em;color:gray'>{most_affected_area}</span>"}
    ))
    fig.update_layout(autosize=False, width=size_fr, height=size_fr)
    
    return fig  

def most_affected_year(data, area):     
      # Apply the year filter
    data_selection = data[data['Area Name'] == area]

    # Define variables
    most_affected_year = data_selection.groupby('Year').count().sort_values('Area Name', ascending = False).index[0]
    crimes_occured_most_year = data_selection.groupby('Year').count().sort_values('Area Name', ascending = False).iloc[0]['Area Name']
    
    # Plot it
    import plotly.graph_objects as go
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode = "number",
        value = int(crimes_occured_most_year),
        number={"font":{"size":40}},
        title = {"text": f"Year with highest number<br> of crimes in {area_selected}<br><br><span style='font-size:1.8em;color:gray'>{most_affected_year}</span>"}
        ))
    
    fig.update_layout(autosize=False, width=size_tr, height=size_tr)
    return fig

def population_percentage(data, area):
    # Get the numeric value of population
    selected_area_popu = data[data['Area name']==area].iloc[0, 1]
    
    # Get the corresponding percentage
    selected_area_percent_popu = data[data['Area name']==area].iloc[0, -1]
    
    # Plot it
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode = "number",
        value = int(selected_area_popu),
        number={"font":{"size":40}},
        domain = {'row': 0, 'column': 1},
        title = {"text": f"{area} population compared to<br>total Los Angeles population <br><br><span style='font-size:1.8em;color:gray'>{selected_area_percent_popu}</span><br>"}
        ))
    
    fig.update_layout(autosize=False, width=size_tr, height=size_tr)

    return fig

def barchart(year):
    
    crime_sel = crime_type.groupby('Year').sum().query('Year == @year').T
    
    data = dict(type='bar', x= crime_sel[year].sort_values(), y=crime_sel.index, orientation = 'h')
    layout = dict( xaxis = dict(title = 'Count'))#, yaxis=dict(ticklabelposition = "inside right"))
    
    fig = go.Figure(data=data, layout=layout)

    fig.update_layout(dict(yaxis = dict(ticklabelposition = "inside right")))
    
    fig.update_layout(autosize=False, width=2000, height=400)

    return fig

def crime_line(year, area):
    
    crime_type_Area = crime_type.query('Area == @area and Date.dt.year == @year')
    # crime_type_Area = crime_type_Area[crime_type_Area['Date'].str.contains(year)]
    crimes_list = ['Agravated assault', 'Burglary','Burglary from vehicle', 'Intimate partner assault', 'Simple assault',
                   'Small theft (under 950$)', 'Stolen vehicle', 'Teft of identity','Vandalism (felony)', 
                   'Vandalism (misdeameanor)']
    crimes_to_hide = ['Agravated assault', 'Intimate partner assault', 'Teft of identity', 'Vandalism (felony)', 'Vandalism (misdeameanor)']
    
    data = [dict(type = 'scatter',
                x = crime_type_Area['Date'],
                y = crime_type_Area[crime],
                name=crime)for crime in crimes_list]
    for d in data:
        if d.get('name') in crimes_to_hide:
            d['visible'] = 'legendonly'    

    layout = dict(yaxis = dict(title = 'Count'), xaxis = dict(title = 'Date'))
    fig = go.Figure(data=data, layout=layout)
    return fig

## Layout

st.title('Crime in Los Angeles')
st.subheader('Interactive visual analysis of Los Angeles crimes from 2010 though 2019.')

st.write('')
st.write('')
st.write('')

## Sidebar

year_selected= st.slider("Select a year", min(crime.Year), max(crime.Year))
crime = crime.query("Year == @year_selected")

## First Row

left1, middle1, right1 = st.beta_columns((0.3,0.3,0.3))

la_area = least_affected_area(crime_bar, year_selected)
ma_area = most_affected_area(crime_bar, year_selected)
co_delta = crimes_occured_delta(crime_bar, year_selected)

with left1:
    st.plotly_chart(la_area, use_container_width= True)

with middle1:
    st.plotly_chart(ma_area, use_container_width= True)

with right1:
    st.plotly_chart(co_delta, use_container_width= True)

## Second Row

left2, spacer, right2 = st.beta_columns((1, 0.1, 1.2))

midpoint = (np.average(crime["LAT"]), np.average(crime["LON"]))
barchart = barchart(year_selected)
# with left2:

st.header("Map of Los Angeles crimes in %i." % (year_selected))
st.write('')
map(crime, midpoint[0], midpoint[1], 8.5)

# with right2:
st.header("Top 10 most occurent crime types in %i." % (year_selected))
st.plotly_chart(barchart, use_container_width = True)
    
# Expander Selector

areas = ['Newton',
 'Pacific',
 'Hollywood',
 'Central',
 'Northeast',
 'Hollenbeck',
 'Southwest',
 'Southeast',
 'Rampart',
 'Olympic',
 'Wilshire',
 '77th Street',
 'Harbor',
 'West LA',
 'Van Nuys',
 'West Valley',
 'Mission',
 'Topanga',
 'N Hollywood',
 'Foothill',
 'Devonshire']
expander = st.beta_expander('Select a Neighborhood')
area_selected= expander.selectbox('', areas)

st.write('')
st.write('')
st.write('')

## Third row

left3, right3 = st.beta_columns((1, 1))

ma_year = most_affected_year(crime_bar, area_selected)
pop_perc = population_percentage(pop_data, area_selected)
with left3:
    st.plotly_chart(ma_year, use_container_width = True)
    # st.plotly_chart(pop_perc, use_container_width = True)
with right3:
    st.plotly_chart(pop_perc, use_container_width = True)

lc = crime_line(year_selected, area_selected)
# with right3:
st.header(f'Top 10 most occured crime types in {area_selected} and their evolution through {year_selected}.')
st.plotly_chart(lc, use_container_width = True)

## Fourth Row 
left4, spacer, right4 = st.beta_columns((1, 0.1, 1))

ring = ring(area_selected)
bar = bar_chart(area_selected)

with left4:
    
    st.write(f'Crime rate in {area_selected} compared to the Los Angeles average.')
    st.plotly_chart(bar, use_container_width= True)
    

with right4:
    
    st.write(f'Ethnicity distribution of the crime victims in {area_selected}.')
    st.plotly_chart(ring, use_container_width = True)
    