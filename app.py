
import streamlit as st
import pandas as pd
import preprocessor
import helper
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Olympics Analysis",
    page_icon="🏅",
    layout="wide"
)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent

athlete_file = DATA_DIR / "athlete_events.csv"
region_file = DATA_DIR / "noc_regions.csv"

if not athlete_file.exists() or not region_file.exists():
    st.error(
        "Dataset files are missing. Please place "
        "athlete_events.csv and noc_regions.csv "
        "in the same folder as app.py."
    )
    st.stop()

df = pd.read_csv(athlete_file)
region_df = pd.read_csv(region_file)

df = preprocessor.preprocess(df, region_df)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Olympics Analysis")

st.sidebar.image(
    "https://e7.pngegg.com/pngimages/1020/402/"
    "png-clipart-2024-summer-olympics-brand-circle-area-"
    "olympic-rings-olympics-logo-text-sport.png"
)

user_menu = st.sidebar.radio(
    "Select an Option",
    (
        "Medal Tally",
        "Overall Analysis",
        "Country-wise Analysis",
        "Athlete wise Analysis"
    )
)


# --------------------------------------------------
# 1. MEDAL TALLY
# --------------------------------------------------

if user_menu == "Medal Tally":

    st.sidebar.header("Medal Tally")

    years, countries = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox(
        "Select Year",
        years
    )

    selected_country = st.sidebar.selectbox(
        "Select Country",
        countries
    )

    medal_tally = helper.fetch_medal_tally(
        df,
        selected_year,
        selected_country
    )

    if selected_year == "Overall" and selected_country == "Overall":
        st.title("Overall Medal Tally")

    elif selected_year != "Overall" and selected_country == "Overall":
        st.title(f"Medal Tally in {selected_year} Olympics")

    elif selected_year == "Overall" and selected_country != "Overall":
        st.title(f"{selected_country} Overall Performance")

    else:
        st.title(
            f"{selected_country} Performance "
            f"in {selected_year} Olympics"
        )

    if not medal_tally.empty:
        st.dataframe(
            medal_tally,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No medal records found for this selection.")


# --------------------------------------------------
# 2. OVERALL ANALYSIS
# --------------------------------------------------

elif user_menu == "Overall Analysis":

    st.title("Top Statistics")

    editions = df["Year"].nunique()
    cities = df["City"].nunique()
    sports = df["Sport"].nunique()
    events = df["Event"].nunique()
    athletes = df["Name"].nunique()
    nations = df["region"].nunique()

    col1, col2, col3 = st.columns(3)

    col1.metric("Olympic Editions", editions)
    col2.metric("Host Cities", cities)
    col3.metric("Sports", sports)

    col1, col2, col3 = st.columns(3)

    col1.metric("Events", events)
    col2.metric("Nations", nations)
    col3.metric("Athletes", athletes)

    # Participating nations over time
    st.subheader("Participating Nations Over the Years")

    nations_over_time = helper.data_over_time(df, "region")

    fig = px.line(
        nations_over_time,
        x="Edition",
        y="region",
        markers=True,
        labels={
            "Edition": "Year",
            "region": "Number of Nations"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

    # Events over time
    st.subheader("Events Over the Years")

    events_over_time = helper.data_over_time(df, "Event")

    fig = px.line(
        events_over_time,
        x="Edition",
        y="Event",
        markers=True,
        labels={
            "Edition": "Year",
            "Event": "Number of Events"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

    # Athletes over time
    st.subheader("Athlete Participation Over the Years")

    athletes_over_time = helper.data_over_time(df, "Name")

    fig = px.line(
        athletes_over_time,
        x="Edition",
        y="Name",
        markers=True,
        labels={
            "Edition": "Year",
            "Name": "Number of Athletes"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

    # Sports and events heatmap
    st.subheader("Number of Events by Sport and Year")

    sports_events = df.drop_duplicates(
        subset=["Year", "Sport", "Event"]
    )

    heatmap_data = sports_events.pivot_table(
        index="Sport",
        columns="Year",
        values="Event",
        aggfunc="count"
    ).fillna(0)

    fig, ax = plt.subplots(figsize=(18, 10))

    sns.heatmap(
        heatmap_data,
        cmap="YlGnBu",
        ax=ax
    )

    ax.set_xlabel("Olympic Year")
    ax.set_ylabel("Sport")
    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    # Most successful athletes
    st.subheader("Most Successful Athletes")

    sport_list = sorted(df["Sport"].dropna().unique().tolist())
    sport_list.insert(0, "Overall")

    selected_sport = st.selectbox(
        "Select a Sport",
        sport_list
    )

    successful_athletes = helper.most_successful(
        df,
        selected_sport
    )

    st.dataframe(
        successful_athletes,
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# 3. COUNTRY-WISE ANALYSIS
# --------------------------------------------------

elif user_menu == "Country-wise Analysis":

    st.sidebar.header("Country-wise Analysis")

    country_list = sorted(
        df["region"].dropna().unique().tolist()
    )

    selected_country = st.sidebar.selectbox(
        "Select a Country",
        country_list
    )

    # Country medal tally over the years
    st.title(f"{selected_country} Medal Tally Over the Years")

    country_df = helper.yearwise_medal_tally(
        df,
        selected_country
    )

    if not country_df.empty:

        fig = px.line(
            country_df,
            x="Year",
            y="Medal",
            markers=True,
            labels={
                "Year": "Olympic Year",
                "Medal": "Medals Won"
            }
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No medal data is available for this country.")

    # Country's strongest sports
    st.subheader(
        f"Sports in Which {selected_country} Won Medals"
    )

    heatmap_data = helper.country_event_heatmap(
        df,
        selected_country
    )

    if not heatmap_data.empty:

        fig, ax = plt.subplots(figsize=(16, 9))

        sns.heatmap(
            heatmap_data,
            cmap="YlOrRd",
            ax=ax
        )

        ax.set_xlabel("Year")
        ax.set_ylabel("Sport")
        plt.tight_layout()

        st.pyplot(fig)
        plt.close(fig)

    else:
        st.info("No sports medal data is available.")

    # Top athletes
    st.subheader(f"Top 10 Athletes of {selected_country}")

    top_athletes = helper.most_successful_countrywise(
        df,
        selected_country
    )

    st.dataframe(
        top_athletes,
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# 4. ATHLETE-WISE ANALYSIS
# --------------------------------------------------

elif user_menu == "Athlete wise Analysis":

    st.title("Athlete-wise Analysis")

    # Age distribution by medal category
    st.subheader("Distribution of Age")

    age_df = df.dropna(subset=["Age"]).copy()

    fig = go.Figure()

    categories = [
        ("Overall Athletes", age_df),
        ("Gold Medalists", age_df[age_df["Medal"] == "Gold"]),
        ("Silver Medalists", age_df[age_df["Medal"] == "Silver"]),
        ("Bronze Medalists", age_df[age_df["Medal"] == "Bronze"])
    ]

    for label, category_df in categories:

        ages = category_df["Age"].dropna()

        if not ages.empty:
            fig.add_trace(
                go.Histogram(
                    x=ages,
                    name=label,
                    opacity=0.55,
                    histnorm="probability density",
                    nbinsx=30
                )
            )

    fig.update_layout(
        barmode="overlay",
        xaxis_title="Age",
        yaxis_title="Probability Density",
        legend_title="Athlete Category"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Age distribution across sports for gold medalists
    st.subheader("Gold Medalist Age Distribution by Sport")

    gold_df = df[
        (df["Medal"] == "Gold") &
        (df["Age"].notna())
    ].copy()

    if not gold_df.empty:

        top_sports = (
            gold_df["Sport"]
            .value_counts()
            .head(15)
            .index
            .tolist()
        )

        sports_age_df = gold_df[
            gold_df["Sport"].isin(top_sports)
        ]

        fig = px.box(
            sports_age_df,
            x="Sport",
            y="Age",
            points=False,
            labels={
                "Sport": "Sport",
                "Age": "Age"
            }
        )

        fig.update_layout(
            xaxis_tickangle=-45
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No gold medalist age data is available.")

    # Height versus weight
    st.subheader("Height vs Weight")

    sport_list = sorted(
        df["Sport"].dropna().unique().tolist()
    )
    sport_list.insert(0, "Overall")

    selected_sport = st.selectbox(
        "Select a Sport",
        sport_list
    )

    athlete_data = helper.weight_v_height(
        df,
        selected_sport
    )

    athlete_data = athlete_data.dropna(
        subset=["Height", "Weight"]
    )

    if not athlete_data.empty:

        fig = px.scatter(
            athlete_data,
            x="Weight",
            y="Height",
            color="Medal",
            symbol="Sex",
            hover_name="Name",
            labels={
                "Weight": "Weight (kg)",
                "Height": "Height (cm)"
            }
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No height and weight data is available.")

    # Men versus women participation
    st.subheader("Men vs Women Participation Over the Years")

    participation = helper.men_vs_women(df)

    fig = px.line(
        participation,
        x="Year",
        y=["Male", "Female"],
        markers=True,
        labels={
            "Year": "Olympic Year",
            "value": "Number of Athletes",
            "variable": "Gender"
        }
    )

    st.plotly_chart(fig, use_container_width=True)
