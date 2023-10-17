# Import Libraries
import pandas as pd
import streamlit as st
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title='Sale Dashboard', page_icon=':bar_chart:', layout='wide')
st.title(':bar_chart: Sale Dashboard EDA')
st.markdown('<style>div.block-container{padding-top:1rem;}<style>', unsafe_allow_html=True)
fl = st.file_uploader(":file_folder: Upload new file", type=(['csv','txt','xlsx','xls']))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename)
else:
    df = pd.read_csv("Superstore.csv")
col1, col2 = st.columns((2))
df['Order Date'] = pd.to_datetime(df['Order Date'])
#Getting Min. Max date, Select Period
startDate = df['Order Date'].min()
endDate = df['Order Date'].max()
with col1:
    date1 = pd.to_datetime(st.date_input('Start Date: ', startDate))
with col2:
    date2 = pd.to_datetime(st.date_input('End Date: ', endDate))
df = df[(df['Order Date']>= date1) & (df['Order Date']<= date2)].copy()
# Select Region
st.sidebar.header('Choose your filter:')
region=st.sidebar.multiselect('Select Region:',df['Region'].unique())
if not region:
    df2=df.copy()
else:
    df2=df[df['Region'].isin(region)]
# Select State
state=st.sidebar.multiselect('Select State:',df2['State'].unique())
if not state:
    df3=df2.copy()
else:
    df3=df2[df2['State'].isin(state)]
# Select City
city=st.sidebar.multiselect('Select City:',df3['City'].unique())
# Created Fitered base on Region, State, City
if not region and not state and not city:
    filtered_df=df
elif not state and not city:
    filtered_df = df2
elif not region and not city:
    filtered_df = df3
elif region and city:
    filtered_df = df3[df['Region'].isin(region) & df['City'].isin(city)]
elif region and state:
    filtered_df = df3[df['Region'].isin(region) & df['State'].isin(state)]
elif state and city:
    filtered_df = df3[df['City'].isin(city) & df['State'].isin(state)]
elif city:
    filtered_df = df3[df3['City'].isin(city)]
else:
    filtered_df = df3[df3['City'].isin(city) & df3['State'].isin(state) & df3['Region'].isin(region)]
# Create 02 Chart of Filtered_df
category_df = filtered_df.groupby(by = ['Category'], as_index = False)['Sales'].sum()
with col1:
    st.subheader('Category wise Sales')
    fig = px.bar(category_df, x = 'Category', y = 'Sales', text = ['${:,.2f}'.format(x) for x in category_df['Sales']], 
                 template='seaborn')
    st.plotly_chart(fig,use_container_width=True, height = 200)
with col2:
    st.subheader('Region wise Sales')
    fig = px.pie(filtered_df, values= 'Sales', names='Region', hole= 0.5,
                 template='seaborn')
    fig.update_traces(text=filtered_df['Region'], textposition='outside')
    st.plotly_chart(fig,use_container_width=True, height = 200)
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category data:"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download data", data=csv, file_name='Category.csv', mime="text/csv",
                           help='Click to download as a CSV file')
with cl2:
    with st.expander("Region data:"):
        region_df = filtered_df.groupby(by='Region', as_index=False)['Sales'].sum()
        st.write(region_df.style.background_gradient(cmap="Blues"))
        csv = region_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download data", data=csv, file_name='Region.csv', mime="text/csv",
                           help='Click to download as a CSV file')
filtered_df['Month_Year']=filtered_df['Order Date'].dt.to_period('M')
st.subheader('Time series analysis')
linechart = pd.DataFrame(filtered_df.groupby(filtered_df['Month_Year'].dt.strftime('%Y - %b'))['Sales'].sum()).reset_index()
fig2=px.line(linechart, x='Month_Year',y='Sales',labels={'Sales':'Amount'}, height=500,width=1000,template='gridon')
st.plotly_chart(fig2,use_container_width=True)
with st.expander('Time series data:'):
    st.write(linechart.T.astype('string[pyarrow]').style.background_gradient(cmap="Blues"))
    csv=linechart.to_csv(index=False).encode('utf-8')
    st.download_button('Download data', data=csv, file_name='TimeSeries.csv', mime='text/csv',
                       help='Click to download as a CSV file')
#Created a treemap base on Region, Category, Sub-category
st.subheader('Hierarchical view of Sales using TreeMap')
fig3 = px.treemap(filtered_df,path=['Region','Category','Sub-Category'], values='Sales',hover_data=['Sales'],
                  color='Sub-Category')
fig3.update_layout(width=800,height=650)
st.plotly_chart(fig3, use_container_width=True)
# Created a scatter plot
data1 = px.scatter(filtered_df, x = 'Sales', y= 'Profit', size='Quantity')
data1['layout'].update(title='Relationship between Sales and Profits using Scatter Plot', 
                       titlefont= dict(size=20), xaxis = dict(title='Sales', titlefont=dict(size=19)),
                       yaxis=dict(title='Profits', titlefont=dict(size=19)))
st.plotly_chart(data1, use_container_width=True)
with st.expander('View data:'):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Blues"))
# Download Dataset
csv = df.to_csv(index=False).encode('utf-8')
st.download_button('Download Data', data=csv, file_name='Data.csv', mime='text/csv')
