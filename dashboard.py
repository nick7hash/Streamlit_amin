import streamlit as st
import pandas as pd
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
st.markdown('''
<div class="hero-section">
    <h1 class="hero-title"> BluePeak Sales Analysis</h1>
</div>
''', unsafe_allow_html=True)

# Info cards using CSS classes
# col1, col2, col3 = st.columns(3)

with st.sidebar:
    st.markdown('''
    <div class="infocard">
        <h4 class="author">Author</h4>
        <p class="authorname">Nikhil Pundir</p>
        <p class="authoragency">DataActs</p>
    </div>
    ''', unsafe_allow_html=True)
st.markdown('''| Section      | Details                                                                               |
|--------------|---------------------------------------------------------------------------------------|
| Tools Used   | GCP(Bigquery, Dataform), Python (Pandas, Plotly), SQL, Streamlit                     |
| Data Source  | Google Bigquery                                                                       |''')


st.markdown("***")
st.header("Report Overview")
st.write('''

This report presents an analysis of data collected from the Amintiri sales database for the selected period.

The main goal of this analysis is to:

1) Identify key trends in product sales, revenue, and customer behavior

2) Understand the overall performance and patterns across categories, locations, and marketing channels

3) Gain actionable insights that can support better business and marketing decisions''')



#----------------------------------------------------cleaning-------------------------------------------------------
df["cleaned_city"] = df["city"].str.lower().str.strip()
df["cleaned_city"] = df["cleaned_city"].apply(lambda x: "bangalore" if pd.notna(x) and x.startswith("ben") else x)
df["cleaned_city"] = df["cleaned_city"].apply(lambda x: "bangalore" if pd.notna(x) and x.startswith("ban") else x)
df["cleaned_city"] = df["cleaned_city"].apply(lambda x: "bangalore" if pd.notna(x) and x.endswith(("lore", "luru")) else x)
df["cleaned_city"] = df["cleaned_city"].fillna("bangalore")
df["subtotal"] = df["subtotal"].fillna(df["subtotal"].mean())
df.drop(columns = ["city"], inplace = True)
df["event_date"] = pd.to_datetime(df["event_date"])

#--------------------------------------melting down data and creating ndf dataframe ------------------------------------
id_vars = [
    "user_pseudo_id", "event_date", "new_event_timestamp", "pincode",
    "subtotal", "source_name", "source_medium", "source_origin",
    "rw", "cleaned_city"
]
item_name = df.melt(
    id_vars = id_vars,
    value_vars = ["item_name_0","item_name_1","item_name_2","item_name_3","item_name_4"],
    value_name = "Product_name",
    var_name = "in"
)
item_price = df.melt(
    id_vars= id_vars,
    value_vars = ["price_0","price_1","price_2","price_3","price_4"],
    value_name = "Price",
    var_name = "ip"
)
item_quantity = df.melt(
    id_vars = id_vars,
    value_vars = ["quantity_0","quantity_1","quantity_2","quantity_3","quantity_4"],
    value_name = "Quantity",
    var_name = "iq"

)
item_variant = df.melt(
    id_vars = id_vars,
    value_vars = ["item_variant_0","item_variant_1","item_variant_2","item_variant_3","item_variant_4"],
    value_name = "Item_variant",
    var_name = "iv"

)

item_name["product_no"]    = item_name["in"].str.extract(r"(\d+)")
item_price["product_no"]   = item_price["ip"].str.extract(r"(\d+)")
item_quantity["product_no"]= item_quantity["iq"].str.extract(r"(\d+)")
item_variant["product_no"] = item_variant["iv"].str.extract(r"(\d+)")


item_name    = item_name.drop(columns=["in"])
item_price   = item_price.drop(columns=["ip"])
item_quantity= item_quantity.drop(columns=["iq"])
item_variant = item_variant.drop(columns=["iv"])


merged = (
    item_name
    .merge(item_price, on=id_vars + ["product_no"])
    .merge(item_quantity, on=id_vars + ["product_no"])
    .merge(item_variant, on=id_vars + ["product_no"])
)

  
merged["Revenue"] = merged["Price"] * merged["Quantity"]
ndf = merged.copy()

#----------------------------------------------------sample data copy--------------------------------------------------
from st_aggrid import AgGrid
st.header("Sample Data")
AgGrid(ndf.head(100))

#---------------------------------------side bar with filtered df and ndf--------------------------------------------------

with st.sidebar:
    st.markdown("""
    <div style="
        background: linear-gradient(90deg, #0a192f, #004462);
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    ">
        <h4 style="color: white; margin: 0;">Date Selection</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Your original date input
    start_date, end_date = st.date_input(
        "Select Date Range",
        [df["event_date"].min(), df["event_date"].max()],
        help="Choose your date range for filtering data"
    )
    
    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)
mask1 = (df["event_date"] >= pd.to_datetime(start_date)) & (df["event_date"] <= pd.to_datetime(end_date))
mask2 = (ndf["event_date"] >= pd.to_datetime(start_date)) & (ndf["event_date"] <= pd.to_datetime(end_date))
ddf = df.loc[mask1]
dndf = ndf.loc[mask2]



#-----------------------------------------------------QIA-------------------------------------------------------------------
st.markdown('***')
st.markdown("## Question Insight Action")
st.markdown('***')

#---------------------------------------------------Question 1---------------------------------------------------------------------
st.markdown("### Which Pincode Generates the Highest Sales ? ")
pin = ddf.groupby("pincode")["subtotal"].sum().reset_index().sort_values(by = "subtotal", ascending = False)
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

st.markdown('''<div class = "summary"><p>The 560037 pincode leads with a total sales value of 2,242k, indicating a strong customer base and high purchasing activity in this region. This is closely followed by 560076 with 2,146k sales, suggesting comparable market potential. The third-highest contributor, 560102, records 2,089k in sales, further highlighting its significance in the overall revenue mix</p></div>''', unsafe_allow_html= True)


#-------------------------------------Top Selling Item of Each Pincode------------------------------

st.markdown('''#### Let’s take a look at the **top-selling item in each pincode**.''')
sell = dndf.groupby(["pincode", "Product_name"]).agg({
    "Quantity":"sum",
    "Revenue":"sum"
}).reset_index().sort_values(by = "Quantity", ascending = False)
geo = pd.read_csv(r"C:\Python Lab Work\Work\Project5(amintiri_report)\pincode_with_lat-long.csv",low_memory=False)
geo = geo.rename(columns = {"Pincode":"pincode"})
geoloc = geo[["pincode","Latitude", "Longitude"]]
sell = sell.merge(geoloc, on="pincode", how = "left")
fig = px.scatter_map(sell, lat = "Latitude", lon = "Longitude", size = "Revenue", color = "Quantity", hover_name = "pincode", hover_data = ["Product_name", "Quantity", "Revenue"], center = {"lat":12.9716, "lon":77.5946}, zoom = 10, color_continuous_scale=px.colors.sequential.Plasma )
fig.update_layout(
    height = 500,
    width = 300,
    margin={"r":0,"t":40,"l":0,"b":0},
)
st.plotly_chart(fig, use_container_with = False)
st.write('''***''')

#-------------------------------------------Average Order Value-----------------------------------------------

st.markdown('### Average Order Value at different location ?')
count_city = ddf["cleaned_city"].value_counts()[ddf["cleaned_city"].value_counts() > 9].index
newcity = ddf[ddf["cleaned_city"].isin(count_city)]
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
st.markdown('''<div class = "summary"><p>Average order value analysis shows Chennai leading with ₹2.07k, followed by Electronic City (Bangalore) at ₹1.95k. Yelahanka (Bangalore) ranks third with ₹1.86k, and Mumbai follows with ₹1.70k.These results highlight strong purchasing power in Chennai and key Bangalore localities</p></div>''',unsafe_allow_html= True)
st.markdown("***")
#-------------------------------------------Most Sold Item By Quantity-----------------------------------------------------------
st.markdown('''### What is the top-selling item based on total quantity sold?''')
items = dndf.groupby("Product_name")["Quantity"].sum().reset_index().sort_values(by = "Quantity", ascending = False).head(10)
fig = px.pie(items, values = "Quantity", names = "Product_name", color = 'Quantity', hole = 0.4)
fig.update_traces(textinfo = "percent+label", textposition = 'outside', textfont = dict(color = 'black'),domain=dict(x=[0.15, 0.85], y=[0, 1]),
    marker = dict(
    line = dict(color = "black", width = 2)
))
fig.update_layout(
    height = 600,
    width = 800,
    margin = {'t':50,'l':0,'r':0,'b':0},
        legend=dict(
        orientation="v",        
        yanchor="bottom",
        y=-0.5,                  
        xanchor="center",
        x=1,                 
        bgcolor="white",       
        bordercolor="black",
        borderwidth=1
    ),
    # annotations = [
    #     dict(
    #         text="Most Sold Item By Quantity",
    #         x=1.7,
    #         y=1.25,
    #         xref="paper",
    #         yref="paper",
    #         font=dict(size=25, family="Arial", color="#91770A",weight = "bold"),
    #         showarrow=False,
    #         bgcolor="white",
    #         bordercolor="#91770A", 
    #         borderwidth=2,
    #         borderpad=14,
    #         width = 620,
    #         align = "left",
    #     )
    # ]
)
st.plotly_chart(fig, use_container_width=True)

st.markdown('''<div class = "summary"><p>The analysis reveals that Croissant is the top-selling item, contributing 12.9% of total sales quantity. It is closely followed by Tres Leches (12%) and Ferrero Rocher (11%), making these three items the dominant contributors to overall sales performance.</p></div>''',unsafe_allow_html= True)

st.markdown("***")
#---------------------------Top Seller By Revenue and Quantity-------------------------------

st.markdown('### Top Seller By Revenue and Quantity')

dndf = dndf.drop(columns = "product_no")
dndf = dndf.dropna(subset=["Product_name"])
productrevenue = dndf.groupby("Product_name").agg(
    {
        'Revenue': 'sum',
        'Quantity': 'sum'
    }
).reset_index().sort_values(by = 'Revenue', ascending = False)
pr = productrevenue.melt(
    id_vars = "Product_name",
    value_vars = ["Revenue", "Quantity"],
    var_name = "Metric",
    value_name = "Value"
)
fig = px.bar(pr, x = "Product_name", y="Value", color = "Metric", barmode = "group", color_discrete_map={
        "Revenue": "#1960a2",
        "Quantity": "#fe6e61"
    })
fig.update_xaxes(
    range = [-0.5,10],
    tickfont = dict(color="black")
)
fig.update_traces(
    marker_line_color = "black",
    marker_line_width = 2,
)
fig.update_layout(
    height= 500,
    width = 900,
    )
st.plotly_chart(fig, use_container_width=False)

st.markdown('''<div class = "summary"><p>When measured by revenue, the top-performing products are Tres Leches (2.7M), Ferrero Rocher (2.25M), and Pineapple Cherry Cake (2.1M). However, in terms of quantity sold, the leading item shifts to Burnt Basque Cheesecake (1,517 units), followed by Tres Leches (1,415 units) and Ferrero Rocher (1,290 units).

This indicates that while premium cakes such as Tres Leches dominate in revenue contribution, certain products like Burnt Basque Cheesecake achieve higher sales volume, reflecting strong customer demand at possibly lower price points.</p></div>''',unsafe_allow_html= True)
st.markdown("***")

#----------------------------------------------Revenue Contribution by Category------------------------------------------------
st.markdown('''### What is the Revenue Contribution of each Product Category''')
product_category = {
    "Almond And Milk Chocolate Brunette": "Cakes & Loaves",
    "Almond And Milk Chocolate Brunette (Eggless)": "Cakes & Loaves",
    "Almond And Milk Chocolate Brunette (eggless)": "Cakes & Loaves",
    "Almond and Milk Chocolate Brunette": "Cakes & Loaves",
    "Almond and Milk Chocolate Brunette (Eggless)": "Cakes & Loaves",
    "Banoffee Cake": "Cakes & Loaves",
    "Belgian Dark Chocolate Truffle Cake (Eggless)": "Cakes & Loaves",
    "Belgian Dark Chocolate Truffle Cake (eggless)": "Cakes & Loaves",
    "Belgian Dark Chocolate Truffle cake (Eggless)": "Cakes & Loaves",
    "Black Satin Entremet (Chocolate Mousse Cake)": "Cakes & Loaves",
    "Blueberry Cheesecake (Eggless)": "Cakes & Loaves",
    "Blueberry Cheesecake (eggless)": "Cakes & Loaves",
    "Burnt Basque Cheesecake": "Cakes & Loaves",
    "Burnt basque cheesecake": "Cakes & Loaves",
    "Classic Black Forest Cake": "Cakes & Loaves",
    "Coffee Pecan Praline Cake": "Cakes & Loaves",
    "Coffee pecan praline cake": "Cakes & Loaves",
    "Cookie Dough Cake": "Cakes & Loaves",
    "Cookie Dough Cake (Eggless)": "Cakes & Loaves",
    "Cookie Dough Cake (eggless)": "Cakes & Loaves",
    "Dark Chocolate and Strawberry cake": "Cakes & Loaves",
    "Date, Palm And Walnut Cake (Vegan)": "Cakes & Loaves",
    "Date, Palm And Walnut Cake (vegan)": "Cakes & Loaves",
    "Date, Palm and Walnut Cake (Vegan)": "Cakes & Loaves",
    "Deep Chocolate Pull Up  Cake": "Cakes & Loaves",
    "Deep Chocolate Pull Up Cake": "Cakes & Loaves",
    "Ferrero Rocher Cake": "Cakes & Loaves",
    "Fresh Strawberry Cheesecake": "Cakes & Loaves",
    "Fresh Strawberry Cheesecake (Eggless)": "Cakes & Loaves",
    "Fresh strawberry and cream cake": "Cakes & Loaves",
    "Hazelnut Chocolate Truffle Cake (Eggless)": "Cakes & Loaves",
    "Hazelnut Chocolate Truffle Cake (eggless)": "Cakes & Loaves",
    "Hazelnut Milk Chocolate Entremet": "Cakes & Loaves",
    "Intense Chocolate And Caramel Cake": "Cakes & Loaves",
    "Intense chocolate and caramel cake": "Cakes & Loaves",
    "La Vie En Rose": "Cakes & Loaves",
    "La vie en rose": "Cakes & Loaves",
    "Lemon, Olive Oil And Chia Seed": "Cakes & Loaves",
    "Lemon, Olive Oil and Chia Seed": "Cakes & Loaves",
    "Lotus Biscoff Cake Loaf (Eggless)": "Cakes & Loaves",
    "Lotus Biscoff Cake Loaf (eggless)": "Cakes & Loaves",
    "Lotus Biscoff Pull Up  Cake": "Cakes & Loaves",
    "Lotus Biscoff Pull Up  Cake (Eggless)": "Cakes & Loaves",
    "Lotus Biscoff Pull Up Cake": "Cakes & Loaves",
    "Lotus Biscoff Pull Up Cake (Eggless)": "Cakes & Loaves",
    "Lotus Biscoff Pull Up Cake (eggless)": "Cakes & Loaves",
    "Mango And Cashew Entremet": "Cakes & Loaves",
    "Mango and Cashew entremet": "Cakes & Loaves",
    "Mango Cheesecake (Eggless)": "Cakes & Loaves",
    "Mango Pull Up Cake (eggless)": "Cakes & Loaves",
    "Mango pull up cake": "Cakes & Loaves",
    "Mango pull up cake (eggless)": "Cakes & Loaves",
    "Mango Tres Leches Dapper": "Cakes & Loaves",
    "Mango Tres Leches Dapper (Eggless)": "Cakes & Loaves",
    "Mango Tres leches Dapper": "Cakes & Loaves",
    "Matilda Cake": "Cakes & Loaves",
    "Matilda cake": "Cakes & Loaves",
    "Nutella And Fresh Strawberry Entremet": "Cakes & Loaves",
    "Nutella and Fresh Strawberry Entremet": "Cakes & Loaves",
    "Nutella Pull Up Cake": "Cakes & Loaves",
    "Nutella pull up cake": "Cakes & Loaves",
    "Opera": "Cakes & Loaves",
    "Peaches & Cream": "Cakes & Loaves",
    "Pineapple, Lychee And Cherry Cake": "Cakes & Loaves",
    "Pineapple, Lychee And Cherry Cake (Eggless)": "Cakes & Loaves",
    "Pineapple, Lychee And Cherry Cake (eggless)": "Cakes & Loaves",
    "Pineapple, Lychee and Cherry Cake": "Cakes & Loaves",
    "Pineapple, Lychee and Cherry Cake (Eggless)": "Cakes & Loaves",
    "Red Velvet": "Cakes & Loaves",
    "Red Velvet (Eggless)": "Cakes & Loaves",
    "Saffron Rasmalai Cake (Eggless)": "Cakes & Loaves",
    "Saffron Rasmalai Cake (eggless)": "Cakes & Loaves",
    "The Rakhi cake (Saffron Rasmalai eggless)": "Cakes & Loaves",
    "Strawberry Pull up": "Cakes & Loaves",
    "Strawberry Pull up (Eggless)": "Cakes & Loaves",
    "Strawberry Streusel Cake": "Cakes & Loaves",
    "Strawberry Streusel Cake (Eggless)": "Cakes & Loaves",
    "Strawberry Streusel Cake (eggless)": "Cakes & Loaves",
    "Sugar-Free Belgian Chocolate Truffle cake (Eggless)": "Cakes & Loaves",
    "Sugar-Free Belgian Chocolate Truffle cake (eggless)": "Cakes & Loaves",
    "Tiramisu Cake": "Cakes & Loaves",
    "Tres Leches Dapper": "Cakes & Loaves",
    "Tres Leches Dapper (Eggless)": "Cakes & Loaves",
    "Tres Leches Dapper (eggless)": "Cakes & Loaves",
    "Walnut Banana And Whole Wheat Cake": "Cakes & Loaves",
    "Walnut Banana and Whole Wheat Cake": "Cakes & Loaves",
    "White Chocolate Raspberry": "Cakes & Loaves",


    "Almond Rocks": "Brownies & Blondies",
    "Almond rocks": "Brownies & Blondies",
    "Chocolate Fudge Brownie": "Brownies & Blondies",
    "Chocolate Fudge Brownie (Eggless)": "Brownies & Blondies",
    "Chocolate Fudge Brownie (eggless)": "Brownies & Blondies",
    "Double Chocolate Walnut Brownie": "Brownies & Blondies",
    "Double Chocolate Walnut Brownie (Eggless)": "Brownies & Blondies",
    "Double Chocolate Walnut Brownie (eggless)": "Brownies & Blondies",
    "Double Chocolate With Caramelised Pistachio (Eggless)": "Brownies & Blondies",
    "Double Chocolate With Caramelised Pistachio (eggless)": "Brownies & Blondies",
    "Double Chocolate with Caramelised Pistachio (Eggless)": "Brownies & Blondies",
    "Gluten Free Chocolate Fudge Brownie": "Brownies & Blondies",
    "Nutella Brownie": "Brownies & Blondies",
    "Nutella Brownie (Eggless)": "Brownies & Blondies",
    "Nutella Brownie (eggless)": "Brownies & Blondies",
    "Pistachio Blondie": "Brownies & Blondies",
    "Pistachio Blondie (Eggless)": "Brownies & Blondies",
    "Pistachio Blondie (eggless)": "Brownies & Blondies",

   
    "Bagels": "Cookies & Biscuits",
    "Box Of 4": "Cookies & Biscuits",
    "Box of 4": "Cookies & Biscuits",
    "Cookies Box Of 3": "Cookies & Biscuits",
    "Cookies Box of 3": "Cookies & Biscuits",
    "Croissants": "Cookies & Biscuits",
    "Eggless Croissant": "Cookies & Biscuits",
    "Eggless croissant": "Cookies & Biscuits",
    "DIY cookie dough": "Cookies & Biscuits",
    "Macaron Box Of 6": "Cookies & Biscuits",
    "Macaron Box of 6": "Cookies & Biscuits",
    "Mixed Herbs And Cheese Sable": "Cookies & Biscuits",
    "Mixed herbs and cheese sable": "Cookies & Biscuits",
    "Nutty Cookies (Eggless)": "Cookies & Biscuits",
    "Nutty Cookies (eggless)": "Cookies & Biscuits",
    "Paprika And Cheese Crackers": "Cookies & Biscuits",
    "Paprika and cheese crackers": "Cookies & Biscuits",
    "Parmesan Cheese Crackers": "Cookies & Biscuits",
    "Parmesan cheese crackers": "Cookies & Biscuits",
    "Salted Butter Crackers": "Cookies & Biscuits",
    "Salted butter crackers": "Cookies & Biscuits",
    "Shrewsbury Thins": "Cookies & Biscuits",
    "Shrewsbury thins": "Cookies & Biscuits",
    "Red velvet Cream Cheese cookies": "Cookies & Biscuits",


    "Brioche": "Breads",
    "Sourdough Bread": "Breads",
    "Sourdough Bread (Eggless)": "Breads",
    "Sourdough Bread (eggless)": "Breads",


    "BESTSELLER PACK OF 2": "Hampers & Specials",
    "BESTSELLER PACK OF 2 (Eggless)": "Hampers & Specials",
    "BESTSELLER PACK OF 2 (eggless)": "Hampers & Specials",
    "Hamper : Decadent (Eggless)": "Hampers & Specials",
    "Hamper : Decadent (eggless)": "Hampers & Specials",
    "Hamper : Indulgent (Eggless)": "Hampers & Specials",
    "Hamper : Indulgent (eggless)": "Hampers & Specials",
    "Hamper : Luxurious (Eggless)": "Hampers & Specials",
    "Hamper : Luxurious (eggless)": "Hampers & Specials",
    "Hamper : Sumptuous (Eggless)": "Hampers & Specials",
    "Hamper : Sumptuous (eggless)": "Hampers & Specials",
    "Valentine's Hamper: Adore": "Hampers & Specials",
    "Rakhi special : Blooms Before Bickering": "Hampers & Specials",

    "Coffee": "Beverages & Jars",
    "Hot Chocolate Powder": "Beverages & Jars",
    "Hot chocolate powder": "Beverages & Jars",
    "Honey Mixed Dry Fruit Jar": "Beverages & Jars",
    "Honey mixed dry fruit jar": "Beverages & Jars",


    "Balloon pump": "Accessories",
    "Balloon Pump": "Accessories",
    "Birthday Balloons (Pack Of 15)": "Accessories",
    "Birthday balloons (Pack of 15)": "Accessories",
    "Birthday Banner": "Accessories",
    "Cake Toppers": "Accessories",
    "Cake toppers": "Accessories",
    "Candles": "Accessories",
    "Split delivery": "Accessories",


    "Autumn Serenade": "Artistic Specials",
    "Autumn serenade": "Artistic Specials",
    "Blush": "Artistic Specials",
    "Golden Hour": "Artistic Specials",
    "Golden hour": "Artistic Specials",
    "Mauve Season": "Artistic Specials",
    "Scarlett Whim": "Artistic Specials",
    "Scarlett whim": "Artistic Specials",
    "Sun Drenched": "Artistic Specials",
    "Sun drenched": "Artistic Specials",
}

dndf["category"] = dndf["Product_name"].map(product_category)
revcat = dndf.groupby("category")["Revenue"].sum().reset_index().sort_values(by = "Revenue", ascending = False)
revcat["Revenue"] = revcat["Revenue"].round(2)
fig = px.treemap(revcat, path = ["category"], values=revcat["Revenue"])
fig.update_traces(
    texttemplate = "<b>%{label}</b><br>Revenue - %{value: .2f}<br>Margin -%{percentParent: .1%}",
    textinfo = "label+value+percent root"
)
st.plotly_chart(fig, use_container_width= False)

st.markdown('''<div class = "summary"><p>The revenue distribution is heavily dominated by the Cakes and Loaves category, which contributes nearly 89% of total revenue. This is followed by Brownies & Blondies (4.9%) and Cookies & Biscuits (2.9%), while other categories contribute marginally.This highlights that cakes and loaves are the primary revenue drivers, suggesting that customer preference and purchasing power are strongly centered around premium cake products, whereas smaller categories play only a supporting role in overall sales.</p></div>''',unsafe_allow_html= True)

st.markdown("***")

# ---------------------- Which marketing source drives the highest Revenue ------------------------------
st.markdown("### Which marketing source drives the highest revenue?")
ddf["source_origin"] = ddf["source_origin"].apply(lambda x: 'direct' if 'direct' in str(x).lower().strip() else x)
ddf["source_origin"] = ddf["source_origin"].apply(lambda x: 'instagram' if 'insta' in str(x).lower().strip() else x)
ddf["source_origin"] = ddf["source_origin"].apply(lambda x: 'facebook' if 'fb' in str(x).lower().strip() else x)
ddf["source_origin"] = ddf["source_origin"].apply(lambda x: 'yahoo' if 'yahoo' in str(x).lower().strip() else x)
ddf["source_origin"] = ddf["source_origin"].apply(lambda x: 'youtube' if 'youtube' in str(x).lower().strip() else x)
ddf["source_origin"] = ddf["source_origin"].apply(lambda x: 'chatgpt' if 'chatgpt'in str(x).lower().strip() else x)
ddf["source_origin"] = ddf["source_origin"].apply(lambda x: 'google' if 'google' in str(x).lower().strip() else x)
ddf["source_origin"] = ddf["source_origin"].apply(lambda x: 'bing' if 'bing' in str(x).lower().strip() else x)
ddf["source_origin"] = ddf["source_origin"].apply(lambda x: 'cdn' if 'cdn' in str(x).lower().strip() else x)
ddf["source_origin"] = ddf["source_origin"].apply(lambda x: 'duckduckgo' if 'duck' in str(x).lower().strip() else x)
ddf["source_origin"] = ddf["source_origin"].apply(lambda x: 'others' if 'available' in str(x).lower().strip() else x)
marketingsource = ddf.groupby("source_origin")["subtotal"].sum().reset_index().sort_values(by = "subtotal", ascending = False).nlargest(10, "subtotal")
fig = px.bar(marketingsource, x = "source_origin", y = "subtotal", color = "source_origin")
fig.update_yaxes(
    type = 'log'
)
st.plotly_chart(fig, use_container_width= False)

st.markdown('''<div class = "summary"><p>Google as a channel contributes the highest revenue at ₹40M, far surpassing other sources such as Direct (₹7.7M), Facebook (₹1.6M), and Instagram (₹0.75M). However, since the “Google” category aggregates multiple platforms (e.g., Search, Display, YouTube), this dominance may actually reflect a combination of distinct sub-channels.</p></div>''',unsafe_allow_html= True)
st.markdown("***")

#--------------------------------What’s the trend in total orders and revenue over time----------------------------------------------
st.markdown("### Trends in Order and Revenue over time")
import plotly.graph_objects as go
from plotly.subplots import make_subplots


trends = ddf.groupby(ddf["event_date"].dt.date).agg({
    "user_pseudo_id": 'count',
    "subtotal": 'sum'
}).rename(columns={"user_pseudo_id":"total_purchase"}).reset_index()


fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(
    go.Scatter(
        x=trends["event_date"],
        y=trends["subtotal"],
        name="Subtotal",
        line=dict(color="red", width=3)
    ),
    secondary_y=False
)

fig.add_trace(
    go.Scatter(
        x=trends["event_date"],
        y=trends["total_purchase"],
        name="Total Purchase",
        line=dict(color="blue", width=3)
    ),
    secondary_y=True
)

fig.update_xaxes(title_text="Date")
fig.update_yaxes(title_text="Revenue", secondary_y=False)
fig.update_yaxes(title_text="Total Purchase", secondary_y=True)


fig.update_layout(
    legend=dict(x=0.85, y=1),
    template="plotly_white",
    height=600,
    width=1000
)
st.plotly_chart(fig, use_container_width= False)

st.markdown('''<div class = "summary"><p>The trend analysis shows that orders and revenue move proportionally over time — whenever the number of orders increases, revenue rises accordingly. Overall, sales have remained fairly consistent throughout the year, without any significant spikes or drops. This indicates a stable demand pattern, where growth in revenue is primarily order-driven rather than price fluctuations, suggesting steady customer purchasing behavior.</p></div>''',unsafe_allow_html= True)

#-------------------------------------trend decomposition------------------------------------------
st.markdown("#### Lets take a look on seasonal Decomposition ")
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import seasonal_decompose

daily = ddf.groupby("event_date")["subtotal"].sum().reset_index()
daily["event_date"] = pd.to_datetime(daily["event_date"])
daily.set_index("event_date", inplace = True)

decomposition = seasonal_decompose(daily["subtotal"], model = "additive", period = 7)

fig = make_subplots(rows = 4, cols = 1, shared_xaxes = True,
subplot_titles = ("Original", "Trend", "Seasonal", "Residual"))
fig.add_trace(go.Scatter(x = daily.index, y=daily["subtotal"], mode = "lines", name = 'Original', line = dict(color = '#2D2D2D')), row=1 , col=1)
fig.add_trace(go.Scatter(x = daily.index, y = decomposition.trend, mode = "lines", name = "Trend",line = dict(color = '#D72638')), row =2, col = 1)
fig.add_trace(go.Scatter(x = daily.index, y = decomposition.seasonal, mode = "lines", name = "Seasonal",line = dict(color = '#3A86FF')), row = 3, col = 1)
fig.add_trace(go.Scatter(x = daily.index, y = decomposition.resid, mode = "lines", name ="Residual",line = dict(color = '#FFBA08')), row = 4, col = 1)
fig.update_layout(height = 900, showlegend = True)
st.plotly_chart(fig, use_container_width= False)
st.markdown('''<div class = "summary"><p>From the seasonal decomposition, we observe that the seasonal component shows an upward trend between January and May, after which sales exhibit a slight downward or stable pattern. The noise component highlights sharp spikes in sales around specific dates such as 13 Feb, 10 May, 6 June, and 15 June, which align with festivals or weekends, indicating short-term demand surges.
This suggests that while the overall sales trend is steady with mild seasonality, special occasions and events act as key demand boosters, creating temporary spikes that businesses can strategically target with promotions.</p></div>''',unsafe_allow_html= True)
