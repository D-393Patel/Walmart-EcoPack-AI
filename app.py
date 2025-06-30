import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt # For visualizations
import numpy as np # For numerical operations, though pandas handles most here

# Import functions from your core_logic.py
from core_logic import (
    PRODUCTS_DF, MATERIALS_DF, get_product_data,
    calculate_optimal_single_box, calculate_approximate_multi_box,
    recommend_sustainable_material, get_mock_current_packaging, get_mock_current_multi_packaging
)

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Walmart Eco-Pack AI",
    layout="wide", # Use wide layout for more space
    initial_sidebar_state="expanded"
)

# --- Header Section ---
st.title("📦 Walmart Eco-Pack AI Assistant")
st.markdown("""
    **Transforming Packaging at Walmart for a Sustainable and Efficient Future.**
    
    Walmart has set ambitious goals for packaging sustainability, aiming for **100% recyclable, reusable, or industrially compostable private brand packaging by 2025**, and a **15% reduction in virgin plastic**. However, recent reports indicate the company is **currently falling short** of these targets, with virgin plastic use increasing and only 68% of packaging meeting recyclability goals.
    
    The **Walmart Eco-Pack AI** directly addresses these critical challenges by intelligently optimizing package dimensions and recommending highly sustainable materials. This leads to **significant cost savings, a reduced environmental footprint, and enhanced brand reputation.**
""")

st.markdown("---")

# --- Sidebar for Product Selection ---
st.sidebar.header("🛒 Order Builder")
all_product_names = PRODUCTS_DF['name'].tolist()
selected_products_names = st.sidebar.multiselect(
    "**Select products for your order:**",
    options=all_product_names,
    default=[] # No default selection
)

# Convert selected product names back to product IDs for core logic
selected_product_ids = PRODUCTS_DF[PRODUCTS_DF['name'].isin(selected_products_names)]['product_id'].tolist()

st.sidebar.markdown("---")
st.sidebar.info("""
    **How it works:**
    1. Select products for an order.
    2. Eco-Pack AI calculates optimal box dimensions.
    3. Recommends the most sustainable, yet strong and cost-effective, packaging materials.
    4. Shows estimated savings and environmental impact.
""")

st.sidebar.markdown("---")
st.sidebar.subheader("🚀 Eco-Pack AI Controls")
cost_tolerance = st.sidebar.slider(
    "Cost Tolerance for Sustainable Materials:",
    min_value=1.0, max_value=1.5, value=1.2, step=0.05,
    help="How much more expensive can a sustainable material be compared to the cheapest suitable one? (e.g., 1.2 = 20% more expensive)"
)


# --- Main Content Area ---
if not selected_product_ids:
    st.image(
    "./static/animation.gif", # <--- CHANGE THIS FILENAME to your GIF
    use_container_width=True,
    caption="Watch Eco-Pack AI optimize your orders!" # A caption fitting animation
)
    st.info("👈 Please select one or more products from the sidebar to see Eco-Pack AI recommendations.")
else:
    st.header("✨ Eco-Pack AI Recommendations")

    st.subheader("1. Selected Order Overview:")
    selected_products_df_display = PRODUCTS_DF[PRODUCTS_DF['product_id'].isin(selected_product_ids)].reset_index(drop=True)
    st.dataframe(selected_products_df_display[['name', 'length_cm', 'width_cm', 'height_cm', 'weight_kg', 'fragility_score']])

    st.markdown("---")

    # --- Packaging Volume Optimization ---
    st.subheader("2. Packaging Volume Optimization (Right-Sizing)")
    
    col1, col2 = st.columns(2)

    optimal_box_info = {}
    current_box_info = {}
    volume_reduction_percent = 0

    if len(selected_product_ids) == 1:
        product_id = selected_product_ids[0]
        product = get_product_data(product_id)
        
        # Optimal
        opt_l, opt_w, opt_h, opt_vol = calculate_optimal_single_box(
            product['length_cm'], product['width_cm'], product['height_cm']
        )
        optimal_box_info = {'L': opt_l, 'W': opt_w, 'H': opt_h, 'Volume': opt_vol}

        # Current (Mock)
        current_pkg = get_mock_current_packaging(product_id)
        current_box_info = {'L': current_pkg['length'], 'W': current_pkg['width'], 'H': current_pkg['height'], 'Volume': current_pkg['volume']}

        if current_pkg['volume'] > 0:
            volume_reduction_percent = ((current_pkg['volume'] - opt_vol) / current_pkg['volume']) * 100
        
        with col1:
            st.markdown(f"**Optimal Box for '{product['name']}'**")
            st.info(f"Dimensions: {opt_l:.1f}x{opt_w:.1f}x{opt_h:.1f} cm")
            st.metric("Volume", f"{opt_vol:.1f} cm³")
        
        with col2:
            st.markdown(f"**Estimated Current Box for '{product['name']}'**")
            st.warning(f"Dimensions: {current_pkg['length']:.1f}x{current_pkg['width']:.1f}x{current_pkg['height']:.1f} cm")
            st.metric("Volume", f"{current_pkg['volume']:.1f} cm³")

    else: # Multi-item order
        # Optimal (approximate)
        opt_l, opt_w, opt_h, opt_vol = calculate_approximate_multi_box(selected_product_ids)
        optimal_box_info = {'L': opt_l, 'W': opt_w, 'H': opt_h, 'Volume': opt_vol}

        # Current (Mock)
        current_pkg = get_mock_current_multi_packaging(selected_product_ids)
        current_box_info = {'L': current_pkg['length'], 'W': current_pkg['width'], 'H': current_pkg['height'], 'Volume': current_pkg['volume']}

        if current_pkg['volume'] > 0:
            volume_reduction_percent = ((current_pkg['volume'] - opt_vol) / current_pkg['volume']) * 100
        
        with col1:
            st.markdown(f"**Optimal Box for {len(selected_product_ids)} items**")
            st.info(f"Dimensions: {opt_l:.1f}x{opt_w:.1f}x{opt_h:.1f} cm")
            st.metric("Volume", f"{opt_vol:.1f} cm³")
        
        with col2:
            st.markdown(f"**Estimated Current Box for {len(selected_product_ids)} items**")
            st.warning(f"Dimensions: {current_pkg['length']:.1f}x{current_pkg['width']:.1f}x{current_pkg['height']:.1f} cm")
            st.metric("Volume", f"{current_pkg['volume']:.1f} cm³")
    
    st.markdown("---")
    st.subheader("Volume Reduction Visual:")
    
    # Create a simple bar chart for volume comparison
    volumes = [current_box_info['Volume'], optimal_box_info['Volume']]
    labels = ['Current Volume', 'Optimal Volume']
    colors = ['orange', 'green']

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, volumes, color=colors)
    ax.set_ylabel('Volume (cm³)')
    ax.set_title('Packaging Volume Comparison')
    for i, v in enumerate(volumes):
        ax.text(i, v + (max(volumes)*0.02), f'{v:.1f}', ha='center', va='bottom')
    st.pyplot(fig)

    st.success(f"**🎉 Potential Volume Reduction: {volume_reduction_percent:.2f}%**")
    st.markdown("*(This directly translates to lower shipping costs by reducing 'shipping air'.)*")
    
    st.markdown("---")

    # --- Sustainable Material Recommendation ---
    st.subheader("3. Sustainable Material Recommendation")

    # For simplicity, calculate average fragility for multi-item, or use max for safety
    avg_fragility = selected_products_df_display['fragility_score'].mean() if not selected_products_df_display.empty else 1
    
    # Pass the cost_tolerance from the sidebar to the core logic function
    recommended_material = recommend_sustainable_material(avg_fragility, cost_tolerance_factor=cost_tolerance)

    if recommended_material is not None:
        st.write(f"**Eco-Pack AI Recommended Material:**")
        st.success(f"**{recommended_material['name']}**")
        
        col_rec1, col_rec2 = st.columns(2)
        with col_rec1:
            st.markdown(f"""
                - **Recycled Content:** {recommended_material['recycled_content_percent']:.0f}%
                - **Recyclability Score:** {recommended_material['recyclability_score']}/5
            """)
        with col_rec2:
            st.markdown(f"""
                - **Biodegradability Score:** {recommended_material['biodegradability_score']}/5
                - **Est. Carbon Footprint:** {recommended_material['carbon_footprint_per_unit_sqm']:.3f} kg CO2/sqm
            """)
        
        st.markdown("---")
        st.write(f"**Estimated Current Standard Material:**")
        
        # Get current material data from the current_pkg dict
        current_material_data = current_pkg['material']
        st.warning(f"**{current_material_data['name']}**")

        col_curr1, col_curr2 = st.columns(2)
        with col_curr1:
            st.markdown(f"""
                - **Recycled Content:** {current_material_data['recycled_content_percent']:.0f}%
                - **Recyclability Score:** {current_material_data['recyclability_score']}/5
            """)
        with col_curr2:
            st.markdown(f"""
                - **Biodegradability Score:** {current_material_data['biodegradability_score']}/5
                - **Est. Carbon Footprint:** {current_material_data['carbon_footprint_per_unit_sqm']:.3f} kg CO2/sqm
            """)

        # Calculate sustainability impact differences
        carbon_reduction_per_sqm = current_material_data['carbon_footprint_per_unit_sqm'] - recommended_material['carbon_footprint_per_unit_sqm']
        carbon_reduction_percent = (carbon_reduction_per_sqm / current_material_data['carbon_footprint_per_unit_sqm']) * 100 if current_material_data['carbon_footprint_per_unit_sqm'] > 0 else 0
        
        recycled_content_increase = recommended_material['recycled_content_percent'] - current_material_data['recycled_content_percent']

        st.subheader("Environmental Impact Comparison:")
        impact_col1, impact_col2 = st.columns(2)
        with impact_col1:
            st.metric(label="Carbon Footprint Reduction (per sq.m)", value=f"{carbon_reduction_per_sqm:.3f} kg CO2", delta=f"{carbon_reduction_percent:.2f}% reduction")
        with impact_col2:
            st.metric(label="Increase in Recycled Content", value=f"{recycled_content_increase:.0f}% points")
        
        st.markdown("*(These figures represent the per-unit-area impact of switching materials. Actual total impact depends on package surface area.)*")

        st.markdown("---")
        st.subheader("Environmental Impact Comparison (Material Properties):")
        # --- NEW MATERIAL COMPARISON CHART ---
        metrics = ['Recycled Content (%)', 'Recyclability Score (1-5)', 'Biodegradability Score (1-5)', 'Carbon Footprint (kg CO2/sqm)']
        
        # Prepare data for plotting
        rec_values = [
            recommended_material['recycled_content_percent'],
            recommended_material['recyclability_score'],
            recommended_material['biodegradability_score'],
            recommended_material['carbon_footprint_per_unit_sqm']
        ]
        curr_values = [
            current_material_data['recycled_content_percent'],
            current_material_data['recyclability_score'],
            current_material_data['biodegradability_score'],
            current_material_data['carbon_footprint_per_unit_sqm']
        ]

        fig2, axes = plt.subplots(1, 4, figsize=(18, 5)) # Use 4 columns for 4 metrics
        fig2.suptitle('Material Sustainability Comparison: Eco-Pack AI vs. Current', fontsize=16)

        # Recycled Content
        ax = axes[0]
        bars = ax.bar(['Current', 'Eco-Pack AI'], [curr_values[0], rec_values[0]], color=['orange', 'green'])
        ax.set_title('Recycled Content (%)')
        ax.set_ylim(0, 100)
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 2, round(yval, 1), ha='center', va='bottom')

        # Recyclability Score
        ax = axes[1]
        bars = ax.bar(['Current', 'Eco-Pack AI'], [curr_values[1], rec_values[1]], color=['orange', 'green'])
        ax.set_title('Recyclability Score (1-5)')
        ax.set_ylim(0, 5.5)
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 0.1, round(yval, 1), ha='center', va='bottom')

        # Biodegradability Score
        ax = axes[2]
        bars = ax.bar(['Current', 'Eco-Pack AI'], [curr_values[2], rec_values[2]], color=['orange', 'green'])
        ax.set_title('Biodegradability Score (1-5)')
        ax.set_ylim(0, 5.5)
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 0.1, round(yval, 1), ha='center', va='bottom')

        # Carbon Footprint
        ax = axes[3]
        bars = ax.bar(['Current', 'Eco-Pack AI'], [curr_values[3], rec_values[3]], color=['orange', 'green'])
        ax.set_title('Carbon Footprint (kg CO2/sqm)')
        max_cf = max(curr_values[3], rec_values[3])
        ax.set_ylim(0, max_cf * 1.2) 
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + (max_cf*0.02), f'{yval:.3f}', ha='center', va='bottom')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95]) 
        st.pyplot(fig2)
        # --- END NEW MATERIAL COMPARISON CHART ---

    else:
        st.warning("Eco-Pack AI could not recommend a suitable sustainable material based on current product fragility and material availability.")

    st.markdown("---")
    st.subheader("📊 Overall Estimated Impact for Walmart")
    
    # Simple calculation of overall savings. In a real app, this would be aggregated over many orders.
    # For demo, just sum up perceived benefits from this single/multi order
    
    # Assume a small cost saving per volume reduction, and per material switch
    # These are illustrative for the demo!
    estimated_shipping_cost_savings = (volume_reduction_percent / 100) * 0.5 * selected_products_df_display['weight_kg'].sum() # Higher weight = more shipping cost savings
    # Note: `estimated_material_cost_delta` was conceptually present but not used for display in old code. 
    # Removed to avoid confusion. Carbon reduction is the main material impact metric.
    
    # Display overall metrics
    st.metric(label="Est. Shipping Volume Reduction (per order)", value=f"{volume_reduction_percent:.2f}%", help="Reduced box size means less 'air' is shipped, saving on logistics costs.")
    
    # Ensure carbon_reduction_percent is defined for this metric
    if 'carbon_reduction_percent' in locals():
        st.metric(label="Est. Carbon Footprint Reduction (per unit area of material)", value=f"{carbon_reduction_percent:.2f}%", help="Switching to greener materials reduces the environmental impact of packaging.")
    else:
        st.metric(label="Est. Carbon Footprint Reduction (per unit area of material)", value="N/A", help="Select a product to see this metric.")

    st.success(f"By leveraging **Walmart Eco-Pack AI**, Walmart can achieve tangible savings in logistics and make significant progress towards its ambitious sustainability goals. This leads to **lower operational costs, reduced environmental footprint, and enhanced brand reputation** with eco-conscious customers.")

    st.markdown("---")
    st.header("📈 Projected Annual Impact for Walmart (Simulation)")

    # Define assumptions for simulation (these are illustrative)
    daily_packages_processed = 500000 
    annual_packages_processed = daily_packages_processed * 365

    st.info(f"Assuming Walmart processes approximately **{daily_packages_processed:,} packages per day** (or {annual_packages_processed:,} annually) globally, and applying the average savings demonstrated:")

    # Project Volume Reduction Savings
    avg_vol_savings_per_pkg = (current_box_info['Volume'] - optimal_box_info['Volume']) if current_box_info['Volume'] > optimal_box_info['Volume'] else 0
    annual_shipping_cost_savings = (avg_vol_savings_per_pkg * annual_packages_processed * 0.0000001) / 1000000 
    
    # Project Carbon Reduction Savings (very rough, based on per sqm for a typical box size)
    avg_box_surface_area_sqm = (optimal_box_info['L']/100 * optimal_box_info['W']/100) * 6 
    annual_carbon_savings_per_material_switch = (carbon_reduction_per_sqm * avg_box_surface_area_sqm * annual_packages_processed) / 1000 

    col_proj1, col_proj2 = st.columns(2)
    with col_proj1:
        st.metric(label="Est. Annual Shipping Cost Savings", value=f"${annual_shipping_cost_savings:.2f} Million USD", help="Based on volume reduction across millions of packages. *Highly illustrative.*")
    with col_proj2:
        st.metric(label="Est. Annual CO2 Emissions Avoided", value=f"{annual_carbon_savings_per_material_switch:.0f} Metric Tons", help="Based on switching to more sustainable materials. *Highly illustrative.*")

    st.markdown("""
        *Note: These are simplified projections for demonstration purposes and would require more detailed logistics and material cost data for precise real-world estimates.*
    """)

    st.markdown("---")
    st.header("🎯 Strategic Impact for Walmart")
    st.markdown("""
        The **Walmart Eco-Pack AI** is designed to be a pivotal tool in Walmart's journey towards its sustainability and efficiency targets.
    """)

    st.success(f"**Addressing Virgin Plastic:** By prioritizing materials with high recycled content, Eco-Pack AI helps reverse the reported **6% increase in virgin plastic use**, contributing directly to Walmart's reduction goals.")
    st.success(f"**Boosting Recyclability:** Our agent actively recommends materials with a **high recyclability score (up to 5/5)**, pushing Walmart closer to its **100% recyclable packaging target** (currently at 68%).")
    st.success(f"**Optimized Logistics:** The calculated **{volume_reduction_percent:.2f}% volume reduction** per order translates into millions in **shipping cost savings** and **reduced carbon emissions** from transportation across Walmart's vast supply chain.")
    
    st.info("This solution isn't just about efficiency; it's about making Walmart's operations fundamentally more sustainable and customer-aligned.")