import streamlit as st
import pandas as pd

# Set up page configurations
st.set_page_config(page_title="Automotive Finance Calculator", layout="wide", initial_sidebar_state="expanded")

# --- 1. DATA LAYER (Extracted from your spreadsheet configurations) ---
VEHICLE_CATALOG = {
    "Attrage P": {"base_price": 50900, "category": "Sedan"},
    "Xpander HL P": {"base_price": 74500, "category": "SUV"},
    "ASX P": {"base_price": 73900, "category": "SUV"},
    "Outlander SP": {"base_price": 117400, "category": "SUV"},
    "Montero Premium": {"base_price": 125900, "category": "SUV"}
}

ACCESSORIES_CATALOG = [
    {"name": "Tinting Package", "default_price": 1200, "selected_by_default": False},
    {"name": "Alloy Wheels Upgrade", "default_price": 5900, "selected_by_default": False},
    {"name": "Exterior Ceramic Protection", "default_price": 5000, "selected_by_default": False},
    {"name": "Parking Sensors Integration", "default_price": 1500, "selected_by_default": False}
]

SUBVENTION_MULTIPLIERS = {2: 0.0000, 3: 0.0339, 4: 0.0678, 5: 0.1017}
STANDARD_INTEREST_RATE = 0.0299  # 2.99% flat rate structure from your May 2024 sheets

# --- 2. CORE FINANCIAL ENGINE ---
def calculate_deal(base_price, selected_accessories, down_payment_pct):
    # Total accessory accumulation
    total_acc_cost = sum([item['price'] for item in selected_accessories])
    
    # Capitalized structures
    net_value = base_price + total_acc_cost
    vat_charges = net_value * 0.05
    total_value = net_value + vat_charges
    
    # Funding structures
    down_payment = total_value * (down_payment_pct / 100)
    finance_amount = total_value - down_payment
    
    # Matrix calculation across tenures
    tenure_data = []
    for years in [2, 3, 4, 5]:
        months = years * 12
        
        # Standard Plan
        total_interest = finance_amount * STANDARD_INTEREST_RATE * years
        standard_emi = (finance_amount + total_interest) / months
        
        # Subvention Offer Plan
        sub_factor = SUBVENTION_MULTIPLIERS[years]
        subvention_discount = finance_amount * sub_factor
        subvention_emi = standard_emi - (subvention_discount / months)
        
        monthly_savings = standard_emi - subvention_emi
        
        tenure_data.append({
            "Tenure (Years)": f"{years} Years ({months} Mos)",
            "Standard EMI (AED)": f"{standard_emi:,.2f}",
            "Promotional EMI (AED)": f"{subvention_emi:,.2f}",
            "Monthly Savings (AED)": f"{monthly_savings:,.2f}",
            "Total Plan Interest (AED)": f"{total_interest:,.2f}"
        })
        
    return {
        "summary": {
            "base_price": base_price,
            "accessories_total": total_acc_cost,
            "net_value": net_value,
            "vat_charges": vat_charges,
            "total_value": total_value,
            "down_payment": down_payment,
            "finance_amount": finance_amount
        },
        "matrix": pd.DataFrame(tenure_data)
    }

# --- 3. INTERACTIVE WEB INTERFACE ---
st.title("🚗 Interactive Automotive Finance Deal Builder")
st.markdown("Modernized internal tool converting static portfolio matrices into dynamic quotation interfaces.")
st.divider()

# Sidebar Configuration Layout
st.sidebar.header("🛠️ Deal Configuration")

selected_model_name = st.sidebar.selectbox("Select Vehicle Model", list(VEHICLE_CATALOG.keys()))
model_base_price = VEHICLE_CATALOG[selected_model_name]["base_price"]

custom_base_price = st.sidebar.number_input(
    "Adjust Base Vehicle Value (AED)", 
    value=int(model_base_price), 
    step=500
)

st.sidebar.subheader("➕ Optional Add-ons & Accessories")
active_accessories = []
for acc in ACCESSORIES_CATALOG:
    is_selected = st.sidebar.checkbox(f"{acc['name']}", value=acc['selected_by_default'])
    price = st.sidebar.number_input(f"Cost for {acc['name']} (AED)", value=acc['default_price'], step=100, key=f"val_{acc['name']}")
    if is_selected:
        active_accessories.append({"name": acc['name'], "price": price})

down_payment_percentage = st.sidebar.slider("Down Payment Percentage (%)", min_value=10, max_value=80, value=20, step=5)

# Execute Engine Calculation Matrix
deal = calculate_deal(custom_base_price, active_accessories, down_payment_percentage)
summary = deal["summary"]

# Render Interface Layout
col1, col2 = st.columns([1, 1.8])

with col1:
    st.subheader("📊 Capitalization Summary")
    
    # Structured tabular data presentation
    summary_data = {
        "Financial Component": [
            "Base Vehicle Value", 
            "Total Accessories Cost", 
            "Net Value", 
            "VAT Charges (5%)", 
            "Gross Capitalized Value", 
            f"Down Payment ({down_payment_percentage}%)", 
            "Total Amount to Finance"
        ],
        "Value (AED)": [
            f"{summary['base_price']:,.2f}",
            f"{summary['accessories_total']:,.2f}",
            f"{summary['net_value']:,.2f}",
            f"{summary['vat_charges']:,.2f}",
            f"**{summary['total_value']:,.2f}**",
            f"**{summary['down_payment']:,.2f}**",
            f"**{summary['finance_amount']:,.2f}**"
        ]
    }
    st.table(pd.DataFrame(summary_data))

with col2:
    st.subheader("📉 Multi-Year Amortization Matrix")
    st.markdown("Comparison between standard banking packages and promotional subvention rates:")
    
    # Display table without index for a clean dashboard UI
    st.dataframe(deal["matrix"], use_container_width=True, hide_index=True)
    
    st.success(f"💡 **Deal Strategy Note:** Selecting the 5-Year promotional tenure drops monthly payments significantly while optimizing dealer subvention buffers.")

st.divider()
if st.button("🖨️ Export Quotation to PDF / Email Structure"):
    st.info("System integration hook: Ready to wire to a corporate PDF template generator or email client dispatch.")
