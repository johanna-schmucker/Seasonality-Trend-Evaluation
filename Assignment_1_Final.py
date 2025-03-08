#necessary imports
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import time

#set the app title and the business question
st.title("Passenger Travel Trends: Seasonality Trend Evaluation & Air Transport Growth Analysis")
st.write("Question: Is the Aviation Business continuously growing and impacted by Seasonality?")

#Google Sheets link (data)
try:
    google_sheet_url = st.secrets["gsheets"]["public_gsheet_url"]
    #st.write("Using Google Sheets CSV URL:", google_sheet_url)
    #df = pd.read_csv(google_sheet_url)
    #st.write("loaded data!")
    #st.dataframe(df.head())
except KeyError:
    st.error("️Google Sheets URL not found in Streamlit secrets! Please add it to `.streamlit/secrets.toml` locally or in Streamlit Cloud.")
    st.stop()

#load dataset and refresh every 60 seconds
@st.cache_data(ttl = 600)
def load_data():
    return pd.read_csv(google_sheet_url)
data = load_data()

#dictionary containing the grouping of months into seasons
month_seasons = {
    "Winter": ["December", "January", "February"],
    "Spring": ["March", "April", "May"],
    "Summer": ["June", "July", "August"],
    "Autumn": ["September", "October", "November"]
}

#function to map months to seasons
def assign_season(month):
    for season, months in month_seasons.items():
        #checks if a given month is in the dictionary of months/seasons
        if month in months:
            return season
     #if the month is not in the dictionary, then return none   
    return "Unknown"

#apply the function to create a new 'Season' column in the existing dataframe
data["Season"] = data["month"].apply(assign_season)

#convert month to categorical for correct ordering
month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
data["month"] = pd.Categorical(data["month"], categories = month_order, ordered = True)


#LINE PLOT (figure A): Growth Trend + Seasonality Together
figure_A, axes = plt.subplots(figsize = (12, 6))

#filter for selected years
selected_years = [1950, 1955, 1960]
filtered_data = data[data["year"].isin(selected_years)]

#plotting
sns.lineplot(x = "month", y = "passengers", hue = "year", data = filtered_data, marker = "o", palette = "coolwarm", ax = axes)
axes.set_title("Passenger Growth & Seasonal Fluctuations (1950, 1955, 1960)", fontsize = 14)
axes.set_xlabel("Month", fontsize = 12)
axes.set_ylabel("Passenger Count", fontsize = 12)
axes.legend(title = "Year", bbox_to_anchor = (1.05, 1), loc = "upper left")
axes.grid(True, linestyle = "--", alpha = 0.5)


#BOX PLOT: Seasonality Over Years
figure_B, axes = plt.subplots(figsize = (12, 6))

#all years faintly in the background
sns.violinplot(x = "Season", y = "passengers", data = data, palette = "Blues", inner = None, ax = axes, alpha = 0.3)
#overlay the key years with box plots
sns.boxplot(x = "Season", y = "passengers", hue = "year", data = filtered_data, palette = "coolwarm", ax = axes)
axes.set_title("Seasonal Passenger Density & Variability", fontsize = 14)
axes.set_xlabel("Season", fontsize = 12)
axes.set_ylabel("Passenger Count", fontsize = 12)
axes.legend(title = "Year", bbox_to_anchor = (1.05, 1), loc = "upper left")


#SESSION STATE
#initialize session state variables
if "chart_shown" not in st.session_state:
    #start with plot B
    st.session_state.chart_shown = "B"
if "start_time" not in st.session_state:
    st.session_state.start_time = None
#so the "I answered your question button" is hidden in the beginning"
if "answered_visible" not in st.session_state: 
    st.session_state.answered_visible = False

#button to start the A/B test (switches charts to A or B)
if st.button("Show me a chart"):
    #randomly select one of the two charts
    new_chart = np.random.choice(["A", "B"])
    #ensure it does not repeat the same chart twice in a row
    while new_chart == st.session_state.chart_shown:
        new_chart = np.random.choice(["A", "B"])

    st.session_state.chart_shown = new_chart
    #start timing
    st.session_state.start_time = time.time()
    #makes sure the second button is visible
    st.session_state.answered_visible = True
    st.rerun()

#show the selected chart
if st.session_state.chart_shown:
    st.subheader("Chart Display:")
    if st.session_state.chart_shown == "A":
        st.pyplot(figure_A)
    else:
      st.pyplot(figure_B)

    #after the chart is shown, display a second button to ask the user if they answered the question
    if st.session_state.answered_visible:
        if st.button("I answered your question"):
            #calculate time taken between showing the chart and clicking the button
            time_taken = time.time() - st.session_state.start_time
            st.write(f"You took {time_taken:.2f} seconds to answer the question.")
