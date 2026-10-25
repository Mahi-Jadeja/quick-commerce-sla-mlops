import json
import requests
import pandas as pd
import streamlit as st
from pathlib import Path

# Page Config
st.set_page_config(
    page_title="Quick-Commerce SLA Risk Operations Console",
    page_icon="⚡",
    layout="wide",
)

# Custom Styling
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; }
    .sub-header { font-size: 1.1rem; color: #4B5563; }
    .metric-card { background-color: #F3F4F6; padding: 1rem; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">⚡ Quick-Commerce SLA Risk Management Console</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Real-time 30-Minute Delivery Breach Risk Prediction & Operational Dispatch System</div>', unsafe_allow_html=True)
st.divider()

# Sidebar Config
st.sidebar.title("🛠️ Microservice Config")
api_base_url = st.sidebar.text_input("FastAPI Backend URL", value="http://localhost:8000")

# Check Health
try:
    health_resp = requests.get(f"{api_base_url}/health", timeout=3)
    if health_resp.status_code == 200:
        health_data = health_resp.json()
        st.sidebar.success(f"🟢 API Online | Source: {health_data.get('model_source', 'S3')}")
    else:
        st.sidebar.error("🔴 API Unhealthy")
except Exception:
    st.sidebar.warning("⚠️ API Connection Offline. Ensure FastAPI service is running on port 8000.")

tabs = st.tabs(["🚀 Single Order Risk Evaluator", "📦 Batch Order Dispatch Inspector", "📊 Model Performance Dashboard"])

# TAB 1: Single Order
with tabs[0]:
    st.subheader("Evaluate Individual Delivery SLA Breach Risk")
    col1, col2, col3 = st.columns(3)

    with col1:
        age = st.number_input("Rider Age", min_value=18, max_value=65, value=28)
        ratings = st.slider("Rider Rating", min_value=1.0, max_value=5.0, value=4.7, step=0.1)
        distance = st.number_input("Delivery Distance (km)", min_value=0.1, max_value=50.0, value=4.5, step=0.1)
        multiple_deliveries = st.selectbox("Concurrent Deliveries Assigned", options=[0.0, 1.0, 2.0, 3.0], index=0)

    with col2:
        weather = st.selectbox("Weather Conditions", options=["Sunny", "Stormy", "Sandstorms", "Windy", "Fog", "Cloudy"])
        traffic = st.selectbox("Road Traffic Density", options=["Low", "Medium", "High", "Jam"])
        vehicle_cond = st.selectbox("Vehicle Condition Index", options=[0, 1, 2], index=2)

    with col3:
        order_type = st.selectbox("Order Type", options=["Snack", "Meal", "Drinks", "Buffet"])
        vehicle_type = st.selectbox("Vehicle Type", options=["motorcycle", "scooter", "electric_scooter", "bicycle"])
        festival = st.selectbox("Festival Period", options=["No", "Yes"])
        city = st.selectbox("City Category", options=["Metropolitian", "Urban", "Semi-Urban"])

    if st.button("⚡ Evaluate Delivery SLA Risk", type="primary", use_container_width=True):
        payload = {
            "Delivery_person_Age": float(age),
            "Delivery_person_Ratings": float(ratings),
            "distance_km": float(distance),
            "Weatherconditions": weather,
            "Road_traffic_density": traffic,
            "Vehicle_condition": int(vehicle_cond),
            "Type_of_order": order_type,
            "Type_of_vehicle": vehicle_type,
            "multiple_deliveries": float(multiple_deliveries),
            "Festival": festival,
            "City": city,
        }

        try:
            resp = requests.post(f"{api_base_url}/predict", json=payload, timeout=5)
            if resp.status_code == 200:
                result = resp.json()
                st.divider()
                
                res_col1, res_col2, res_col3 = st.columns(3)
                
                risk_level = result["risk_level"]
                proba = result["sla_breach_probability"] * 100
                will_breach = result["will_breach_sla"]

                if risk_level == "HIGH":
                    res_col1.error(f"🚨 Risk Level: {risk_level}")
                elif risk_level == "MEDIUM":
                    res_col1.warning(f"⚠️ Risk Level: {risk_level}")
                else:
                    res_col1.success(f"✅ Risk Level: {risk_level}")

                res_col2.metric("SLA Breach Probability", f"{proba:.1f}%")
                res_col3.metric("Predicted Status", "Breach (>30m)" if will_breach == 1 else "On-Time (≤30m)")

                st.info(f"💡 **Operational Recommendation:** {result['recommendation']}")
            else:
                st.error(f"API Error {resp.status_code}: {resp.text}")
        except Exception as e:
            st.error(f"Failed to connect to API backend: {e}")

# TAB 2: Batch Inspection
with tabs[1]:
    st.subheader("Batch Order Dispatch SLA Inspector")
    st.write("Upload a CSV file containing multiple delivery orders to evaluate SLA breach risk in batch.")
    
    sample_csv = pd.DataFrame([{
        "Delivery_person_Age": 28.0, "Delivery_person_Ratings": 4.7, "distance_km": 4.5,
        "Weatherconditions": "Sunny", "Road_traffic_density": "Low", "Vehicle_condition": 2,
        "Type_of_order": "Snack", "Type_of_vehicle": "motorcycle", "multiple_deliveries": 0.0,
        "Festival": "No", "City": "Metropolitian"
    }, {
        "Delivery_person_Age": 22.0, "Delivery_person_Ratings": 3.8, "distance_km": 12.0,
        "Weatherconditions": "Stormy", "Road_traffic_density": "Jam", "Vehicle_condition": 0,
        "Type_of_order": "Meal", "Type_of_vehicle": "scooter", "multiple_deliveries": 2.0,
        "Festival": "Yes", "City": "Metropolitian"
    }])

    st.download_button("📥 Download Sample Batch Template CSV", data=sample_csv.to_csv(index=False), file_name="batch_delivery_template.csv", mime="text/csv")

    uploaded_file = st.file_uploader("Upload Batch CSV", type=["csv"])
    if uploaded_file is not None:
        batch_df = pd.read_csv(uploaded_file)
        st.write("Uploaded Batch Preview:", batch_df.head())

        if st.button("⚡ Run Batch SLA Inspection", type="primary"):
            orders_payload = {"orders": batch_df.to_dict(orient="records")}
            try:
                resp = requests.post(f"{api_base_url}/predict/batch", json=orders_payload, timeout=10)
                if resp.status_code == 200:
                    results = resp.json()
                    res_df = pd.DataFrame(results)
                    output_df = pd.concat([batch_df, res_df], axis=1)
                    
                    st.success(f"Batch evaluation complete! Inspected {len(output_df)} orders.")
                    st.dataframe(output_df)
                    st.download_button("📥 Download Results CSV", data=output_df.to_csv(index=False), file_name="sla_risk_batch_results.csv", mime="text/csv")
                else:
                    st.error(f"Batch API Error: {resp.text}")
            except Exception as e:
                st.error(f"Batch Connection Error: {e}")

# TAB 3: Model Performance
with tabs[2]:
    st.subheader("Model Evaluation Summary & Benchmarks")
    metrics_path = Path("metrics.json")
    if metrics_path.exists():
        with open(metrics_path, "r") as f:
            metrics_data = json.load(f)
        
        st.write(f"🏆 **Champion Model:** `{metrics_data.get('best_model', 'LightGBM')}`")
        st.write(f"📈 **Best ROC-AUC Score:** `{metrics_data.get('best_roc_auc', 0.0):.4f}`")

        model_metrics = metrics_data.get("metrics_by_model", {})
        df_metrics = pd.DataFrame(model_metrics).T
        st.dataframe(df_metrics.style.highlight_max(axis=0, color="#D1FAE5"))
    else:
        st.info("No `metrics.json` file found. Run model training (`python -m src.train`) to populate statistics.")
