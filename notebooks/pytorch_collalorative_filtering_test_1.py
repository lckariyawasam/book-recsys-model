# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import pandas as pd
from sklearn.model_selection import train_test_split

# Import the dataset
users = pd.read_csv("data/Users.csv")
users.head()

users.describe()

users.isna().sum()

books = pd.read_csv("data/minified/cleaned_books_reduced.csv")
books.head(5)

books.isna().sum()

ratings = pd.read_csv("data/minified/cleaned_ratings_reduced.csv")
ratings.head()

len(ratings)

# Split data into training and validation sets
train_indices, val_indices = train_test_split(range(len(ratings)), test_size=0.2, random_state=42)

user_ids = ratings['User-ID'].astype('category').cat.codes.values
isbns = ratings['Book-ID'].astype('category').cat.codes.values
book_ratings = ratings['Book-Rating'].values.astype(float)

train_user_ids = user_ids[train_indices]
train_isbns= isbns[train_indices]
train_ratings = book_ratings[train_indices]

val_user_ids = user_ids[val_indices]
val_isbns = isbns[val_indices]
val_ratings = book_ratings[val_indices]

train_user_ids

if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)} is available.")
else:
    print("No GPU available. Training will run on CPU.")

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(device)

class RatingDataset(Dataset):
    def __init__(self, user_ids, isbns, ratings):
        self.user_ids = torch.tensor(user_ids, dtype=torch.long)
        self.isbns = torch.tensor(isbns, dtype=torch.long)
        self.ratings = torch.tensor(ratings, dtype=torch.float32)

        if device == "cuda":
          self.user_ids = self.user_ids.to('cuda')
          self.isbns = self.isbns.to('cuda')
          self.ratings = self.ratings.to('cuda')


    def __len__(self):
        return len(self.ratings)

    def __getitem__(self, idx):
        return self.user_ids[idx], self.isbns[idx], self.ratings[idx]

# Create DataLoader instances for training and validation
train_dataset = RatingDataset(train_user_ids, train_isbns, train_ratings)
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

val_dataset = RatingDataset(val_user_ids, val_isbns, val_ratings)
val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)

class CollaborativeFiltering(nn.Module):
    def __init__(self, num_users, num_books, embedding_dim=50):
        super(CollaborativeFiltering, self).__init__()
        self.user_embedding = nn.Embedding(num_users, embedding_dim)
        self.book_embedding = nn.Embedding(num_books, embedding_dim)
        self.fc = nn.Linear(embedding_dim * 2, 1)

    def forward(self, user_ids, book_ids):
        user_embedded = self.user_embedding(user_ids)
        book_embedded = self.book_embedding(book_ids)
        concatenated = torch.cat([user_embedded, book_embedded], dim=1)
        output = self.fc(concatenated)
        return output.squeeze()

# Initialize the model, optimizer, and loss function
model = CollaborativeFiltering(num_users=len(user_ids), num_books=len(isbns), embedding_dim=32).to(device)

optimizer = optim.Adam(model.parameters(), lr=0.001)
criterion = nn.MSELoss()

# Training loop
def train_epoch(model, dataloader, criterion, optimizer):
    model.to(device)
    model.train()
    epoch_loss = 0.0
    for user_ids, isbns, ratings in dataloader:
        user_ids, isbns, ratings = user_ids.to(device), isbns.to(device), ratings.to(device)
        optimizer.zero_grad()
        outputs = model(user_ids, isbns)
        loss = criterion(outputs, ratings)
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item()
    return epoch_loss / len(dataloader)

# Validation loop
def evaluate(model, dataloader, criterion):
    model.eval()
    epoch_loss = 0.0
    with torch.no_grad():
        for user_ids, isbns, ratings in dataloader:
            user_ids, isbns, ratings = user_ids.to(device), isbns.to(device), ratings.to(device)
            outputs = model(user_ids, isbns)
            loss = criterion(outputs, ratings)
            epoch_loss += loss.item()
    return epoch_loss / len(dataloader)

# Training the model
num_epochs = 10
for epoch in range(num_epochs):
    train_loss = train_epoch(model, train_loader, criterion, optimizer)
    val_loss = evaluate(model, val_loader, criterion)
    print(f"Epoch {epoch+1}, Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")



"""This run has clearly overfit to the traininig data, incrasing validation error for each epoch. Need to retry again with different architecture
:(
"""

# Generate predications
def predict_rating(model, user_id, isbn):
    model.eval()
    with torch.no_grad():
        user_id = torch.tensor([user_id], dtype=torch.long).to(device)
        isbn = torch.tensor([isbn], dtype=torch.long).to(device)
        rating = model(user_id, isbn)
    return rating.item()


# # Predicting ratings for a few users and books
# user_id = 1
# isbn = 1

# predicted_rating = predict_rating(model, user_id, isbn)
# predicted_rating


# Get the most similar book to a given book
def most_similar_books(model, isbn, n=5):
    book_embedding = model.book_embedding.weight.data
    book_vector = book_embedding[isbn]
    similarities = torch.matmul(book_embedding, book_vector)
    similarities, indices = torch.topk(similarities, n+1)
    return similarities, indices


# Get the most similar books to the first book
similarities, indices = most_similar_books(model, 0)