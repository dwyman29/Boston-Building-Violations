# Building Violations Final Project

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk


# Reading the data into a DataFrame/cleaning dataset of null values/cells
file_path = "Final Project Building Violations/boston_building_violations_7000_sample.csv"
dfBuildingViolations = pd.read_csv(file_path, index_col="case_no")


csv_columns = ["status_dttm", "status", "code", "description", "violation_stno", "violation_street", "violation_suffix", "violation_city", "violation_state", "violation_zip", "ward", "contact_addr1", "contact_city", "contact_state", "contact_zip", "sam_id", "latitude", "longitude", "location"]

dfBuildingViolations = dfBuildingViolations.dropna(subset=csv_columns)


# Function for creating and plotting map of all building violations with streamlit
def longitude_latitude():
    st.header("Building Violations in Boston and Surrounding Cities")
    columns = ["description", "violation_street", "violation_suffix", "violation_city", "violation_zip",
               "violation_state", "latitude", "longitude", "status","danger_level"]  # Columns needed
    dfMap = dfBuildingViolations.loc[:, columns]  # Creating the map columns
    dfMap = dfMap.dropna(subset=columns)  # Cleaning null values in dataframe

# Formatting the violations map
    view_BuildingViolations = pdk.ViewState(
        latitude=dfMap["latitude"].mean(),
        longitude=dfMap["longitude"].mean(),
        zoom=10.5,
        pitch=0
    )

    # Plotting marks on violations map
    layer = pdk.Layer("ScatterplotLayer",
        data=dfMap,
        get_position="[longitude, latitude]",
        get_radius=20,
        auto_highlight=True,
        get_color=[0, 0, 255],
        pickable=True
    )

    # Description for violations on map
    tool_tip = {"html":
                    "Building Street: <b>{violation_street}, {violation_suffix}</b></br>"
                    "Building City: <b>{violation_city}</b></br>"
                    "Building Zip: <b>{violation_zip}</b></br>"
                    "Violation Description: <b>{description}</b></br>"
                    "Status: <b>{status}</b></br>"
                    "Danger Level: <b>{danger_level}</b></br>",
                    "style": {"backgroundColor": "green", "color": "white"}
                }

    # Creating violations map
    violationsMap = pdk.Deck(
        map_style="road",
        initial_view_state =view_BuildingViolations,
        layers = layer,
        tooltip = tool_tip
    )

    # Plotting map with streamlit
    st.pydeck_chart(violationsMap)

# Create filter for dataframe that allows user to filter violations by city name
def cities(df, column):
    cities = []
    for _, row in df.iterrows():
        if row[column].capitalize() not in cities:
            cities.append(row[column].capitalize())
    return cities

# Filtering dataframe by city and plotting pie chart of dangerous violations by city
def filterByCity(cities):
    # Creating dropdown with city names
    city = st.selectbox(
        'Building Violations by City:',
        cities)
    st.write('Building Violations in', city + ":")

    # Locating rows for specified city
    dfCity = dfBuildingViolations.loc[:, ["status", "description", "danger_level", "violation_street", "violation_suffix", "violation_city", "violation_state", "violation_zip", "contact_addr1", "contact_city", "contact_state", "contact_zip"]]
    dfCity = dfCity.loc[dfCity["violation_city"] == city]
    st.dataframe(dfCity) # Writing to dataframe
def pieChart(df):
    dangerLevelCounts = df[df["danger_level"] == "Red"].groupby("violation_city").size().reset_index(name="count")  # Count rows per city with danger level "Red"

    max_value = dangerLevelCounts["count"].max()

    # Find the index of the row with the highest number of "Red" danger level
    index_of_max_val = dangerLevelCounts.index[dangerLevelCounts["count"] == max_value][0]

    # Set explode to 0.2 for the violation city with the most "Red" danger level
    explode = [0] * dangerLevelCounts.shape[0]
    explode[index_of_max_val] = 0.2

    # Making pie chart using matplotlib.pyplot
    fig, ax = plt.subplots()
    ax.pie(dangerLevelCounts["count"], labels=dangerLevelCounts["violation_city"], labeldistance=1.1, autopct="%1.0f%%", pctdistance=0.75, startangle=90, explode=explode)
    ax.axis("equal")  # equal aspect ratio ensures that the pie chart is circular

    # Plot in streamlit
    st.pyplot(fig)

# Creating bar chart to plot total violations per city
def violations_by_city(df):
    # Group by violation city and count the number of violations
    dfCityViolations = df.groupby("violation_city").size().reset_index(name="count")

    # Sorting the bar chart
    dfCityViolations = dfCityViolations.sort_values(by="count", ascending=False)

    # Plotting the bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    dfCityViolations.plot(x="violation_city", y="count", kind="bar", ax=ax, legend=False, color="Red")

    # Set labels and title
    ax.set_xlabel("City")
    ax.set_ylabel("Count of Building Violations")
    ax.set_title("Bar Chart of Total Building Violations by City")

    # Display the bar chart in Streamlit
    st.pyplot(fig)

def main():
    # List to hold danger level
    violation_lvl = []
    # List of keywords that categorize danger level
    dangerous_keywords = ["Unsafe and Dangerous", "Unsafe Structures", "Fire Protection Systems",
                          "Emergency Escape & Rescue", "Unsafe Structure", "Fire Alarm Systems",
                          "Emergency Escape and Rescue Op", "Smoke Detectors", "Carbon Monoxide Detectors",
                          "Prohibited Locations", "Unsafe Building & Structures"]
    # Adding new categorization of danger level to building violation types.
    for _, row in dfBuildingViolations.iterrows():
        description = row.description
        if description in dangerous_keywords:
            violation_lvl.append("Red")
        else:
            violation_lvl.append("Green")

    dfBuildingViolations["danger_level"] = violation_lvl

    print(dfBuildingViolations)
    longitude_latitude()
    filterByCity(cities(dfBuildingViolations,"violation_city"))
    pieChart(dfBuildingViolations)

    # Plotting violation count bar chart in Streamlit
    violations_by_city(dfBuildingViolations)
main()

