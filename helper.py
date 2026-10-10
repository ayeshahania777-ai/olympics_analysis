
import numpy as np


def fetch_medal_tally(df, year, country):
    medal_df = df.drop_duplicates(
        subset=[
            'Team', 'NOC', 'Games', 'Year', 'City',
            'Sport', 'Event', 'Medal'
        ]
    )

    flag = 0

    if year == 'Overall' and country == 'Overall':
        temp_df = medal_df

    elif year == 'Overall' and country != 'Overall':
        flag = 1
        temp_df = medal_df[medal_df['region'] == country]

    elif year != 'Overall' and country == 'Overall':
        temp_df = medal_df[medal_df['Year'] == int(year)]

    else:
        temp_df = medal_df[
            (medal_df['Year'] == int(year)) &
            (medal_df['region'] == country)
        ]

    if flag == 1:
        x = (
            temp_df.groupby('Year')[['Gold', 'Silver', 'Bronze']]
            .sum()
            .sort_values('Year')
            .reset_index()
        )
    else:
        x = (
            temp_df.groupby('region')[['Gold', 'Silver', 'Bronze']]
            .sum()
            .sort_values('Gold', ascending=False)
            .reset_index()
        )

    x['total'] = x['Gold'] + x['Silver'] + x['Bronze']

    for col in ['Gold', 'Silver', 'Bronze', 'total']:
        x[col] = x[col].astype(int)

    return x


def country_year_list(df):
    years = df['Year'].unique().tolist()
    years.sort()
    years.insert(0, 'Overall')

    country = np.unique(df['region'].dropna().values).tolist()
    country.sort()
    country.insert(0, 'Overall')

    return years, country


def data_over_time(df, col):
    nations_over_time = (
        df.drop_duplicates(['Year', col])['Year']
        .value_counts()
        .rename_axis('Edition')
        .reset_index(name=col)
        .sort_values('Edition')
    )

    return nations_over_time


def most_successful(df, sport):
    temp_df = df.dropna(subset=['Medal'])

    if sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]

    athlete_medals = (
        temp_df['Name']
        .value_counts()
        .rename_axis('Name')
        .reset_index(name='Medals')
        .head(15)
    )

    athlete_sport = (
        temp_df[['Name', 'Sport', 'region']]
        .drop_duplicates(subset=['Name'])
    )

    x = athlete_medals.merge(athlete_sport, on='Name', how='left')

    return x[['Name', 'Medals', 'Sport', 'region']]


def yearwise_medal_tally(df, country):
    temp_df = df.dropna(subset=['Medal']).copy()

    temp_df = temp_df.drop_duplicates(
        subset=[
            'Team', 'NOC', 'Games', 'Year', 'City',
            'Sport', 'Event', 'Medal'
        ]
    )

    new_df = temp_df[temp_df['region'] == country]

    final_df = (
        new_df.groupby('Year')
        .size()
        .reset_index(name='Medal')
    )

    return final_df


def country_event_heatmap(df, country):
    temp_df = df.dropna(subset=['Medal']).copy()

    temp_df = temp_df.drop_duplicates(
        subset=[
            'Team', 'NOC', 'Games', 'Year', 'City',
            'Sport', 'Event', 'Medal'
        ]
    )

    new_df = temp_df[temp_df['region'] == country]

    pt = new_df.pivot_table(
        index='Sport',
        columns='Year',
        values='Medal',
        aggfunc='count'
    ).fillna(0)

    return pt


def most_successful_countrywise(df, country):
    temp_df = df.dropna(subset=['Medal']).copy()
    temp_df = temp_df[temp_df['region'] == country]

    athlete_medals = (
        temp_df['Name']
        .value_counts()
        .rename_axis('Name')
        .reset_index(name='Medals')
        .head(10)
    )

    athlete_sport = (
        temp_df[['Name', 'Sport']]
        .drop_duplicates(subset=['Name'])
    )

    x = athlete_medals.merge(
        athlete_sport,
        on='Name',
        how='left'
    )

    return x[['Name', 'Medals', 'Sport']]


def weight_v_height(df, sport):
    athlete_df = df.drop_duplicates(
        subset=['Name', 'region']
    ).copy()

    athlete_df['Medal'] = athlete_df['Medal'].fillna('No Medal')

    if sport != 'Overall':
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        return temp_df

    return athlete_df


def men_vs_women(df):
    athlete_df = df.drop_duplicates(
        subset=['Name', 'region']
    )

    men = (
        athlete_df[athlete_df['Sex'] == 'M']
        .groupby('Year')
        .size()
        .reset_index(name='Male')
    )

    women = (
        athlete_df[athlete_df['Sex'] == 'F']
        .groupby('Year')
        .size()
        .reset_index(name='Female')
    )

    final = men.merge(women, on='Year', how='outer')
    final = final.fillna(0)

    final['Male'] = final['Male'].astype(int)
    final['Female'] = final['Female'].astype(int)

    return final
