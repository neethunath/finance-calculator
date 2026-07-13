import streamlit as st
import pandas as pd
import numpy as np
import os
import io

st.set_page_config(page_title="Mitsubishi Finance Calculator", layout="wide")

# ------------------------------------------------------------------
# AUTOMATIC EXCEL DATA EXTRACTION ENGINE
# ------------------------------------------------------------------
@st.cache_data
def load_all_vehicle_data(file_path):
    if not os.path.exists(file_path):
        return {}
    
    xls = pd.ExcelFile(file_path)
    catalog = {}
    
    for sheet in xls.sheet_names:
        if sheet in ['Structure', 'MY-2025', 'MY-2026']:
            continue
            
        try:
            df = pd.read_excel(xls, sheet_name=sheet, header=None)
            
            # Extract Model Information from Row 4
            model_name = str(df.iloc[4, 2]).strip()  # Cell C5
            
            if not model_name or model_name == "nan":
                model_name = sheet
                
            year = "2026" if sheet.endswith("26") else "2025"
            display_label = f"{model_name} ({year})"
            
            # Extract Values from Row 6 and Row 18
            base_price = float(df.iloc[6, 1])          # Cell B7
            vat_charges = float(df.iloc[6, 5])         # Cell F7
            interest_rate = float(df.iloc[18, 3])       # Cell D19
            
            # Extract Accessories Dynamic Matrix (Rows 10 to 15)
            accessories = {}
            for r_idx in range(10, 16):
                acc_name = str(df.iloc[r_idx, 1]).strip()
                acc_status = str(df.iloc[r_idx, 2]).strip().upper()
                try:
                    acc_val = float(df.iloc[r_idx, 3])
                except:
                    acc_val = 0.0
                
                if acc_name and acc_name != "nan":
                    accessories[acc_name] = {
                        "price": acc_val,
                        "default_checked": True if acc_status == "YES" else False
                    }
            
            catalog[display_label] = {
                "base_price": base_price,
                "interest_rate": interest_rate,
                "vat_charges": vat_charges,
                "accessories": accessories,
                "year": year
            }
        except Exception as e:
            continue
            
    return catalog

# Load the catalog dataset
EXCEL_FILE = "NFC New VRI Project (2).xlsx"
VEHICLE_CATALOG = load_all_vehicle_data(EXCEL_FILE)

# ------------------------------------------------------------------
# INTERFACE LAYOUT (SIDEBAR FOR CONTROLS)
# ------------------------------------------------------------------
if not VEHICLE_CATALOG:
    st.error(f"Could not find or load '{EXCEL_FILE}' in your repository directory.")
else:
    # --- SIDEBAR: ALL CONFIGURATION DROPDOWNS & INPUTS ---
    with st.sidebar:
        st.header("🚗 Vehicle Configuration")
        
        sorted_options = sorted(list(VEHICLE_CATALOG.keys()))
        selected_variant = st.selectbox("Select Model Variant:", sorted_options)
        
        # Get sheet values for default fallback values
        v_data = VEHICLE_CATALOG[selected_variant]
        
        base_vehicle_price = st.number_input("Base Price (AED):", value=v_data["base_price"], step=500.0)
        bank_rate = st.number_input("Flat Interest Rate:", value=v_data["interest_rate"], format="%.4f", step=0.0001)
        
        down_payment_pct = st.slider("Down Payment Percentage (%):", 0, 100, 20) / 100.0
        calculated_downpayment = base_vehicle_price * down_payment_pct
        st.write(f"**Down Payment Amount:** {calculated_downpayment:,.2f} AED")
        
        st.markdown("---")
        st.header("➕ Add-ons & Accessories")
        selected_addons_total = 0.0
        
        for addon_name, info in v_data["accessories"].items():
            is_checked = st.checkbox(
                f"{addon_name} (+{info['price']:,.0f} AED)", 
                value=info["default_checked"]
            )
            if is_checked:
                selected_addons_total += info["price"]

    # --- MAIN AREA: CLEAN DATA TABLE & EXPORT ---
    st.title("Mitsubishi Financial Matrix Calculator")
    st.markdown(f"### Currently Viewing: **{selected_variant}**")
    st.markdown("---")
    
    # Financial Formula Calculation Engine
    total_financed_amount = (base_vehicle_price + selected_addons_total) - calculated_downpayment
    
    tenures = [2, 3, 4, 5]
    emi_results = []
    
    for years in tenures:
        months = years * 12
        total_interest = total_financed_amount * bank_rate * years
        total_repayable = total_financed_amount + total_interest
        monthly_emi = total_repayable / months
        
        emi_results.append({
            "Tenure Period": f"{years} Years ({months} Months)",
            "Financed Principal (AED)": round(total_financed_amount, 2),
            "Total Interest (AED)": round(total_interest, 2),
            "Estimated Monthly EMI (AED)": round(monthly_emi, 2)
        })
        
    df_output = pd.DataFrame(emi_results)
    
    # Format numbers visually for display inside the table
    df_display = df_output.copy()
    df_display["Financed Principal (AED)"] = df_display["Financed Principal (AED)"].map('{:,.2f}'.format)
    df_display["Total Interest (AED)"] = df_display["Total Interest (AED)"].map('{:,.2f}'.format)
    df_display["Estimated Monthly EMI (AED)"] = df_display["Estimated Monthly EMI (AED)"].map('{:,.2f}'.format)
    
    # Display the clean table in the main panel
    st.table(df_display)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- EXPORT FUNCTIONALITY ---
    # Create an in-memory buffer to save the generated excel bytes safely
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_output.to_excel(writer, index=False, sheet_name="EMI Matrix")
    
    st.download_button(
        label="📥 Export Financial Matrix to Excel",
        data=buffer.getvalue(),
        file_name=f"Finance_Matrix_{selected_variant.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
