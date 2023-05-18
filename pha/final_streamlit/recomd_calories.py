
def calculate_recommended_calories(age, goal_weight, height, activity_level, goal_type):
    # Constants for calorie calculations
    weight_factor = 10
    height_factor = 6.25
    age_factor = 5
    sedentary_factor = 1.2
    moderate_factor = 1.55
    active_factor = 1.9

    # Calculate the basal metabolic rate (BMR)
    bmr = (weight_factor * goal_weight) + (height_factor * height) - (age_factor * age)

    # Calculate the recommended calories based on activity level
    if activity_level == 'sedentary':
        recommended_calories = bmr * sedentary_factor
    elif activity_level == 'moderate':
        recommended_calories = bmr * moderate_factor
    elif activity_level == 'active':
        recommended_calories = bmr * active_factor
    else:
        recommended_calories = None  # Handle unknown activity levels

    # consider the goal_type 
    if goal_type  == 'diet':
        proteins = recommended_calories * 0.35 
        fats = recommended_calories * 0.2
        carbs = recommended_calories - proteins - fats
    # goal_type == "putting on weight "
    else :
        proteins = recommended_calories * 0.4
        fats = recommended_calories * 0.3
        carbs =  recommended_calories - proteins - fats

    return recommended_calories, carbs, proteins, fats 

# Example usage

if __name__ == '__main__':
    goal_weight = 70  # User's goal weight in kilograms
    height = 170  # User's height in centimeters
    activity_level = 'moderate'  # User's activity level
    age = 27
    goal_type = 'diet'

    recommended_calories = calculate_recommended_calories(age, goal_weight, height, activity_level, goal_type)
    print(f"Recommended calories: {recommended_calories} kcal")
