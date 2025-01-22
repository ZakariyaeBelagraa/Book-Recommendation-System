import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from fuzzywuzzy import process
from PIL import Image
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

books_data = pd.read_csv('data/books_data.csv')

selected_features = ['title', 'authors', 'categories', 'description']

for feature in selected_features:
    books_data[feature] = books_data[feature].fillna('')

combined_features = books_data['title'] + ' ' + books_data['authors'] + ' ' + \
                     books_data['categories'] + ' ' + books_data['description']

books_data['combined_features'] = combined_features

tfidf = TfidfVectorizer(stop_words='english')

tfidf_matrix = tfidf.fit_transform(books_data['combined_features'])

knn = NearestNeighbors(n_neighbors=11, metric='cosine', algorithm='brute')

knn.fit(tfidf_matrix)

book_indices = pd.Series(books_data.index, index=books_data['title']).drop_duplicates()

def find_closest_title(input_title, books_data):
    result = process.extractOne(input_title, books_data['title'])
    
    if result and len(result) >= 2:
        closest_title, score = result[:2]
        if score >= 80:
            return closest_title
    
    return "No similar titles found."

def recommend_books_knn_with_fuzzy(input_title, knn_model, data_matrix, book_indices, books_data):
    closest_title = find_closest_title(input_title, books_data)
    
    if closest_title == "No similar titles found.":
        return closest_title
    
    idx = book_indices[closest_title]
    
    distances, indices = knn_model.kneighbors(data_matrix[idx], n_neighbors=11)
    
    recommended_indices = indices.flatten()[1:]
    recommended_books_data = books_data.iloc[recommended_indices].to_dict(orient='records')
    
    return closest_title, recommended_books_data

if __name__ == "__main__":
    # Exemple de test
    input_title = "java"
    result = recommend_books_knn_with_fuzzy(input_title, knn, tfidf_matrix, book_indices, books_data)
    
    print(result)




