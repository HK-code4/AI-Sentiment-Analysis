import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import numpy as np
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns
import re
from transformers import pipeline
from sklearn.model_selection import train_test_split
from wordcloud import WordCloud
from io import StringIO
import scipy as sp
from sklearn.preprocessing import LabelEncoder


def fetch_google_sheet_data(url):
    csv_url = url.replace('/edit?usp=sharing', '/gviz/tq?tqx=out:csv').replace('/pubhtml', '/pub?output=csv')

    try:
        response = requests.get(csv_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve the sheet: {e}")
        return None

    data = StringIO(response.text)
    df = pd.read_csv(data, on_bad_lines='skip')

    return df


def main():
    url = input("Enter the product page URL: ")

    df = fetch_google_sheet_data(url)
    if df is None:
        print("Failed to fetch product data.")
        return

    print(df)
    return (df)


if __name__ == "__main__":
    df = main()


def check_data_types(df):
    categorical_columns = []
    numerical_columns = []

    for column in df.columns:
        if pd.api.types.is_numeric_dtype(df[column]):
            numerical_columns.append(column)
        elif pd.api.types.is_categorical_dtype(df[column]) or df[column].dtype == 'object':
            categorical_columns.append(column)

    return categorical_columns, numerical_columns


categorical_columns, numerical_columns = check_data_types(df)
print("Categorical columns:", categorical_columns)
print("Numerical columns:", numerical_columns)

pd.set_option('display.max_columns', None)

print(df.columns)
print("Shape:",df.shape)
df.info()

df['rating'] = df['rating'].astype(str).str.replace('|', '3.9').astype('float64')
df['rating_count'] = df['rating_count'].str.replace(',', '').astype('float64')

df.describe()
df.isnull().sum().sort_values(ascending=False)
df.isnull().sum().sum()

# missing values
plt.figure(figsize=(22, 10))
sns.heatmap(df.isnull(), yticklabels=False, cbar=False, cmap='viridis')

plt.figure(figsize=(22, 10))
missing_percentage = df.isnull().sum() / len(df) * 100
missing_percentage.plot(kind='bar')

plt.xlabel('Columns')
plt.ylabel('Percentage')
plt.title('Percentage of Missing Values in each Column')

df[df['rating_count'].isnull()].head(5)
df['rating_count'] = df.rating_count.fillna(value=df['rating_count'].median())

df.isnull().sum()
df.duplicated().sum()

# Scatter Plot
plt.scatter(df['rating'], df['rating_count'])
plt.xlabel('Rating')
plt.ylabel('Rating Count')
plt.title('Rating vs. Rating Count')
plt.show()

plt.scatter(df['actual_price'], df['rating'])
plt.xlabel('Actual Price')
plt.ylabel('Rating')
plt.title('Actual Price vs. Rating')
plt.show()

# Histogram
plt.hist(df['rating'])
plt.xlabel('Rating')
plt.ylabel('Frequency')
plt.title('Distribution of Ratings')
plt.show()

plt.hist(df['actual_price'])
plt.xlabel('Actual Price')
plt.ylabel('Frequency')
plt.title('Distribution of Actual Price')
plt.show()

# Box-plot
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, y="rating")
plt.title("Box Plot of Ratings")
plt.ylabel("Rating")
plt.show()

plt.figure(figsize=(10, 6))
sns.boxplot(data=df, y="actual_price")
plt.title("Box Plot of Actual Price")
plt.ylabel("Actual Price")
plt.show()

# LabelEncoder: Categorical data in to integral values
le_product_id = LabelEncoder()
le_category = LabelEncoder()
le_review_id = LabelEncoder()
le_review_content = LabelEncoder()
le_product_name = LabelEncoder()
le_user_name = LabelEncoder()
le_about_product = LabelEncoder()
le_user_id = LabelEncoder()
le_review_title = LabelEncoder()
le_img_link = LabelEncoder()
le_product_link = LabelEncoder()

df['product_id'] = le_product_id.fit_transform(df['product_id'])
df['category'] = le_category.fit_transform(df['category'])
df['review_id'] = le_review_id.fit_transform(df['review_id'])
df['review_content'] = le_review_content.fit_transform(df['review_content'])
df['product_name'] = le_product_name.fit_transform(df['product_name'])
df['user_name'] = le_user_name.fit_transform(df['user_name'])
df['about_product'] = le_about_product.fit_transform(df['about_product'])
df['user_id'] = le_user_id.fit_transform(df['user_id'])
df['review_title'] = le_review_title.fit_transform(df['review_title'])
df['img_link'] = le_img_link.fit_transform(df['img_link'])
df['product_link'] = le_product_link.fit_transform(df['product_link'])

print(df['actual_price'].dtype)

if df['actual_price'].dtype != object:
    df['actual_price'] = df['actual_price'].astype(str)

df['actual_price'] = df['actual_price'].str.replace('₹', '', regex=False).str.replace(',', '', regex=False)
df['actual_price'] = df['actual_price'].str.replace('â¹', '', regex=False)
df['actual_price'] = pd.to_numeric(df['actual_price'], errors='coerce')

correlation_matrix = df.corr(numeric_only=True)
sns.heatmap(correlation_matrix, annot=True)
plt.show()

correlation_coefficient = np.corrcoef(df['actual_price'], df['rating'])[0, 1]
print(correlation_coefficient)

df['sentiment'] = df['cleaned_review'].apply(analyze_sentiment)

# Extract keywords for each review
df['keywords'] = extract_keywords(df['cleaned_review'])

# Display the first few results
print(df[['review_content', 'sentiment', 'keywords']].head())