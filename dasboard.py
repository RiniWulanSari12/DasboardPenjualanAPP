import streamlit as st
import pandas as pd
import plotly.express as px

# Fungsi untuk memuat data dengan caching
@st.cache_data
def load_data():
    products_dataset = pd.read_csv('products_dataset.csv')
    order_items_dataset = pd.read_csv('order_items_dataset.csv')
    # Mengonversi kolom shipping_limit_date ke tipe datetime
    order_items_dataset['shipping_limit_date'] = pd.to_datetime(order_items_dataset['shipping_limit_date'])
    return products_dataset, order_items_dataset

# Memuat data
products_dataset, order_items_dataset = load_data()

# Sidebar untuk filter
st.sidebar.header("Filter Data Penjualan")
year = st.sidebar.selectbox("Pilih Tahun", [2017, 2018], index=0)
category = st.sidebar.selectbox("Pilih Kategori Produk", ['Semua'] + list(products_dataset['product_category_name'].unique()))

# Pilihan jumlah produk yang akan ditampilkan
num_products = st.sidebar.slider("Pilih Jumlah Produk Teratas yang Ingin Ditampilkan", min_value=5, max_value=20, value=5, step=5)

# Filter berdasarkan tahun dan kategori
order_items_filtered = order_items_dataset[
    (order_items_dataset['shipping_limit_date'].dt.year == year) 
]

# Gabungkan data dengan nama produk
merged_data = order_items_filtered.merge(
    products_dataset[['product_id', 'product_category_name']],
    on='product_id'
)

# Filter berdasarkan kategori jika bukan 'Semua'
if category != 'Semua':
    merged_data = merged_data[merged_data['product_category_name'] == category]

# Menghitung total penjualan dan jumlah produk
total_sales = merged_data.groupby('product_category_name')['price'].sum().reset_index()

# Menampilkan Top produk teratas berdasarkan pilihan pengguna
top_products = total_sales.nlargest(num_products, 'price')

st.title(f"Dashboard Penjualan Produk Tahun {year}")
st.write(f"Kategori yang dipilih: {category if category != 'Semua' else 'Semua Kategori'}")

    # Menampilkan metrik penjualan
metric_col1, metric_col2 = st.columns(2)
with metric_col1:
        st.metric("Total Penjualan", f"Rp{total_sales['price'].sum():,.0f}")
with metric_col2:
        st.metric("Jumlah Kategori Terjual", f"{total_sales.shape[0]} kategori")

    # Menampilkan tabel produk dengan penjualan tertinggi
st.subheader(f"{num_products} Produk dengan Penjualan Tertinggi")
st.write(top_products)

    # Visualisasi menggunakan Plotly untuk grafik interaktif
fig = px.bar(
        top_products, 
        x='price', 
        y='product_category_name', 
        orientation='h', 
        title=f"Top {num_products} Produk Berdasarkan Penjualan",
        labels={'price': 'Total Penjualan (Rp)', 'product_category_name': 'Kategori Produk'},
        color='price', 
        color_continuous_scale='Blues'
    )

    # Membalik sumbu y agar produk teratas di atas
fig.update_layout(yaxis={'categoryorder':'total ascending'})

    # Menampilkan grafik
st.plotly_chart(fig)

# Menambahkan footer atau pesan tambahan di sidebar
st.sidebar.markdown("Silakan Pilih Sesuai dengan Kebutuhan!")
