def generate_subcategory_id(category_prefix, counter=0):
    """Generate unique subcategory ID"""
    base_id = f"subid{category_prefix}{counter:03d}25"
    from ..models import SubCategory
    
    if not SubCategory.objects.filter(sub_category_id=base_id).exists():
        return base_id
    if counter > 999:
        raise ValueError("Unable to generate unique subcategory ID after 999 attempts")
    return generate_subcategory_id(category_prefix, counter + 1)

def get_starting_counter(category_id, last_sub_category):
    """Get the starting counter for subcategory ID generation"""
    if not last_sub_category:
        return 1
        
    try:
        category_prefix = str(category_id)
        id_parts = last_sub_category.sub_category_id.split(category_prefix)
        if len(id_parts) > 1:
            num_part = id_parts[1][0:3]
            return int(num_part) + 1
    except (ValueError, IndexError):
        pass
    
    return 1 