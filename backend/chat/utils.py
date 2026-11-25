def conversation_group_name(first_user_id, second_user_id):
    low, high = sorted((first_user_id, second_user_id))
    return f"chat_{low}_{high}"
