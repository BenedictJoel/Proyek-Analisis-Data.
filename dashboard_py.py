# -*- coding: utf-8 -*-
"""Dashboard.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1cbi2UZiCCscVQwnt-aUBrlF4FnK2Olfy
"""

pip install streamlit

!conda activate main-ds
!pip install streamlit babel

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_date').agg({
        "order_id": "nunique",
        "total_price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "total_price": "revenue"
    }, inplace=True)

    return daily_orders_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_name").quantity_x.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def create_bygender_df(df):
    bygender_df = df.groupby(by="gender").customer_id.nunique().reset_index()
    bygender_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)

    return bygender_df

def create_byage_df(df):
    byage_df = df.groupby(by="age_group").customer_id.nunique().reset_index()
    byage_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    byage_df['age_group'] = pd.Categorical(byage_df['age_group'], ["Youth", "Adults", "Seniors"])

    return byage_df

def create_bystate_df(df):
    bystate_df = df.groupby(by="state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)

    return bystate_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_date": "max", #mengambil tanggal order terakhir
        "order_id": "nunique",
        "total_price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_date"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df

all_df = pd.read_csv("/content/all_data.csv")

datetime_columns = ["order_approved_at", "order_delivered_customer_date"]
all_df.sort_values(by=datetime_columns[0], inplace=True) # Use the first column in datetime_columns for sorting
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = pd.to_datetime(all_df["order_purchase_timestamp"]).min().date()  # Convert to datetime, then extract date
max_date = pd.to_datetime(all_df["order_purchase_timestamp"]).max().date()  # Convert to datetime, then extract date

with st.sidebar:

    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")


    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) &
                (all_df["order_purchase_timestamp"] <= str(end_date))]

daily_orders_df = main_df.groupby('order_purchase_timestamp')['order_id'].count().reset_index()
daily_orders_df = daily_orders_df.rename(columns={'order_purchase_timestamp': 'order_date', 'order_id': 'order_count'})

st.header('Proyek Analisis Data :sparkles:')

try:
    orders_df = pd.read_csv('/mnt/data/E-commerce-public-dataset/olist_orders_dataset.csv')
    order_items_df = pd.read_csv('/mnt/data/E-commerce-public-dataset/olist_order_items_dataset.csv')
    st.success("Data berhasil dimuat!")
except Exception as e:
    st.error(f"Error saat membaca data: {e}")

# Langkah 2: Menggabungkan Dataset yang Relevan
try:
    merged_df = pd.merge(order_items_df, orders_df, on='order_id')
    st.success("Data berhasil digabungkan!")
except Exception as e:
    st.error(f"Error saat menggabungkan data: {e}")

# Langkah 3: Menghitung Jumlah Produk yang Terjual per Hari
try:
    merged_df['order_purchase_timestamp'] = pd.to_datetime(merged_df['order_purchase_timestamp'])
    merged_df['order_date'] = merged_df['order_purchase_timestamp'].dt.date
    daily_product_sales = merged_df.groupby('order_date').size().reset_index(name='product_count')
    st.success("Berhasil menghitung jumlah produk harian!")

    # Coba gunakan subset data
    subset_daily_product_sales = daily_product_sales.head(30)  # Menggunakan 30 hari pertama
except Exception as e:
    st.error(f"Error saat menghitung produk harian: {e}")

# Langkah 4: Visualisasi Data Menggunakan Streamlit
try:
    st.subheader('Daily Product Sales')

    # Display the data as metrics
    total_products = daily_product_sales['product_count'].sum()
    total_days = daily_product_sales['order_date'].nunique()

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Products Sold", value=total_products)

    with col2:
        st.metric("Total Days Recorded", value=total_days)

    # Plotting the data
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        subset_daily_product_sales["order_date"],  # Menggunakan subset data
        subset_daily_product_sales["product_count"],
        marker='o',
        linewidth=2,
        color="#90CAF9"
    )
    ax.set_title('Jumlah Produk yang Terjual Per Hari', fontsize=20)
    ax.set_xlabel('Tanggal', fontsize=15)
    ax.set_ylabel('Jumlah Produk Terjual', fontsize=15)
    ax.tick_params(axis='y', labelsize=12)
    ax.tick_params(axis='x', labelsize=12)
    plt.xticks(rotation=45)

    # Display the plot in Streamlit
    st.pyplot(fig)
    st.success("Visualisasi berhasil!")
except Exception as e:
    st.error(f"Error saat visualisasi: {e}")

try:
    products_df = pd.read_csv('/mnt/data/E-commerce-public-dataset/olist_products_dataset.csv')
    order_items_df = pd.read_csv('/mnt/data/E-commerce-public-dataset/olist_order_items_dataset.csv')
    st.success("Data berhasil dimuat!")
except Exception as e:
    st.error(f"Error saat membaca data: {e}")

# Langkah 2: Menghitung Jumlah Penjualan per Produk
try:
    # Gabungkan data pesanan dengan data item pesanan
    product_sales = order_items_df.groupby('product_id').size().reset_index(name='sales_count')

    # Menggabungkan dengan dataset produk untuk mendapatkan nama produk
    product_sales = pd.merge(product_sales, products_df[['product_id', 'product_category_name']], on='product_id')

    # Menghitung produk paling laris
    top_5_products = product_sales.sort_values(by='sales_count', ascending=False).head(5)

    # Menghitung produk paling sedikit terjual
    bottom_5_products = product_sales.sort_values(by='sales_count', ascending=True).head(5)

    st.success("Berhasil menghitung penjualan produk!")
except Exception as e:
    st.error(f"Error saat menghitung penjualan produk: {e}")

# Langkah 3: Visualisasi Produk Paling Laris dan Paling Sedikit Terjual
try:
    st.subheader('Top 5 Best-Selling Products')

    # Plotting 5 Produk Paling Laris
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(top_5_products['product_category_name'], top_5_products['sales_count'], color='green')
    ax.set_xlabel('Jumlah Terjual')
    ax.set_ylabel('Kategori Produk')
    ax.set_title('5 Produk Paling Laris')
    plt.gca().invert_yaxis()  # Membalikkan sumbu Y agar produk terlaris di atas

    st.pyplot(fig)

    st.subheader('Top 5 Least-Selling Products')

    # Plotting 5 Produk Paling Sedikit Terjual
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(bottom_5_products['product_category_name'], bottom_5_products['sales_count'], color='red')
    ax.set_xlabel('Jumlah Terjual')
    ax.set_ylabel('Kategori Produk')
    ax.set_title('5 Produk Paling Sedikit Terjual')
    plt.gca().invert_yaxis()  # Membalikkan sumbu Y agar produk dengan penjualan terendah di atas

    st.pyplot(fig)

    st.success("Visualisasi berhasil!")
except Exception as e:
    st.error(f"Error saat visualisasi: {e}")

daily_product_sales = pd.DataFrame({
    'order_date': pd.date_range(start='2023-01-01', periods=30, freq='D'),
    'product_count': range(1, 31)
})

# Subset data (gunakan seluruh data jika tidak ada masalah dengan kinerja)
subset_daily_sales = daily_product_sales.head(30)  # Coba dengan hanya 30 data pertama

# Matplotlib Visualization
st.subheader('Daily Product Sales (Matplotlib)')
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    subset_daily_sales["order_date"],
    subset_daily_sales["product_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
plt.xticks(rotation=45)
plt.tight_layout()

# Debugging untuk melihat apakah fig terdefinisi dengan benar
st.write("Rendering the plot with Matplotlib...")
st.write(fig)

# Tampilkan plot dengan plt.show() terlebih dahulu (opsional)
plt.show()

# Kemudian tampilkan dengan Streamlit
st.pyplot(fig)

daily_product_sales = pd.DataFrame({
    'order_date': pd.date_range(start='2023-01-01', periods=30, freq='D'),
    'product_count': range(1, 31)
})

# Contoh data untuk 5 produk terlaris dan paling sedikit terjual
product_sales = pd.DataFrame({
    'product_name': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'],
    'sales_count': [150, 120, 110, 30, 20]
})

top_products = product_sales.sort_values('sales_count', ascending=False).head(5)
bottom_products = product_sales.sort_values('sales_count', ascending=True).head(5)

# 1. Visualisasi Daily Product Sales menggunakan Matplotlib
st.subheader('Daily Product Sales (Matplotlib)')
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    daily_product_sales["order_date"],
    daily_product_sales["product_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)

# 2. Visualisasi Daily Product Sales menggunakan Altair
st.subheader('Daily Product Sales (Altair)')
chart = alt.Chart(daily_product_sales).mark_line(point=True).encode(
    x='order_date:T',
    y='product_count:Q'
).properties(
    width=600,
    height=300
)
st.altair_chart(chart, use_container_width=True)


st.subheader('Top 5 Best Selling Products')
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(top_products['product_name'], top_products['sales_count'], color='green')
plt.xlabel('Sales Count')
plt.ylabel('Product Name')
plt.title('Top 5 Best Selling Products')
plt.tight_layout()
st.pyplot(fig)

st.subheader('Bottom 5 Least Selling Products')
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(bottom_products['product_name'], bottom_products['sales_count'], color='red')
plt.xlabel('Sales Count')
plt.ylabel('Product Name')
plt.title('Bottom 5 Least Selling Products')
plt.tight_layout()
st.pyplot(fig)

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# Contoh data
daily_product_sales = pd.DataFrame({
    'order_date': pd.date_range(start='2023-01-01', periods=30, freq='D'),
    'product_count': range(1, 31)
})

# Membuat grafik menggunakan Matplotlib
st.subheader('Daily Product Sales (Matplotlib)')
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    daily_product_sales["order_date"],
    daily_product_sales["product_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
plt.xticks(rotation=45)
plt.tight_layout()

# Menampilkan grafik dengan Streamlit
st.pyplot(fig)

import matplotlib.pyplot as plt
import pandas as pd

# Contoh data
daily_product_sales = pd.DataFrame({
    'order_date': pd.date_range(start='2023-01-01', periods=30, freq='D'),
    'product_count': range(1, 31)
})

# Membuat grafik menggunakan Matplotlib
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    daily_product_sales["order_date"],
    daily_product_sales["product_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
plt.xticks(rotation=45)
plt.tight_layout()

# Simpan grafik ke file
fig.savefig("output.png")

# Menampilkan gambar di Streamlit
import streamlit as st
st.image("output.png")

!pip freeze > requirements.txt

!pip install session-info

!pipreqs