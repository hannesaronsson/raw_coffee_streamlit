import requests
import streamlit as st
import polars as pl
from io import StringIO
import plotly.graph_objects as go


@st.cache_data()
def get_data():
    response = requests.get('https://rq013sxzu8.execute-api.eu-north-1.amazonaws.com/prod/prices')
    df = None
    if response.status_code == 200:
        # Convert the JSON response to a pandas DataFrame
        content_type = response.headers.get('Content-Type')
        if 'text/csv' in content_type:
            data = StringIO(response.text)
            df = pl.read_csv(data)
            df = df.with_columns(time = pl.col('time').str.to_datetime())

    return df

df: pl.DataFrame = get_data()

dates = df.select(pl.col('time').unique())['time'].sort(descending=True)
current_products = df.filter(pl.col('time') == pl.col('time').max())['name'].to_list()
last_day_product = df.filter(pl.col('time') == dates[1])['name'].to_list()
data_freschness = df['time'].max()
product_change_amnt = len(last_day_product) - len(current_products) 



delta_product_metric = None
if product_change_amnt != 0:
    delta_product_metric = product_change_amnt

cols = st.columns(2) 
cols[0].metric('Current products for sale', value=len(current_products),delta=delta_product_metric)
cols[1].metric('Latest data gather', value=data_freschness.strftime('%Y-%m-%d'))

st.write('Shows price history for the current offerings')
selected_product = st.selectbox('Price History',options=current_products)


price_history_df = df.filter(pl.col('name') == selected_product)


fig = go.Figure()
x = price_history_df['time']
y = price_history_df['price']

fig.add_trace(go.Scatter(x=x,y=y))


st.plotly_chart(fig)



