import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Define category seed examples for linguistic clustering
CATEGORY_EXAMPLES = {
    'Dairy': [
        'milk', 'cheese', 'yoghurt', 'butter', 'cream', 'ice cream',
        'lactose free', 'greek yogurt', 'mozzarella', 'cheddar',
        'cottage cheese', 'sour cream', 'whipped cream'
    ],
    'Bakery': [
        'bread', 'bagel', 'croissant', 'donut', 'muffin', 'cake',
        'biscuit', 'cookie', 'roll', 'pastry', 'sourdough', 'focaccia'
    ],
    'Cereals': [
        'cereal', 'muesli', 'granola', 'corn flakes', 'oats', 'porridge',
        'breakfast', 'flakes', 'grain', 'bran'
    ],
    'Grains': [
        'rice', 'pasta', 'noodles', 'flour', 'couscous', 'quinoa',
        'barley', 'lentil', 'bean', 'chickpea', 'grain', 'bulgur'
    ],
    'Meat': [
        'chicken', 'beef', 'pork', 'lamb', 'turkey', 'meat', 'steak',
        'mince', 'chop', 'wing', 'breast', 'sausage', 'bacon'
    ],
    'Seafood': [
        'fish', 'salmon', 'tuna', 'prawn', 'shrimp', 'crab', 'lobster',
        'oyster', 'mussel', 'anchovy', 'cod', 'trout', 'squid'
    ],
    'Produce': [
        'vegetable', 'fruit', 'apple', 'banana', 'carrot', 'lettuce',
        'tomato', 'potato', 'broccoli', 'spinach', 'orange', 'strawberry',
        'grape', 'onion', 'garlic', 'cucumber'
    ],
    'Frozen': [
        'frozen', 'freeze', 'ice', 'nugget', 'fillet', 'patty', 'pea',
        'berry', 'vegetable mix', 'french fries', 'pizza', 'meal'
    ],
    'Condiments': [
        'sauce', 'dip', 'salsa', 'ketchup', 'mustard', 'mayo', 'vinegar',
        'oil', 'honey', 'jam', 'peanut butter', 'spreads', 'paste'
    ],
    'Snacks': [
        'snack', 'chip', 'crisp', 'trail mix', 'nut', 'popcorn',
        'dried fruit', 'bar', 'energy', 'superfood', 'mix'
    ],
    'Beverages': [
        'juice', 'drink', 'soda', 'coffee', 'tea', 'water', 'milk',
        'smoothie', 'cola', 'lemonade', 'cordial', 'squash'
    ],
}

# Create TfidfVectorizer-based categorizer
def create_tfidf_categorizer():
    """Create a TfidfVectorizer model using category examples."""
    all_examples = []
    category_labels = []
    
    for category, examples in CATEGORY_EXAMPLES.items():
        all_examples.extend(examples)
        category_labels.extend([category] * len(examples))
    
    vectorizer = TfidfVectorizer(
        analyzer='char',
        ngram_range=(2, 3),
        lowercase=True,
        stop_words='english'
    )
    X = vectorizer.fit_transform(all_examples)
    
    return vectorizer, X, category_labels

vectorizer, X_train, category_labels = create_tfidf_categorizer()

def categorize_by_name(product_name, vectorizer, X_train, category_labels, fallback_url=''):
    """
    Categorize product using TfidfVectorizer and cosine similarity.
    Uses product name for linguistic clustering.
    """
    if not product_name or len(product_name.strip()) == 0:
        return 'Other'
    
    # Transform product name
    X_product = vectorizer.transform([product_name.lower()])
    
    # Calculate similarity to all training examples
    similarities = cosine_similarity(X_product, X_train)[0]
    
    # Find category with highest average similarity
    unique_categories = list(CATEGORY_EXAMPLES.keys())
    category_scores = {}
    
    for category in unique_categories:
        category_indices = [i for i, cat in enumerate(category_labels) if cat == category]
        if category_indices:
            avg_similarity = np.mean(similarities[category_indices])
            category_scores[category] = avg_similarity
    
    # Return best matching category if similarity is above threshold
    best_category = max(category_scores, key=category_scores.get)
    best_score = category_scores[best_category]
    
    # Use a similarity threshold of 0.05 to avoid weak matches
    if best_score > 0.05:
        return best_category
    
    return 'Other'

df = pd.read_csv('cleanedData.csv')

# Debug: Check similarity scores for first few products
print("=== DEBUG: First 5 products and their scores ===")
for idx, name in enumerate(df['name'].head(5)):
    X_product = vectorizer.transform([name.lower()])
    similarities = cosine_similarity(X_product, X_train)[0]
    
    unique_categories = list(CATEGORY_EXAMPLES.keys())
    category_scores = {}
    for category in unique_categories:
        category_indices = [i for i, cat in enumerate(category_labels) if cat == category]
        if category_indices:
            avg_similarity = np.mean(similarities[category_indices])
            category_scores[category] = avg_similarity
    
    best_category = max(category_scores, key=category_scores.get)
    best_score = category_scores[best_category]
    print(f"Product: {name[:50]}")
    print(f"  Scores: {category_scores}")
    print(f"  Best: {best_category} ({best_score:.4f})")
    print()

# Apply categorization using TfidfVectorizer
df['category'] = df['name'].apply(
    lambda name: categorize_by_name(name, vectorizer, X_train, category_labels)
)

df = df[['name', 'company', 'category', 'quantity', 'daySinceEpoch', 'price', 'url']]

df = df.sort_values(by=['company', 'category'])

df.to_csv('categorisedData.csv', index=False)