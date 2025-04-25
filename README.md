Gourmet Recipe Finder
Overview
Gourmet Recipe Finder is a Machine Learning-based tool designed to suggest recipes based on the ingredients you have on hand. Simply input the ingredients you want to use, and the tool will recommend recipes tailored to your preferences, making cooking smarter, easier, and more fun!
Features

Ingredient-Based Recipe Suggestions: Enter the ingredients you have, and get personalized recipe recommendations.
Machine Learning Powered: Utilizes ML algorithms to analyze and suggest recipes efficiently.
Large Dataset: Built using a dataset of over 4,500 rows, ensuring a wide variety of recipes.

Project Structure

app.py: Main application file for running the recipe suggestion tool.
cuisine_updated_new.csv: Dataset containing over 4,500 rows of recipe data.
database/: Directory for database-related files.
templates/: Directory containing HTML templates for the web interface.
recipe.env: Environment file for configuration settings.

Installation

Clone the repository:git clone https://github.com/Om-Singh-45/Gourmet_Recipe_Finder.git


Navigate to the project directory:cd Gourmet_Recipe_Finder


Install the required dependencies (ensure you have Python installed):pip install -r requirements.txt

Note: If a requirements.txt file isn’t present, you may need to install dependencies manually (e.g., pandas, scikit-learn, etc.).
Run the application:python app.py



Usage

Launch the application by running app.py.
Open your browser and go to http://localhost:5000 (or the specified port).
Enter the ingredients you have in the input field.
Get recipe suggestions tailored to your ingredients!

Dataset
The project uses a dataset (cuisine_updated_new.csv) with over 4,500 rows of recipe data, including ingredients, cuisines, and other relevant details to power the ML model.
Contributing
Contributions are welcome! Feel free to open issues or submit pull requests to improve the project.
License
This project is licensed under the MIT License.

Outputs:
Screenshot 2025-04-26 010934.png

