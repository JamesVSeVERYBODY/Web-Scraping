import streamlit as st
import pandas as pd
import altair as alt

# Load the dataset
df = pd.read_csv('GitHub_topics_detailed.csv')

# Sidebar to choose comparison or single view
view_mode = st.sidebar.radio("View Mode", ("Single Topic", "Compare Topics", "All Rank"))

if view_mode == "Single Topic":
    # Single topic selection
    selected_topic = st.sidebar.selectbox('Select a topic', df['Topics'].unique())
    
    # Filter the dataset based on the selected topic
    filtered_df = df[df['Topics'] == selected_topic]
    
    # Display basic information using a more aesthetic layout
    st.title(f'GitHub Topic: {selected_topic}')
    if not filtered_df.empty:
        row = filtered_df.iloc[0]
        with st.container():
            st.subheader("Most Popular Repo:")
            st.markdown(f"[{row['Popular_Repository']}](https://github.com/{row['PR_Username']}/{row['Popular_Repository']})", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.caption("Description")
                st.write(row['Description'])
            with col2:
                st.caption("Top Repo Owner")
                st.write(row['PR_Username'])
            st.metric(label="Stars", value=f"{row['Stars']:,}")
            st.metric(label="Forks", value=f"{row['Forks']:,}")
            st.markdown(f"**Topic URL:** [Visit Topic](https://github.com/topics/{selected_topic})")

    # Visualization enhancements
    st.subheader('Stars vs Forks for Popular Repositories')
    bubble_chart = alt.Chart(filtered_df).mark_circle().encode(
        x=alt.X('Stars:Q', title='Stars', axis=alt.Axis(format=',d')),
        y=alt.Y('Forks:Q', title='Forks', axis=alt.Axis(format=',d')),
        size='Stars:Q',
        color=alt.value('#1f77b4'),
        tooltip=['Popular_Repository', alt.Tooltip('Stars:Q', format=',d'), alt.Tooltip('Forks:Q', format=',d')]
    ).properties(
        width=600,
        height=400
    ).interactive()
    st.altair_chart(bubble_chart)

    # Lollipop Chart for Top Repositories by Stars
    st.subheader('Top Repositories by Stars')
    lollipop_chart = alt.Chart(filtered_df).mark_point(filled=True, size=100).encode(
        y=alt.Y('Popular_Repository:N', sort='-x', title='Repository'),
        x=alt.X('Stars:Q', title='Stars', axis=alt.Axis(format=',d')),
        color=alt.Color('Popular_Repository:N', legend=None),  # Optional: Customize color mapping if needed
        tooltip=['Popular_Repository', alt.Tooltip('Stars:Q', format=',d')]
    ).properties(
        width=600,
        height=400
    ) + alt.Chart(filtered_df).mark_rule().encode(
        y=alt.Y('Popular_Repository:N', sort='-x'),
        x=alt.X('Stars:Q'),
        color=alt.Color('Popular_Repository:N', legend=None)
    )
    st.altair_chart(lollipop_chart, use_container_width=True)

elif view_mode == "Compare Topics":
    # Comparison view adjustments
    topic_a = st.sidebar.selectbox('Select Topic A', df['Topics'].unique(), key='topic_a')
    topic_b = st.sidebar.selectbox('Select Topic B', df['Topics'].unique(), key='topic_b')
    
    # Filter the dataset for both topics
    df_a = df[df['Topics'] == topic_a]
    df_b = df[df['Topics'] == topic_b]
    
    # Display topic comparison
    st.title(f'Popular Repo Comparison: {topic_a} vs {topic_b}')
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f'{topic_a} Details')
        for _, row in df_a.iterrows():
            with st.container():
                st.caption("Popular Repository : ")
                st.subheader(row['Popular_Repository'])
                st.caption("Description")
                st.write(row['Description'])
                st.metric(label="Stars", value=f"{row['Stars']:,}")
                st.metric(label="Forks", value=f"{row['Forks']:,}")
    with col2:
        st.subheader(f'{topic_b} Details')
        for _, row in df_b.iterrows():
            with st.container():
                st.caption("Popular Repository : ")
                st.subheader(row['Popular_Repository'])
                st.caption("Description")
                st.write(row['Description'])
                st.metric(label="Stars", value=f"{row['Stars']:,}")
                st.metric(label="Forks", value=f"{row['Forks']:,}")

    # Combined bubble chart
    st.subheader(f'Stars vs Forks Comparison: {topic_a} vs {topic_b}')
    combined_chart = alt.Chart(df_a).mark_circle(size=60).encode(
        x='Stars:Q',
        y='Forks:Q',
        color=alt.value('#1f77b4'),
        tooltip=['Popular_Repository', 'Stars', 'Forks']
    ).properties(
        width=600,
        height=400
    ) + alt.Chart(df_b).mark_circle(size=60).encode(
        x='Stars:Q',
        y='Forks:Q',
        color=alt.value('#ff7f0e'),
        tooltip=['Popular_Repository', 'Stars', 'Forks']
    )
    st.altair_chart(combined_chart.interactive())

    # Donut chart for star distribution
    st.subheader(f'Star Distribution: {topic_a} vs {topic_b}')
    df_a['Label'] = topic_a
    df_b['Label'] = topic_b
    combined_df = pd.concat([df_a[['Stars', 'Label']], df_b[['Stars', 'Label']]])
    
    donut_chart = alt.Chart(combined_df).mark_arc(innerRadius=50).encode(
        theta='Stars:Q',
        color='Label:N',
        tooltip=['Label', alt.Tooltip('Stars:Q', format=',d')]
    ).properties(
        width=400,
        height=400
    )
    st.altair_chart(donut_chart)

elif view_mode == "All Rank":
    # All Rank view implementation with additional visualizations
    st.title("GitHub Topic Rankings")
    
    # Sort by options
    sort_by = st.selectbox("Sort by", ['Stars', 'Forks'], index=0)
    sort_order = st.radio("Sort Order", ['Descending', 'Ascending'], index=0)

    # Search bar for filtering topics
    search_term = st.text_input("Search Topics", "")

    # Apply search filter
    filtered_df = df[df['Topics'].str.contains(search_term, case=False, na=False)]

    # Apply sorting based on selection
    sorted_df = filtered_df.sort_values(by=sort_by, ascending=(sort_order == 'Ascending')).reset_index(drop=True)

    # Overview scatter plot
    st.subheader("Overview of Topics by Stars and Forks")
    overview_scatter = alt.Chart(sorted_df).mark_circle(size=60).encode(
        x=alt.X('Stars:Q', title='Stars', scale=alt.Scale(type='log')),
        y=alt.Y('Forks:Q', title='Forks', scale=alt.Scale(type='log')),
        color=alt.Color('Topics:N', legend=None),
        tooltip=['Topics', 'Stars', 'Forks']
    ).properties(width=700, height=400).interactive()
    st.altair_chart(overview_scatter)

    # Extra Visualization 1: Bar chart of stars and forks
    st.subheader("Stars and Forks by Topic")
    bar_chart = alt.Chart(sorted_df).mark_bar().encode(
        x=alt.X('Topics:N', title='Topics'),
        y=alt.Y('Stars:Q', title='Stars'),
        color=alt.Color('Topics:N', legend=None),
        tooltip=['Topics', 'Stars', 'Forks']
    ).properties(width=700, height=400)
    st.altair_chart(bar_chart)

    # Extra Visualization 2: Line chart to show Stars trend
    st.subheader("Trend of Stars by Topic")
    line_chart = alt.Chart(sorted_df).mark_line(point=True).encode(
        x=alt.X('Topics:N', title='Topics'),
        y=alt.Y('Stars:Q', title='Stars'),
        color=alt.Color('Topics:N', legend=None),
        tooltip=['Topics', 'Stars']
    ).properties(width=700, height=400)
    st.altair_chart(line_chart)

    # Display each topic in an expander
    for i in range(len(sorted_df)):
        topic = sorted_df.iloc[i]
        with st.expander(f"{i+1}. {topic['Topics']} ({topic['Stars']:,} Stars)"):
            st.subheader(f"Description for {topic['Topics']}:")
            st.write(topic['Description'])
            st.subheader("Popular Repository:")
            st.write(f"[{topic['Popular_Repository']}](https://github.com/{topic['PR_Username']}/{topic['Popular_Repository']})")
            st.metric("Stars", f"{topic['Stars']:,}")
            st.metric("Forks", f"{topic['Forks']:,}")

            # Optional: Mini Chart for detailed visualization
            mini_chart = alt.Chart(pd.DataFrame([topic])).mark_bar().encode(
                x=alt.X('Stars:Q', title='Stars'),
                y=alt.Y('Forks:Q', title='Forks'),
                color=alt.value('lightblue')
            ).properties(width=300, height=150)
            st.altair_chart(mini_chart)
