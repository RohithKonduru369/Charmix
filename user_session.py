logged_in_user_email = None
current_routine_category = None
current_routine_products = None

def set_current_user(email):
    global logged_in_user_email
    logged_in_user_email = email

def get_current_user():
    return logged_in_user_email

# --- NEW FUNCTIONS FOR ROUTINE PERSISTENCE ---
def set_user_routine(category, products):
    global current_routine_category, current_routine_products
    current_routine_category = category
    current_routine_products = products

def get_user_routine():
    """Returns a tuple: (category_name, product_list) or (None, None)"""
    return current_routine_category, current_routine_products

def clear_session():
    """Resets everything on logout"""
    global logged_in_user_email, current_routine_category, current_routine_products
    logged_in_user_email = None
    current_routine_category = None
    current_routine_products = None