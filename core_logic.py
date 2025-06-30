import pandas as pd
import numpy as np

# Load mock data - Ensure these paths are correct relative to where core_logic.py is run
PRODUCTS_DF = pd.read_csv('data/products.csv')
MATERIALS_DF = pd.read_csv('data/packaging_materials.csv')

def get_product_data(product_id):
    """Retrieves product data by ID."""
    return PRODUCTS_DF[PRODUCTS_DF['product_id'] == product_id].iloc[0]

def calculate_optimal_single_box(length, width, height, buffer_cm=1):
    """
    Calculates the smallest possible rectangular box for a single product.
    Adds a small buffer to each dimension for safety.
    """
    optimal_length = length + buffer_cm
    optimal_width = width + buffer_cm
    optimal_height = height + buffer_cm
    optimal_volume = optimal_length * optimal_width * optimal_height
    return optimal_length, optimal_width, optimal_height, optimal_volume

def calculate_approximate_multi_box(product_ids):
    """
    Calculates an approximate optimal box for multiple items using a simplified bounding box.
    Assumes items can be roughly stacked or placed to minimize overall footprint.
    For a prototype, this is a reasonable simplification.
    """
    selected_products = PRODUCTS_DF[PRODUCTS_DF['product_id'].isin(product_ids)]
    
    if selected_products.empty:
        return 0, 0, 0, 0

    # For a simple approximation:
    # Max length of any item, max width of any item, sum of heights (as if stacked)
    # This is a basic heuristic for a quick prototype.
    max_l = selected_products['length_cm'].max()
    max_w = selected_products['width_cm'].max()
    sum_h = selected_products['height_cm'].sum() # Assuming they can be stacked

    # Add buffer to the overall dimensions
    buffer_cm_multi = 2 # Slightly larger buffer for multi-items
    optimal_length = max_l + buffer_cm_multi
    optimal_width = max_w + buffer_cm_multi
    optimal_height = sum_h + buffer_cm_multi

    optimal_volume = optimal_length * optimal_width * optimal_height
    return optimal_length, optimal_width, optimal_height, optimal_volume

def recommend_sustainable_material(product_fragility, cost_tolerance_factor): # Removed default value
    """
    Recommends the most sustainable packaging material that meets strength
    requirements and is within a reasonable cost tolerance.
    """
    suitable_materials = MATERIALS_DF[MATERIALS_DF['strength_rating'] >= product_fragility].copy()

    if suitable_materials.empty:
        return None # No suitable material found

    # Calculate a composite sustainability score (higher is better)
    # Weights can be adjusted based on desired emphasis
    # (e.g., more weight on recyclability, less on biodegradability if not relevant to specific recycling streams)
    suitable_materials['sustainability_score'] = (
        suitable_materials['recycled_content_percent'] * 0.005 +  # Scale 0-100 to 0-0.5
        suitable_materials['recyclability_score'] * 0.1 +        # Scale 1-5 to 0.1-0.5
        suitable_materials['biodegradability_score'] * 0.05 +     # Scale 1-5 to 0.05-0.25
        (1 - (suitable_materials['carbon_footprint_per_unit_sqm'] / MATERIALS_DF['carbon_footprint_per_unit_sqm'].max())) * 0.2 # Higher carbon footprint is worse, so invert
    )
    # Sort by sustainability score (descending)
    suitable_materials = suitable_materials.sort_values(by='sustainability_score', ascending=False)

    # Find the lowest cost among suitable materials to set a baseline for tolerance
    lowest_cost_material_cost = suitable_materials['cost_per_unit_area'].min()

    # Filter for materials within cost tolerance
    affordable_sustainable_materials = suitable_materials[
        suitable_materials['cost_per_unit_area'] <= lowest_cost_material_cost * cost_tolerance_factor
    ]

    if affordable_sustainable_materials.empty:
        # Fallback: if no affordable sustainable options, just pick the most sustainable suitable one
        return suitable_materials.iloc[0]
    
    # Return the most sustainable from the affordable ones
    return affordable_sustainable_materials.iloc[0]

# --- Mock "Current" State Calculations (for comparison) ---
# These functions simulate less optimized, "current" Walmart packaging.
# In a real scenario, this would come from actual historical data.

def get_mock_current_packaging(product_id):
    """
    Simulates existing, likely less optimized, packaging for a single product.
    Uses larger buffers than optimal.
    """
    product = get_product_data(product_id)
    # Assume existing packaging is always significantly larger than the product
    current_l = product['length_cm'] * 1.2 # 20% larger
    current_w = product['width_cm'] * 1.2
    current_h = product['height_cm'] * 1.2
    current_vol = current_l * current_w * current_h
    
    # Simple lookup for current material based on product type or just a default
    current_material_id = product['current_packaging_material']
    current_material = MATERIALS_DF[MATERIALS_DF['material_id'] == current_material_id].iloc[0]

    return {
        'length': current_l,
        'width': current_w,
        'height': current_h,
        'volume': current_vol,
        'material': current_material
    }

def get_mock_current_multi_packaging(product_ids):
    """
    Simulates a larger, less optimized box for multiple items.
    """
    selected_products = PRODUCTS_DF[PRODUCTS_DF['product_id'].isin(product_ids)]
    
    if selected_products.empty:
        return {'length': 0, 'width': 0, 'height': 0, 'volume': 0, 'material': MATERIALS_DF[MATERIALS_DF['material_id'] == 'cardboard_standard'].iloc[0]}

    # For multi-item, assume a much larger standard box is used
    max_l = selected_products['length_cm'].max()
    max_w = selected_products['width_cm'].max()
    sum_h = selected_products['height_cm'].sum() 

    current_l = max_l * 1.5 # Even more buffer for multi-items
    current_w = max_w * 1.5
    current_h = sum_h * 1.5
    current_vol = current_l * current_w * current_h
    
    # Default to a standard, less sustainable cardboard for current multi-packaging
    current_material = MATERIALS_DF[MATERIALS_DF['material_id'] == 'cardboard_standard'].iloc[0]

    return {
        'length': current_l,
        'width': current_w,
        'height': current_h,
        'volume': current_vol,
        'material': current_material
    }