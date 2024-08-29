from pinecone import Pinecone, ServerlessSpec
import dotenv
import os

dotenv.load_dotenv()

pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

book_index_name = 'book-text'
book_index = pc.Index(book_index_name)


def find_similar_books(book_id, top_k=10):
    query_result = book_index.query(id=book_id, top_k=top_k)
    similar_books = [int(match['id']) for match in query_result['matches']]
    # return books.loc[similar_books, ['Book', 'Author', 'Description', 'Genres', 'Avg_Ratings', 'URL']]

    print(similar_books)
    return similar_books


if __name__ == '__main__':
    find_similar_books("522")