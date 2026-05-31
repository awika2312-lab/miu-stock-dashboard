import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Miu Stock Dashboard",
    layout="wide"
)

st.title("📊 Miu Stock Dashboard")

df = pd.DataFrame({
    "Ticker": ["NVDA", "RKLB"],
    "Company": [
        "NVIDIA Corporation",
        "Rocket Lab USA Inc."
    ],
    "Price": [100.00, 10.00]
})

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
