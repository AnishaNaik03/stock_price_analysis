import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector

st.set_page_config(page_title="Stock Dashboard", page_icon="📈", layout="wide")

@st.cache_data

#######################################################################################

def load_data():
    # Establish a connection to the MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        db="sample",
    )
    # Load data from the database
    query = "SELECT * FROM stock_3"
    df = pd.read_sql(query, conn)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    
    # Close the connection
    conn.close()
    
    numeric_df = df.select_dtypes(['float', 'int'])
    numeric_cols = numeric_df.columns
    non_numeric_cols = list(df.select_dtypes(['object']).columns)
    non_numeric_cols.append(None)

    text_df = df.select_dtypes(['object'])
    text_cols = text_df.columns

    stock_column = df["Name"]
    unique_stocks = stock_column.unique()
    return df, numeric_cols, text_cols, unique_stocks, non_numeric_cols

df, numeric_cols, text_cols, unique_stocks, non_numeric_cols = load_data()


########################################################################################
#Home page
st.markdown("<h1 style='text-align:center;'>Stock Dashboard 📈</h1>", unsafe_allow_html=True)
#expander
with st.expander("Tabular"):
        showData=st.multiselect("filter:",numeric_cols,default=[])
        st.write(df[showData])


#############################################################################################

#sidebar for plots
st.sidebar.title("Settings")
check_box = st.sidebar.checkbox(label="Display Dataset")
if check_box:
    st.write(df)
opt=st.sidebar.selectbox("select attribute for statistical data",numeric_cols)
st.sidebar.subheader("Timeseries Settings")
feature_selection = st.sidebar.multiselect(label="Features to Plot", options=numeric_cols)
stock_dropdown = st.sidebar.selectbox(label="Stock Ticker", options=unique_stocks)

########################################################################################

#statical data display
sum_values = df[opt].sum()
mean_value=df[opt].mean()
median_value=df[opt].median()
mode_value=df[opt].mode()
st.subheader(f"Statistical Data for {opt}")

total1,total2=st.columns(2,gap='large')
with total1:
    st.info('toal value',icon='📌')
    st.write(f"{sum_values:,.2f}")
    
with total2:
    st.info('Average value',icon='📌')
    st.write(f"{mean_value:,.2f}")
##########################################################################################

#display plot
df_filtered = df[df['Name'] == stock_dropdown]
df_features = df_filtered[feature_selection]

g1,g2=st.columns(2,gap="large")
with g1:
    pie_chart_feature = 'Name'
    pie_chart_df = df.groupby(pie_chart_feature).size().reset_index(name='count')

    pie_chart_figure = px.pie(data_frame=pie_chart_df,
                            names=pie_chart_feature,
                            values='count',
                            title='Distribution of Stocks')

    st.plotly_chart(pie_chart_figure)
with g2:
    plot = px.bar(data_frame=df, x="Name", y="high",color="Name",animation_frame="year",
                  title='highest Stocks price over years')
    st.plotly_chart(plot)

if not df_features.empty:
    plotly_figure = px.line(
        data_frame=df_features,
        x=df_features.index,
        y=feature_selection,
        title=(str(stock_dropdown) + ' Timeline')
    )
    st.plotly_chart(plotly_figure)
else:
    st.write("Please select features to plot.")
st.markdown("""---""")
############################################################################################



chart_select = st.sidebar.selectbox(
    label="Select the Chart Type",
    options=["Select Chart Type", "Scatterplot","Barplot","Lineplots", "Histogram", "Boxplots"],
    index=0  # Set index to 0 for default selection ("Select Chart Type")
)

try:
    if chart_select == "Scatterplot":
        st.sidebar.subheader("Scatterplot Settings")
        x_values = st.sidebar.selectbox("X axis", options=numeric_cols)
        y_values = st.sidebar.selectbox("Y axis", options=numeric_cols)
        plot = px.scatter(data_frame=df_filtered, x=x_values, y=y_values,size="open",color="close",animation_frame="year")
        st.plotly_chart(plot)

    if chart_select == "Barplot":
        st.sidebar.subheader("Barplot Settings")
        x_values = st.sidebar.selectbox("X axis", options=numeric_cols)
        y_values = st.sidebar.selectbox("Y axis", options=numeric_cols)
        plot = px.bar(data_frame=df_filtered, x=x_values, y=y_values,color="Name",animation_frame="year")
        st.plotly_chart(plot)

    elif chart_select == "Lineplots":
        st.sidebar.subheader("Line Plot Settings")
        x_values = st.sidebar.selectbox('X axis', options=numeric_cols)
        y_values = st.sidebar.selectbox('Y axis', options=numeric_cols)
        color_value = st.sidebar.selectbox("Color", options=non_numeric_cols)
        plot = px.line(data_frame=df_filtered, x=x_values, y=y_values, color=color_value,animation_frame="year")
        st.plotly_chart(plot)

    elif chart_select == "Histogram":
        st.sidebar.subheader("Histogram Settings")
        x = st.sidebar.selectbox('Feature', options=numeric_cols)
        bin_size = st.sidebar.slider("Number of Bins", min_value=10, max_value=100, value=40)
        color_value = st.sidebar.selectbox("Color", options=non_numeric_cols)
        plot = px.histogram(x=x, data_frame=df_filtered, color=color_value,animation_frame="year")
        st.plotly_chart(plot)

    elif chart_select == "Boxplots":
        st.sidebar.subheader("Boxplot Settings")
        y = st.sidebar.selectbox("Y axis", options=numeric_cols)
        x = st.sidebar.selectbox("X axis", options=non_numeric_cols)
        color_value = st.sidebar.selectbox("Color", options=non_numeric_cols)
        plot = px.box(data_frame=df_filtered, y=y, x=x, color=color_value,animation_frame="year")
        st.plotly_chart(plot)

except Exception as e:
    st.error(f"An error occurred: {e}")
