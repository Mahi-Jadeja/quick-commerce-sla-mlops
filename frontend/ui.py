import os
import requests
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Quick-Commerce SLA Risk Operations",
    page_icon="⚡",
    layout="wide"
)

DEFAULT_API_URL = os.getenv("API_URL", "http://api:8000")

st.title("⚡ Quick-Commerce SLA Risk Management System")
st.markdown("Real-time Delivery Breach Risk Prediction & Dispatch Optimization Console")

st.sidebar.header("Configuration")
api_url = st.sidebar.text_input("API Base URL", value=DEFAULT_API_URL)

tab1, tab2, tab3 = st.tabs(["🎯 Single Order Risk Predictor", "📦 Batch Dispatch Evaluator", "📊 System Health & Metrics"])

with tab1:
    st.subheader("Single Delivery Order Parameters")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Rider Age", min_value=18, max_value=60, value=28)
        ratings = st.number_input("Rider Rating", min_value=1.0, max_value=5.0, value=4.5, step=0.1)
        distance = st.number_input("Delivery Distance (km)", min_value=0.1, max_value=50.0, value=7.5, step=0.1)
        weather = st.selectbox("Weather Condition", ["Sunny", "Stormy", "Sandstorms", "Windy", "Fog", "Cloudy"])
    
    with col2:
        traffic = st.selectbox("Road Traffic Density", ["Low", "Medium", "High", "Jam"])
        vehicle_cond = st.selectbox("Vehicle Condition Code", [0, 1, 2])
        order_type = st.selectbox("Order Type", ["Snack", "Meal", "Drinks", "Buffet"])
        vehicle_type = st.selectbox("Vehicle Type", ["scooter", "motorcycle", "electric_scooter", "bicycle"])
    
    with col3:
        deliveries = st.number_input("Multiple Deliveries in Trip", min_value=0, max_value=5, value=1)
        festival = st.selectbox("Festival Period?", ["No", "Yes"])
        city = st.selectbox("City Zone Type", ["Metropolitian", "Urban", "Semi-Urban"])
    
    if st.button("Predict SLA Breach Risk", type="primary"):
        payload = {
            "Delivery_person_Age": age,
            "Delivery_person_Ratings": ratings,
            "distance_km": distance,
            "Weatherconditions": weather,
            "Road_traffic_density": traffic,
            "Vehicle_condition": vehicle_cond,
            "Type_of_order": order_type,
            "Type_of_vehicle": vehicle_type,
            "multiple_deliveries": deliveries,
            "Festival": festival,
            "City": city
        }
        
        try:
            resp = requests.post(f"{api_url}/predict", json=payload, timeout=5)
            if resp.status_code == 200:
                result = resp.json()
                st.markdown("---")
                if result["will_breach_sla"] == 1:
                    st.error(f"⚠️ **HIGH SLA BREACH RISK DETECTED** (Probability: {result['sla_breach_probability']:.2%})")
                else:
                    st.success(f"✅ **ON-TIME DELIVERY EXPECTED** (SLA Breach Risk: {result['sla_breach_probability']:.2%})")
                
                st.info(f"**Actionable Dispatch Recommendation:** {result['recommendation']}")
            else:
                st.error(f"API Error {resp.status_code}: {resp.text}")
        except Exception as e:
            st.error(f"Failed to connect to API backend: {e}")

with tab2:
    st.subheader("Batch Order Dispatch Evaluation")
    st.markdown("Upload a CSV file containing multiple delivery orders for batch risk scoring.")
    
    uploaded_file = st.file_uploader("Choose CSV file", type=["csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.write("Uploaded Orders Preview:", df.head())
            
            if st.button("Run Batch Prediction"):
                orders = df.to_dict(orient="records")
                resp = requests.post(f"{api_url}/predict/batch", json={"orders": orders}, timeout=15)
                if resp.status_code == 200:
                    results = resp.json()
                    res_df = pd.DataFrame(results["predictions"])
                    st.success(f"Successfully processed {results['total_orders']} orders!")
                    st.dataframe(res_df)
                else:
                    st.error(f"Batch Processing Error: {resp.text}")
        except Exception as e:
            st.error(f"CSV Processing Error: {e}")

with tab3:
    st.subheader("System Health & ML Model Status")
    try:
        health_resp = requests.get(f"{api_url}/health", timeout=3)
        if health_resp.status_code == 200:
            h_data = health_resp.json()
            st.json(h_data)
        else:
            st.warning("Could not reach API health endpoint.")
    except Exception as e:
        st.error(f"API Connection Error: {e}")
