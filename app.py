import os
import json
import numpy as np
import mysql.connector
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import traceback
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class RecipeSuggestor:
    def __init__(self):
        """Initialize database connection and ML models"""
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root',
                database='recipe_suggestor'
            )
            self.cursor = self.connection.cursor(dictionary=True)
            
            # Initialize ML components
            self.vectorizer = TfidfVectorizer()
            self.mlb = MultiLabelBinarizer()
            self.recipe_vectors = None
            self.ingredient_vectors = None
            
            # Load and preprocess recipes
            self.load_and_preprocess_recipes()
        except mysql.connector.Error as err:
            logger.error(f"Database Connection Error: {err}")
            raise

    def load_dataset(self):
        """Load recipes from CSV file into the recipenew table using pandas"""
        try:
            # Check if recipenew table is empty
            self.cursor.execute("SELECT COUNT(*) as count FROM recipenew")
            count = self.cursor.fetchone()['count']
            logger.info(f"Current row count in recipenew: {count}")
            
            if count == 0:
                dataset_path = r"C:\Users\Shruti Singh\Downloads\cuisine_updated_new.csv"
                logger.info(f"Attempting to load dataset from: {dataset_path}")
                
                if not os.path.exists(dataset_path):
                    logger.error(f"File not found: {dataset_path}")
                    raise FileNotFoundError(f"Dataset file not found at {dataset_path}")
                
                # Load CSV with pandas
                df = pd.read_csv(dataset_path, encoding='utf-8')
                expected_columns = ['name', 'image_url', 'description', 'cuisine', 'course', 'diet', 'prep_time', 'ingredients', 'instructions', 'image_available']
                
                # Verify columns
                if list(df.columns) != expected_columns:
                    logger.error(f"Unexpected CSV header. Expected: {expected_columns}, Got: {list(df.columns)}")
                    raise ValueError("CSV header does not match expected columns")
                
                # Insert each row into the database
                for index, row in df.iterrows():
                    try:
                        query = """
                        INSERT INTO recipenew (name, image_url, description, cuisine, course, diet, prep_time, ingredients, instructions, image_available)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        values = (
                            row['name'],
                            row['image_url'],
                            row['description'],
                            row['cuisine'],
                            row['course'],
                            row['diet'],
                            row['prep_time'],
                            row['ingredients'],
                            row['instructions'],
                            int(row['image_available'])
                        )
                        self.cursor.execute(query, values)
                        logger.debug(f"Inserted row {index + 2}: {row['name']}")
                    except Exception as e:
                        logger.warning(f"Failed to insert row {index + 2}: {e}")
                        continue
                
                self.connection.commit()
                logger.info("Loaded dataset from CSV into recipenew table")
            else:
                logger.info("Recipenew table already populated, skipping CSV load")

        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            logger.error(traceback.format_exc())
            self.connection.rollback()

    def load_and_preprocess_recipes(self):
        """Load recipes from recipenew and prepare ML models"""
        try:
            # Load dataset from CSV
            self.load_dataset()

            # Fetch all recipes from recipenew
            query = "SELECT id, name, cuisine, diet, ingredients FROM recipenew"
            self.cursor.execute(query)
            recipes = self.cursor.fetchall()
            logger.info(f"Fetched {len(recipes)} recipes from recipenew")

            if not recipes:
                logger.warning("No recipes found in recipenew table for ML preprocessing")
                return

            # Preprocess ingredients for vectorization
            self.recipes = recipes  # Store for later use
            recipe_texts = []
            ingredient_lists = []
            for recipe in recipes:
                # Clean ingredients
                cleaned_ingredients = [self.clean_ingredient(ing) for ing in recipe['ingredients'].split(',')]
                recipe['cleaned_ingredients'] = cleaned_ingredients  # Store for matching
                ingredient_text = ' '.join(cleaned_ingredients)
                recipe_texts.append(f"{recipe['name']} {recipe['cuisine']} {ingredient_text} {recipe['diet']}")
                ingredient_lists.append(cleaned_ingredients)

            # Create TF-IDF vectors for recipes
            self.recipe_vectors = self.vectorizer.fit_transform(recipe_texts)

            # Create ingredient matrix for similarity
            self.ingredient_vectors = self.mlb.fit_transform(ingredient_lists)

        except Exception as e:
            logger.error(f"ML Preprocessing Error: {e}")

    def clean_ingredient(self, ingredient):
        """Clean an ingredient string by removing quantities and standardizing"""
        import re
        # Remove quantities (e.g., "4 cups", "1 tsp")
        ingredient = re.sub(r'\d+\s*(cup|tbsp|tsp|piece|g|ml|to taste)?\s*', '', ingredient)
        # Remove extra whitespace and convert to lowercase
        return ingredient.strip().lower()

    def find_matching_recipes(self, ingredients):
        """Advanced recipe recommendation using ML techniques"""
        try:
            # Preprocess ingredients
            ingredients = [self.clean_ingredient(ing) for ing in ingredients]
            logger.info(f"Searching for recipes with ingredients: {ingredients}")
            
            if self.recipe_vectors is None or self.ingredient_vectors is None:
                logger.error("ML models not initialized. No recipes loaded.")
                return []

            # Create input vector
            input_text = ' '.join(ingredients)
            input_vector = self.vectorizer.transform([input_text])

            # Compute cosine similarity
            similarities = cosine_similarity(input_vector, self.recipe_vectors)[0]

            # Find top recipes based on similarity
            top_indices = similarities.argsort()[-5:][::-1]
            
            # Convert top_indices to regular Python integers
            top_indices = [int(idx) for idx in top_indices]
            
            # Fetch full recipe details for top matches
            if not top_indices:
                logger.info("No matching recipes found after similarity computation")
                return []

            query = """
            SELECT id, name, image_url, description, cuisine, course, diet, prep_time, ingredients, instructions, image_available
            FROM recipenew
            WHERE id IN (%s)
            """ % ','.join(['%s'] * len(top_indices))
            
            # Adjust indices (add 1 to match database IDs, which start at 1)
            adjusted_indices = [idx + 1 for idx in top_indices]
            self.cursor.execute(query, tuple(adjusted_indices))
            recipes = self.cursor.fetchall()
            logger.info(f"Found {len(recipes)} matching recipes")

            return recipes

        except Exception as e:
            logger.error(f"Recipe Matching Error: {e}")
            return []

    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'connection'):
            self.connection.close()

# Flask Application
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/suggest_recipes', methods=['POST'])
def suggest_recipes():
    # Get ingredients from form
    ingredients = request.form.get('ingredients', '').split(',')
    ingredients = [ing.strip() for ing in ingredients]

    logger.info(f"Received Ingredients: {ingredients}")

    # Create recipe suggestor instance
    try:
        recipe_suggestor = RecipeSuggestor()

        # Find matching recipes using ML techniques
        recipes = recipe_suggestor.find_matching_recipes(ingredients)
        return jsonify(recipes)
    except Exception as e:
        logger.error(f"Unexpected Error: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


