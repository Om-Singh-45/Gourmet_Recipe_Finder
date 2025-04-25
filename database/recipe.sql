-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS recipe_suggestor;

-- Use the recipe_suggestor database
USE recipe_suggestor;

-- Create ingredients table
CREATE TABLE IF NOT EXISTS ingredients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create recipes table
CREATE TABLE IF NOT EXISTS recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    prep_time INT NOT NULL,
    cook_time INT NOT NULL,
    instructions JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create recipe_ingredients junction table for many-to-many relationship
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    quantity VARCHAR(50),
    unit VARCHAR(50),
    PRIMARY KEY (recipe_id, ingredient_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
);

-- Insert sample ingredients
INSERT INTO ingredients (name) VALUES
('chicken breast'),
('olive oil'),
('salt'),
('black pepper'),
('garlic'),
('onion'),
('tomato'),
('pasta'),
('cheese'),
('bell pepper'),
('rice'),
('lemon'),
('butter'),
('flour'),
('eggs'),
('milk'),
('carrot'),
('celery'),
('basil'),
('oregano'),
('beef'),
('pork'),
('potatoes'),
('cumin'),
('paprika'),
('cinnamon'),
('sugar'),
('honey'),
('spinach'),
('mushroom');

-- Insert sample recipes
INSERT INTO recipes (name, prep_time, cook_time, instructions) VALUES
(
    'Spaghetti Bolognese', 
    15, 
    30, 
    '[
        "Heat olive oil in a large pan over medium heat.",
        "Add chopped onions and garlic, sauté until fragrant.",
        "Add ground beef and cook until browned.",
        "Add diced tomatoes, salt, pepper, and oregano. Simmer for 20 minutes.",
        "Meanwhile, cook pasta according to package instructions.",
        "Serve sauce over pasta and garnish with cheese."
    ]'
),
(
    'Chicken Stir Fry', 
    10, 
    15, 
    '[
        "Slice chicken breast into thin strips.",
        "Heat olive oil in a wok or large pan over high heat.",
        "Add chicken and cook until golden, about 5 minutes.",
        "Add sliced bell peppers, onions, and garlic. Stir fry for 3 minutes.",
        "Season with salt, pepper, and soy sauce.",
        "Serve hot over rice."
    ]'
),
(
    'Vegetable Omelette', 
    5, 
    10, 
    '[
        "Beat eggs in a bowl with salt and pepper.",
        "Heat butter in a non-stick pan over medium heat.",
        "Add diced bell peppers, onions, and mushrooms. Sauté for 2