import google.generativeai as genai
import json
from typing import List
from pydantic import BaseModel

# Configure the API key (you'll need to set this)
# genai.configure(api_key="YOUR_GEMINI_API_KEY")

class Recipe(BaseModel):
    """Pydantic model for recipe structure"""
    recipeName: str
    ingredients: List[str]
    cookingTime: str
    difficulty: str

class RecipeList(BaseModel):
    """Container for multiple recipes"""
    recipes: List[Recipe]

def create_manual_schema():
    """
    Create a manual schema using the Schema object structure
    This demonstrates the raw schema approach without Pydantic
    """
    return {
        "type": "object",
        "properties": {
            "recipes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "recipeName": {
                            "type": "string",
                            "description": "Name of the recipe"
                        },
                        "ingredients": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "List of ingredients with measurements"
                        },
                        "cookingTime": {
                            "type": "string",
                            "description": "Total cooking time"
                        },
                        "difficulty": {
                            "type": "string",
                            "enum": ["Easy", "Medium", "Hard"],
                            "description": "Difficulty level"
                        }
                    },
                    "required": ["recipeName", "ingredients", "cookingTime", "difficulty"],
                    "propertyOrdering": ["recipeName", "ingredients", "cookingTime", "difficulty"]
                }
            }
        },
        "required": ["recipes"],
        "propertyOrdering": ["recipes"]
    }

def call_gemini_with_pydantic_schema():
    """
    Call Gemini using Pydantic model for schema definition (recommended approach)
    """
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        prompt = """
        Generate 3 different cookie recipes. Each recipe should include:
        - A creative recipe name
        - A detailed list of ingredients with measurements
        - Total cooking time
        - Difficulty level (Easy, Medium, or Hard)
        
        Make the recipes diverse and interesting.
        """
        
        # Generate content with Pydantic schema
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=RecipeList
            )
        )
        
        return response.text
        
    except Exception as e:
        print(f"Error with Pydantic schema approach: {e}")
        return None

def call_gemini_with_manual_schema():
    """
    Call Gemini using manually defined schema
    """
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        prompt = """
        Generate 2 different dessert recipes. Each recipe should include:
        - A creative recipe name
        - A detailed list of ingredients with measurements
        - Total cooking time
        - Difficulty level (Easy, Medium, or Hard)
        
        Focus on chocolate-based desserts.
        """
        
        # Create manual schema
        schema = create_manual_schema()
        
        # Generate content with manual schema
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=schema
            )
        )
        
        return response.text
        
    except Exception as e:
        print(f"Error with manual schema approach: {e}")
        return None

def validate_and_display_json(json_string, title):
    """
    Validate and pretty print the JSON response
    """
    try:
        data = json.loads(json_string)
        print(f"\n{title}")
        print("=" * len(title))
        print(json.dumps(data, indent=2))
        
        # Display in a more readable format
        if 'recipes' in data:
            print(f"\nParsed {len(data['recipes'])} recipes:")
            for i, recipe in enumerate(data['recipes'], 1):
                print(f"\n{i}. {recipe['recipeName']}")
                print(f"   Difficulty: {recipe['difficulty']}")
                print(f"   Cooking Time: {recipe['cookingTime']}")
                print(f"   Ingredients: {len(recipe['ingredients'])} items")
                
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for {title}: {e}")
        print(f"Raw response: {json_string}")

def main():
    """
    Main function to demonstrate both approaches
    """
    print("Google Gemini Structured JSON Output Demo")
    print("=" * 45)
    
    # Check if API key is configured
    try:
        # This will raise an exception if API key is not set
        model = genai.GenerativeModel('gemini-1.5-pro')
        print("✓ Gemini API configured successfully")
    except Exception as e:
        print("✗ Gemini API not configured. Please set your API key:")
        print("genai.configure(api_key='YOUR_GEMINI_API_KEY')")
        print(f"Error: {e}")
        return
    
    # Approach 1: Using Pydantic models (recommended)
    print("\n1. Calling Gemini with Pydantic Schema (Recommended)")
    pydantic_result = call_gemini_with_pydantic_schema()
    if pydantic_result:
        validate_and_display_json(pydantic_result, "Pydantic Schema Results")
    
    # Approach 2: Using manual schema definition
    print("\n2. Calling Gemini with Manual Schema")
    manual_result = call_gemini_with_manual_schema()
    if manual_result:
        validate_and_display_json(manual_result, "Manual Schema Results")

# Example of more complex schema with nested objects
class NutritionalInfo(BaseModel):
    calories: int
    protein: str
    carbs: str
    fat: str

class DetailedRecipe(BaseModel):
    recipeName: str
    ingredients: List[str]
    instructions: List[str]
    cookingTime: str
    prepTime: str
    servings: int
    difficulty: str
    nutritionalInfo: NutritionalInfo
    tags: List[str]

def advanced_schema_example():
    """
    Example with more complex nested schema
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        prompt = """
        Generate 1 detailed healthy breakfast recipe with complete nutritional information.
        Include step-by-step instructions, prep time, cooking time, servings, and relevant tags.
        """
        
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=DetailedRecipe
            )
        )
        
        print("\n3. Advanced Schema Example (Nested Objects)")
        validate_and_display_json(response.text, "Advanced Schema Results")
        
    except Exception as e:
        print(f"Error with advanced schema: {e}")

if __name__ == "__main__":
    # Uncomment the line below and add your API key
    # genai.configure(api_key="YOUR_GEMINI_API_KEY")
    
    main()
    
    # Uncomment to run advanced example
    # advanced_schema_example()
    
