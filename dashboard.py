import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import warnings 
import pathlib
import sqlite3

warnings.filterwarnings("ignore")
con = sqlite3.connect('amin.db')
df = pd.read_sql("select * from sales", con)
# pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', '{:,.0f}'.format)



#------------------------------------------------------SETUP----------------------------------------------------------------
st.set_page_config(layout="wide")


def css(path):
    try:
        with open(path, 'r') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)
    except Exception as e:
        print("An error occured",e)
css_path = pathlib.Path("assets/style.css")
css(css_path)


#---------------------------------------------header---------------------
st.title("BluePeak Sales Analysis")
st.markdown('''| Section      | Details                                                                               |
|--------------|---------------------------------------------------------------------------------------|
| Tools Used   | GCP(Bigquery, Dataform), Python (Pandas, Matplotlib), SQL, Quarto                     |
| Data Source  | Google Bigquery                                                                       |''')





#----------------------------------------------------cleaning-------------------------------------------------------
df["cleaned_city"] = df["city"].str.lower().str.strip()
df["cleaned_city"] = df["cleaned_city"].apply(lambda x: "bangalore" if pd.notna(x) and x.startswith("ben") else x)
df["cleaned_city"] = df["cleaned_city"].apply(lambda x: "bangalore" if pd.notna(x) and x.startswith("ban") else x)
df["cleaned_city"] = df["cleaned_city"].apply(lambda x: "bangalore" if pd.notna(x) and x.endswith(("lore", "luru")) else x)
df["cleaned_city"] = df["cleaned_city"].fillna("bangalore")
df["subtotal"] = df["subtotal"].fillna(df["subtotal"].mean())
df.drop(columns = ["city"], inplace = True)
df["event_date"] = pd.to_datetime(df["event_date"])



#-----------------------------------------------------QIA-------------------------------------------------------------------
st.markdown("## Question Insight Action")
st.markdown('***')

#---------------------------------------------------Question 1---------------------------------------------------------------------
st.markdown("### Which Pincode Generates the Highest Sales ? ")
pin = df.groupby("pincode")["subtotal"].sum().reset_index().sort_values(by = "subtotal", ascending = False)
pin["pincode"] = pin["pincode"].astype(str)
fig = px.bar(pin, x = "pincode", y = "subtotal", text = round(pin["subtotal"]/1000), labels = {"pincode":"Pincode", "subtotal": "Total Sales"},color = "subtotal", color_continuous_scale="GnBu")

fig.update_xaxes(
    range = [-0.5,10],
    tickfont = dict(color="black")
)
fig.update_traces(
    marker_line_color = "black",
    marker_line_width = 1.5,
    texttemplate = "%{text}k",
    textposition = "outside",
    outsidetextfont=dict(color="black")
)
fig.update_layout(
    height= 500,
    width = 800,
    template="plotly_white",
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(color="black"),
    margin=dict( t=80, b=60),
    annotations=[
        dict(
            text="Highest Sales By Pincode",
            x=0.555,
            y=1.22,
            xref="paper",
            yref="paper",
            font=dict(size=25, family="Arial", color="#1e3a8a",weight = "bold"),
            showarrow=False,
            bgcolor="white",
            bordercolor="#1e40af", 
            borderwidth=2.4,
            borderpad=14,
            width = 668,
            align = "left",

            
        )]


)
st.plotly_chart(fig, use_container_width=False)
st.write('''The 560037 pincode leads with a total sales value of 2,242k, indicating a strong customer base and high purchasing activity in this region. This is closely followed by 560076 with 2,146k sales, suggesting comparable market potential. The third-highest contributor, 560102, records 2,089k in sales, further highlighting its significance in the overall revenue mix.''')


#-------------------------------------------Question 2-----------------------------------------------

st.markdown('### Average Order Value at different location ?')
count_city = df["cleaned_city"].value_counts()[df["cleaned_city"].value_counts() > 9].index
newcity = df[df["cleaned_city"].isin(count_city)]
nc = newcity.groupby("cleaned_city")["subtotal"].mean().reset_index().sort_values(by = "subtotal", ascending = False)
fig = px.bar(nc, x="cleaned_city", y="subtotal",text = nc["subtotal"]/1000, labels = {"cleaned_city":"City","subtotal":"Average Order Value"}, color = "subtotal", color_continuous_scale= "Blues")
fig.update_traces(
    marker_line_color = "black",
    marker_line_width = 2,
    texttemplate = "%{text:.2f}k",
    textposition = "outside"
)
fig.update_xaxes(
    tickfont = dict(color = "black")
)
fig.update_layout(
    height= 500,
    width = 800,
    font=dict(color="black"),
    template="plotly_white",
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict( t=80, b=60),
    annotations=[
        dict(
            text="Average Order Value",
            x=0.620,
            y=1.24,
            xref="paper",
            yref="paper",
            font=dict(size=25, family="Arial", color="#1e3a8a",weight = "bold"),
            showarrow=False,
            bgcolor="white",
            bordercolor="#1e40af", 
            borderwidth=2,
            borderpad=14,
            width = 670,
            align = "left",
            
        )])
st.plotly_chart(fig, use_container_width=False)
st.write('''Average order value analysis shows Chennai leading with ₹2.07k, followed by Electronic City (Bangalore) at ₹1.95k.
Yelahanka (Bangalore) ranks third with ₹1.86k, and Mumbai follows with ₹1.70k.
These results highlight strong purchasing power in Chennai and key Bangalore localities.''')
