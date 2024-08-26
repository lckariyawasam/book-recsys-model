import pandas as pd
from rapidfuzz import process, fuzz
from multiprocessing import Pool, cpu_count
import os
import re

PARALLEL = False

# Function to process a single chunk
def process_chunk(chunk, title_to_isbn, threshold=90):
    print("Processing chunk...")
    unique_titles = chunk['Book-Title'].unique()
    
    # Update the title_to_isbn mapping with the current chunk
    for title in unique_titles:
        similar_titles = get_similar_titles(title, title_to_isbn.keys(), threshold)
        similar_titles = [t for t in similar_titles if not is_sequel(title, t)]
        if len(similar_titles) > 1:
            print(title, "COUNT:", len(similar_titles), similar_titles)
            unified_isbn = min(title_to_isbn[t] for t in similar_titles)
            title_to_isbn[title] = unified_isbn
     
    # Update chunk with unified ISBNs
    chunk['unified_isbn'] = chunk['Book-Title'].map(title_to_isbn)
    print("Finished processing chunk")
    return chunk[['ISBN', 'Book-Title', 'Book-Author', 'unified_isbn']]

# Function to find similar titles
def get_similar_titles(title, all_titles, threshold=80):
    return [t[0] for t in process.extract(title, all_titles, scorer=fuzz.ratio, limit=None) if t[1] >= threshold]

# Function to process a file chunk
def process_file_chunk(file_chunk):
    # File chunk is passed as a DataFrame and title_to_isbn as a dictionary
    return process_chunk(file_chunk[0], file_chunk[1])

def extract_numbers(title):
    numbers = re.findall(r'\d+', title)
    return set([int(num) for num in numbers])

# Function to determine if a title is a sequel based on a heuristic
def is_sequel(title, similar_title):
    # Define a simple heuristic to identify sequels
    title_numbers = extract_numbers(title)
    similar_title_numbers = extract_numbers(similar_title)
    return bool(title_numbers and similar_title_numbers and title_numbers != similar_title_numbers)



def run_parallel():
    # Parameters
    chunk_size = 36000  # Adjust based on available memory
    threshold = 80

    # Load data in chunks
    chunks = pd.read_csv('data/cleaned_books.csv', chunksize=chunk_size)
    
    # Initialize title_to_isbn dictionary
    title_to_isbn = {}

    # Load all books
    books_df = pd.read_csv('data/cleaned_books_modified.csv')
    title_to_isbn = dict(zip(books_df['Book-Title'], books_df['ISBN']))
    
    # List to store chunks results
    all_chunks = []
    
    # Prepare data for parallel processing
    file_chunks = [(chunk, title_to_isbn) for chunk in chunks]
    
    # Use multiprocessing to process chunks in parallel
    with Pool(processes=cpu_count() - 2) as pool:
        results = pool.map(process_file_chunk, file_chunks)
        
        # Collect results
        for result in results:
            all_chunks.append(result)

    # Concatenate all processed chunks into a single DataFrame
    books_df = pd.concat(all_chunks).drop_duplicates().reset_index(drop=True)

    print("Unified ISBNs for Books:", books_df['unified_isbn'].nunique())

    # Update ratings DataFrame
    ratings_df = pd.read_csv('data/cleaned_ratings.csv')
    ratings_df = ratings_df.merge(books_df[['ISBN']], on='ISBN', how='left', suffixes=('', '_new'))
    ratings_df = ratings_df.drop(columns='ISBN')

    # Save the updated DataFrames to new CSV files
    books_df.to_csv('updated_books.csv', index=False)
    ratings_df.to_csv('updated_ratings.csv', index=False)


def runner():    
    # Initialize title_to_isbn dictionary
    title_to_isbn = {}

    # Load all books
    books_df = pd.read_csv('data/cleaned_books_modified.csv')
    title_to_isbn = dict(zip(books_df['Book-Title'], books_df['Book-ID']))
    books_modified = books_df.copy()
    books_modified['Book-ID-Modified'] = books_modified['Book-ID']

    for author in books_df['Book-Author'].unique():
        authors_books = books_df[books_df['Book-Author'] == author]
        author_titles = authors_books['Book-Title'].unique()
        encountered = set()
        for title in author_titles:
            if title in encountered:
                continue
            similar_titles = get_similar_titles(title, author_titles, threshold=90)
            if len(similar_titles) > 1:
                print(title, "COUNT:", len(similar_titles), similar_titles)
                unified_isbn = min(title_to_isbn[t] for t in similar_titles)
                title_to_isbn[title] = unified_isbn
                for t in similar_titles:
                    books_modified.loc[books_modified['Book-Title'] == t, 'Book-ID-Modified'] = unified_isbn
                encountered.update(similar_titles)

                
    # Update ratings DataFrame
    ratings_df = pd.read_csv('data/cleaned_ratings_modified.csv')
    ratings_df = ratings_df.merge(books_df[['Book-ID']], on='Book-ID', how='left', suffixes=('', '_new'))

    # Save the updated DataFrames to new CSV files
    books_modified.to_csv('updated_books.csv', index=False)
    ratings_df.to_csv('updated_ratings.csv', index=False)

if __name__ == "__main__":
    if PARALLEL:
        run_parallel()
    else:
        runner()