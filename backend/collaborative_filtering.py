import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class CollaborativeFiltering:
    def __init__(self):
        self.ratings_df = pd.read_csv('../data/minified/cleaned_ratings_reduced.csv')
        self.books_df = pd.read_csv('../data/minified/cleaned_books_reduced.csv')
        # Combine the books and the ratings dataframes using Book-ID
        # Keep only the columns Book-Title, Book-Author, Year-Of-Publication, Publisher, User-ID, Book-Rating
        combined_df = pd.merge(self.ratings_df, self.books_df, on='Book-ID')[['Book-Title', 'Book-Author', 'User-ID', 'Book-Rating']]
        # # The books with the highest 10/10 ratings
        # combined_df[combined_df['Book-Rating'] >= 10].groupby('Book-Title').size().sort_values(ascending=False).head(10)

        self.books = combined_df
        self.vectorizer = TfidfVectorizer(ngram_range=(1,2))
        self.tfidf = self.vectorizer.fit_transform(self.books_df['Book-Title'])


    def search(self, title, result_count=5):
        query_vec = self.vectorizer.transform([title])
        similarity = cosine_similarity(query_vec, self.tfidf).flatten()
        indices = np.argpartition(similarity, -1 * result_count)[-1 * result_count:]
        results = self.books_df.iloc[indices].iloc[::-1]["Book-Title"]
        
        return results

    def get_similar_users(self, title, rating_threshold=8):
        similar_users = self.books[self.books['Book-Title'] == title].where(self.books['Book-Rating'] >= rating_threshold)["User-ID"].unique()
        # Change the user_id to int
        similar_users = similar_users.astype(int)
        return similar_users

    def get_recommendations_from_similar_users(self, similar_users, rating_lower_bound=7, minimum_similarity=0.03, normalize=False, count=None):
        """
        Get the recommendations for a user based on the similar users

        Inputs:
        similar_users: list of similar users
        minimum_similarity: minimum similarity to consider a movie (0 < minimum_similarity < 1)

        Returnds:
        similar_user_recs: list of recommended movies
        """

        similar_users_recommendations = self.books[self.books['User-ID'].isin(similar_users) & (self.books['Book-Rating'] >= rating_lower_bound
                                                                                                )]["Book-Title"]

        # Get the percentage of similar users who have liked the book
        similar_user_recs = similar_users_recommendations.value_counts() / len(similar_users)

        # Filter only the books which have been liked by more than minimum_similarity of the users
        similar_user_recs = similar_user_recs[similar_user_recs > minimum_similarity]

        if not normalize:
            if count is None:
                return similar_user_recs
            else:
                return similar_user_recs.head(count)


        # Ratings from all users
        all_user_recs = self.combined_df["Book-Title"].value_counts() / len(self.combined_df["User-ID"].unique())

        # Combine the similar user recommendations and all user recommendations
        rec_percentages = pd.concat([similar_user_recs, all_user_recs], axis=1)
        rec_percentages.columns = ["similar", "all"]

        # Take only the rows where the similar users have liked the book
        rec_percentages.dropna(inplace=True)


        # Calculate the recommendation score by dividing the percentage of similar users who liked the movie 
        # by the percentage of all users who liked the movie
        rec_percentages["score"] = rec_percentages["similar"] / rec_percentages["all"]

        if count is None:
            return rec_percentages.sort_values("score", ascending=False)
        else:
            return rec_percentages.sort_values("score", ascending=False).head(count+1)
        

    def get_recommendations_from_multiple_books(self, titles, rating_threshold=8, rating_lower_bound=7, minimum_similarity=0.03, normalize=False, count=None):
        """
        Get recommendations based on multiple book titles.

        Inputs:
        titles: list of book titles to base recommendations on
        rating_threshold: minimum rating to consider a user as similar
        rating_lower_bound: minimum rating for a book to be recommended
        minimum_similarity: minimum similarity to consider a book (0 < minimum_similarity < 1)
        normalize: whether to normalize the recommendations
        count: number of top recommendations to return

        Returns:
        aggregated_recommendations: sorted list of recommended books
        """
        combined_recs = pd.Series()

        for title in titles:
            similar_users = self.get_similar_users(title, rating_threshold)
            recs = self.get_recommendations_from_similar_users(similar_users, rating_lower_bound, minimum_similarity, normalize, count)
            combined_recs = combined_recs.add(recs, fill_value=0)

        # Aggregate recommendations by summing the scores
        aggregated_recs = combined_recs.groupby(level=0).sum()

        # Sort recommendations by score in descending order
        sorted_recs = aggregated_recs.sort_values(ascending=False)

        if count is None:
            return sorted_recs
        else:
            return sorted_recs.head(count)
            


cfmodel = CollaborativeFiltering()


if __name__ == "__main__":
    input = "The Fellowship of the Ring"
    rating_lower_bound = 8
    cf = CollaborativeFiltering()
    title = cf.search(input, result_count=1).values[0]
    print("The title is :", title)
    similar_users = cf.get_similar_users(title, rating_threshold=rating_lower_bound)
    print("Number of similar users: ", len(similar_users))

    recommendations = cf.get_recommendations_from_similar_users(similar_users, minimum_similarity=0.01, count=15, normalize=False)
    for recommendation, score in recommendations.items():
        print(recommendation, score)



