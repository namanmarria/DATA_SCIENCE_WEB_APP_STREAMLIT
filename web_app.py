import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

# load the data set
DATA_URL ='D:/SANSAD_IYC/MEDIA_ANALYSIS/DS_ANALYSIS/COURSERA_GUIDED_PROJECTS/WEB_APP/Motor_Vehicle_Collisions_-_Crashes.csv'

# add title to the web Application
st.title('Motor Vehicle Collisions in New York City')
st.markdown('This is a streamlit dashboard application that can be used \n to analyse motor vehicle collisions in NYC')


# function to load the data and perform computations
# using st.cache because we don't want to rerun this computation again and again
@st.cache_data(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows,parse_dates=[['CRASH_DATE','CRASH_TIME']])
    data.dropna(subset=['LATITUDE','LONGITUDE'], inplace=True)
    # create a lowercase lambda function
    lowercase = lambda x:str(x).lower()
    data.rename(lowercase,axis=1, inplace=True)
    data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True)
    return data

data =load_data(100000)
# making copy of data
original_data =data

st.header("Where are the most people injured in NYC ?")
# add slider to make it interactive
injured_people = st.slider("Number of persons injured in vehicle collisions.",0,19)
# filtering data using query
# plots the map compares column with variable along inputs lat and long : dropping null values as well
st.map(data.query("injured_persons >= @injured_people")[['latitude', 'longitude']].dropna(how='any'))


#new header
st.header("How many collisions occured during a given time of day ?")
# add a drop down
hour = st.selectbox("Hour to look at ", range(0,24),1)
# subset our data on basis of hour slider
data = data[data['date/time'].dt.hour == hour]

# markdown 
st.markdown("Vehicle Collisions between %i:00 and %i:00" % (hour,(hour+1) % 24 ))

# coordinates for new york city
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

#create a pydeck figure
st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",
    initial_view_state = {'latitude':midpoint[0],'longitude':midpoint[1],'zoom':1,'pitch':50},
    layers = [
        pdk.Layer(
            "HexagonLayer",
            data = data[['date/time','latitude','longitude']],
            get_position = ['longitude','latitude'],
            # add few more arguments such as radius = 100m
            radius=100,
            extruded = True,
            pickable = True,
            elevation_scale =4,
            elevation_range = [0,1000],
        ),
    ],
))

# break down of collision by 
st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour,(hour+1)%24))
#create new df caled filter
filtered = data[
    (data['date/time'].dt.hour>=hour) & (data['date/time'].dt.hour <= (hour+1))

]
# create histogram using this data and we get daata entry at 0 index
hist =np.histogram(filtered['date/time'].dt.minute, bins=60,range=(0,60))[0]
chart_data=pd.DataFrame({'Minute':range(60),'Crashes':hist})
fig = px.bar(chart_data, x= 'Minute',y='Crashes',hover_data = ['Minute','Crashes'],height=400)
st.write(fig)


# select data using histogram
st.header("Top 5 dangerous streets by affected type")
select = st.selectbox('Affected type of people',['Pedestrians','Cyclists','Motorists'])

# if select is particular then check that particular type in df sort them and give the top 5 
# using copy of data 
if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[['on_street_name',"injured_pedestrians"]].sort_values(by=['injured_pedestrians'],ascending = False).dropna(how='any'))[:5]

elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[['on_street_name',"injured_cyclists"]].sort_values(by=['injured_cyclists'],ascending = False).dropna(how='any'))[:5]

elif select == 'Motorists':
    st.write(original_data.query("injured_motorists >= 1")[['on_street_name',"injured_motorists"]].sort_values(by=['injured_motorists'],ascending = False).dropna(how='any'))[:5]


# to hide the data with a check box
if st.checkbox("Show Raw Data",False):
    st.subheader('Raw Data')
    st.write(data)

    