import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

# Fungsi untuk membaca data
def load_data():
    data_dir = Path("data/")
    csv_files = list(data_dir.glob("*.csv"))
    df_list = []
    for file in csv_files:
        try:
            df = pd.read_csv(file, parse_dates=["dteday"])
            df["year"] = df["dteday"].dt.year
            df["month"] = df["dteday"].dt.month
            df["day"] = df["dteday"].dt.day
            if "hr" in df.columns:
                df["DateTime"] = pd.to_datetime(df["dteday"]) + pd.to_timedelta(df["hr"], unit="h")
            df_list.append(df)
        except Exception as e:
            st.error(f"Failed to read {file.name}: {e}")
    return pd.concat(df_list, ignore_index=True) if df_list else None

# Load data
df = load_data()

# Sidebar navigation
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["Home", "Dataset", "Pertanyaan Satu", "Pertanyaan Dua", "Binning", "Kesimpulan"])

# Home Page
if menu == "Home":
    st.title("Proyek Analisis Data: Bike Sharing Dataset")

# Dataset Page
elif menu == "Dataset":
    st.title("Dataset Overview")
    if df is not None:
        st.write(df.head())
        st.write("### Statistik Dataset")
        st.write(df.describe())
        
        # Visualisasi Distribusi Tahun
        st.write("### Distribusi Tahun")
        fig, ax = plt.subplots()
        sns.countplot(x="year", data=df, ax=ax)
        st.pyplot(fig)
    else:
        st.error("Data tidak tersedia.")

# Pertanyaan Satu
elif menu == "Pertanyaan Satu":
    st.title("Hari apa yang biasanya memiliki rata-rata rental sepeda terbanyak per minggu?")
    
    # Langsung analisis dan visualisasi
    rental_per_day = df.groupby("weekday")["cnt"].mean().reset_index()
    day_mapping = {0: "Sunday", 1: "Monday", 2: "Tuesday", 
                   3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday"}
    rental_per_day["weekday"] = rental_per_day["weekday"].map(day_mapping)
    rental_per_day = rental_per_day.sort_values("cnt", ascending=False)
    
    # Visualisasi rata-rata peminjaman sepeda per hari
    plt.figure(figsize=(10, 6))
    sns.barplot(x="weekday", y="cnt", data=rental_per_day, palette="Blues_r")
    plt.title("Rerata Peminjaman Sepeda Setiap Hari per Minggu")
    plt.xlabel("Hari")
    plt.ylabel("Rerata Rental")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)
    
    # Menampilkan hari tersibuk dan hari senggang
    busiest_day = rental_per_day.iloc[0]['weekday']
    max_count = rental_per_day.iloc[0]['cnt']
    selo_kang_day = rental_per_day.iloc[-1]['weekday']
    min_count = rental_per_day.iloc[-1]['cnt']
    
    st.write(f"Hari tersibuk: **{busiest_day}** dengan rerata **{max_count:.0f}** peminjaman")
    st.write(f"Hari senggang: **{selo_kang_day}** dengan rerata **{min_count:.0f}** peminjaman")
    
    # Penjelasan
    st.markdown("""**Analisis:**  
- Hari **{busiest_day}** memiliki rata-rata peminjaman sepeda tertinggi, menunjukkan bahwa hari yang terbanyak peminjamannya dalam seminggu untuk rental sepeda.
- Sebaliknya, hari **{selo_kang_day}** memiliki rata-rata peminjaman sepeda terendah.
- Kebanyakan peminjaman sepeda terjadi ketika hari kerja.
    """.format(busiest_day=busiest_day, selo_kang_day=selo_kang_day))
    
# Pertanyaan Dua
elif menu == "Pertanyaan Dua":
    st.title("Pertanyaan Dua")
    st.write("Analisis dan jawaban untuk pertanyaan kedua.")

    # Langsung analisis dan visualisasi
    rental_per_hour = df.groupby("hr")["cnt"].min().reset_index()
    
    # Visualisasi rata-rata peminjaman sepeda per jam
    plt.figure(figsize=(10, 6))
    sns.lineplot(x="hr", y="cnt", data=rental_per_hour, marker="o")
    plt.title("Rerata Peminjaman Sepeda Setiap Jam dalam Sehari")
    plt.xlabel("Jam")
    plt.ylabel("Rerata Rental")
    plt.tight_layout()
    st.pyplot(plt)
    
    # Menampilkan jam tersibuk dan jam senggang
    peak_hour = rental_per_hour.loc[rental_per_hour["cnt"].idxmax()]
    min_hour = rental_per_hour.loc[rental_per_hour["cnt"].idxmin()]
    
    st.write(f"Jam tersibuk: **{int(peak_hour['hr']):02d}:00** dengan rerata **{peak_hour['cnt']:.0f}** peminjaman")
    st.write(f"Jam senggang: **{int(min_hour['hr']):02d}:00** dengan rerata **{min_hour['cnt']:.0f}** peminjaman")
    
    # Penjelasan
    st.markdown("""**Analisis:**  
- Jam **{peak_hour}:00** memiliki rata-rata peminjaman sepeda tertinggi, menunjukkan bahwa jam tersebut adalah waktu tersibuk dalam sehari untuk rental sepeda.
- Sebaliknya, jam **{min_hour}:00** memiliki rata-rata peminjaman sepeda terendah.
- Peminjaman sepeda cenderung meningkat pada jam-jam sibuk seperti pagi dan sore hari.
    """.format(peak_hour=int(peak_hour['hr']), min_hour=int(min_hour['hr'])))

# Binning Analysis
elif menu == "Binning":
    st.title("Binning Analysis")

    # Tambahkan fungsi analyze_rental_categories
    def analyze_rental_categories(df):
        bins = [0, 500, 2000, df["cnt"].max()]
        labels = ["Low", "Medium", "High"]
        df["rental_category"] = pd.cut(df["cnt"], bins=bins, labels=labels)

        plt.figure(figsize=(10, 5))
        sns.countplot(x="rental_category", data=df, palette="coolwarm")
        plt.title("Distribution of Bike Rental Categories")
        plt.xlabel("Category")
        plt.ylabel("Number of Days")
        plt.tight_layout()
        st.pyplot(plt)

        category_counts = df["rental_category"].value_counts()
        st.write("### Count of Days per Rental Category")
        for category, count in category_counts.items():
            st.write(f"{category}: {count:,} days")

    # Call analyze_rental_categories function
    analyze_rental_categories(df)
    st.markdown("""
- Kebanyakan penyewaan sepeda setiap harinya dibawah 500 count, yang dikategorikan low, dengan total 16,103 hari
- Distribusi kategori penyewaan sepeda menunjukkan pola yang jelas di mana penyewaan sepeda lebih sering terjadi pada tingkat rendah daripada tingkat sedang atau tinggi.
    """)

# Kesimpulan
elif menu == "Kesimpulan":
    st.title("Kesimpulan")
    
    st.write("- Pagi hari (08:00 - 10:00) dan sore hari (17:00 - 19:00) adalah waktu dengan jumlah rental sepeda tertinggi. Pola ini menunjukkan bahwa sepeda sering digunakan sebagai alat transportasi untuk berangkat kerja atau sekolah.")
    st.write("- Pada malam hari, jumlah rental cenderung menurun, mungkin karena aktivitas utama berlangsung di tempat kerja atau sekolah.")
    st.write("- Pada akhir pekan cenderung menurun dikarenakan mungkin peminjaman sepeda dilakukan untuk aktivitas di tempat kerja atau sekolah.")