import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from transformers import pipeline
from bs4 import BeautifulSoup
import nltk

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Function to fetch country names and their ISO codes from an open-source API
def fetch_country_data():
    api_url = "https://restcountries.com/v3.1/all"
    response = requests.get(api_url)
    if response.status_code == 200:
        countries = response.json()
        country_data = {country['name']['common']: country['cca2'] for country in countries}
        return country_data
    else:
        st.error("Failed to fetch country data")
        return {}

# Function to get male and female population
def get_population_data(country):
    api_url = f"https://restcountries.com/v3.1/name/{country}"
    
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()[0]
            total_population = data.get('population', 'N/A')
            
            if total_population != 'N/A':
                # Hypothetical percentage distribution (adjust based on real data if available)
                male_percentage = 0.51
                female_percentage = 0.49
                
                male_population = int(total_population * male_percentage)
                female_population = int(total_population * female_percentage)
                
                return male_population, female_population, total_population
            else:
                return 'N/A', 'N/A', 'N/A'
        else:
            st.error(f"Failed to fetch data: {response.status_code}")
            return 'N/A', 'N/A', 'N/A'
    except requests.exceptions.RequestException as e:
        st.error(f"Request error: {e}")
        return 'N/A', 'N/A', 'N/A'

# Function to scrape website content
def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    text = ' '.join([p.text for p in soup.find_all('p')])
    return text

# Function to preprocess text
def preprocess_text(text):
    text = re.sub('[^a-zA-Z]', ' ', text)
    text = text.lower()
    words = word_tokenize(text)
    words = [word for word in words if word not in stopwords.words('english')]
    return ' '.join(words)

# Function to generate ad copies
def generate_ad_copies(summary, country):
    google_ads = f"Looking for {summary}? Get the best services in {country} now!"
    meta_ads = f"Explore top-notch {summary} services in {country}. Click here to learn more!"
    return google_ads, meta_ads

# Function to generate a blog post
def generate_blog(summary, country):
    blog_intro = f"Are you looking for the best {summary}? Look no further!"
    blog_body = f"In {country}, our {summary} services stand out for their quality and reliability."
    return f"{blog_intro}\n\n{blog_body}"

# Function to get social media users
def get_social_media_users(country):
    try:
        url = "https://www.statista.com/statistics/278341/number-of-social-network-users-in-selected-countries/"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'table'})
            if table:
                rows = table.find_all('tr')
                data = {}
                for row in rows[1:]:
                    cols = row.find_all('td')
                    country_name = cols[0].text.strip()
                    users = cols[1].text.strip().replace(",", "")
                    data[country_name] = users
                return data.get(country, 'N/A')
    except Exception as e:
        st.error(f"An error occurred while fetching social media users: {e}")
    return 'N/A'

# Functions to get average customer spend
industry_average_spend = {
    "Advocacy": {"India": 3000, "United States": 5000, "Canada": 4500, "United Kingdom": 4700, "average": 4425},
    "Auto": {"India": 15000, "United States": 20000, "Canada": 18000, "United Kingdom": 19000, "average": 18000},
    "B2B": {"India": 12000, "United States": 17000, "Canada": 16000, "United Kingdom": 16500, "average": 15375},
    "Consumer Services": {"India": 8000, "United States": 12000, "Canada": 10000, "United Kingdom": 11000, "average": 10250},
    "E-commerce": {"India": 25000, "United States": 35000, "Canada": 32000, "United Kingdom": 34000, "average": 31500},
    "Education": {"India": 20000, "United States": 30000, "Canada": 28000, "United Kingdom": 29000, "average": 26750},
    "Finance & Insurance": {"India": 22000, "United States": 33000, "Canada": 31000, "United Kingdom": 32000, "average": 29500},
    "Health & Medical": {"India": 12000, "United States": 18000, "Canada": 17000, "United Kingdom": 17500, "average": 16125},
    "Home Goods": {"India": 10000, "United States": 15000, "Canada": 14000, "United Kingdom": 14500, "average": 13375},
    "Industrial Services": {"India": 14000, "United States": 21000, "Canada": 19000, "United Kingdom": 20000, "average": 18500},
    "Legal": {"India": 18000, "United States": 27000, "Canada": 25000, "United Kingdom": 26000, "average": 24000},
    "Real Estate": {"India": 150000, "United States": 200000, "Canada": 180000, "United Kingdom": 190000, "average": 180000},
    "Technology": {"India": 50000, "United States": 70000, "Canada": 65000, "United Kingdom": 67000, "average": 63000},
    "Travel & Hospitality": {"India": 20000, "United States": 30000, "Canada": 28000, "United Kingdom": 29000, "average": 26750}
}

def get_average_customer_spend(industry, country):
    return industry_average_spend.get(industry, {}).get(country, 'N/A')

def get_industry_average_spend(industry):
    return industry_average_spend.get(industry, {}).get("average", 'N/A')

# Function to create marketing proposal
def create_marketing_proposal(industry, country):
    country_data = fetch_country_data()
    country_code = country_data.get(country)
    if not country_code:
        return pd.DataFrame([{
            'Industry': industry,
            'Country': country,
            'Male:Female Ratio': 'N/A',
            'Active Social Media Users': 'N/A',
            'Average Customer Spend': 'N/A'
        }])

    male_population, female_population, total_population = get_population_data(country)
    social_media_users = get_social_media_users(country)
    average_spend = get_average_customer_spend(industry, country)
    industry_average = get_industry_average_spend(industry)

    non_social_media_users = float(total_population) - float(social_media_users) * 1e6 if total_population != 'N/A' and social_media_users != 'N/A' else 'N/A'

    proposal_data = {
        'Industry': industry,
        'Country': country,
        'Male:Female Ratio': f"{male_population}:{female_population}" if male_population != 'N/A' and female_population != 'N/A' else 'N/A',
        'Active Social Media Users': social_media_users + " million" if social_media_users != 'N/A' else 'N/A',
        'Average Customer Spend': "USD " + str(average_spend) if average_spend != 'N/A' else 'N/A'
    }

    return pd.DataFrame([proposal_data]), male_population, female_population, social_media_users, non_social_media_users, average_spend, industry_average

# Function to plot charts
def plot_charts(male_population, female_population, social_media_users, non_social_media_users, average_spend, industry_average, country):
    fig, axs = plt.subplots(1, 3, figsize=(18, 6))

    # Male:Female Ratio
    if male_population != 'N/A' and female_population != 'N/A':
        axs[0].pie([male_population, female_population], labels=['Male', 'Female'], autopct='%1.1f%%', colors=['blue', 'pink'])
        axs[0].set_title(f'Male:Female Ratio in {country}')

    # Social Media vs Non-Social Media Users
    # Social Media vs Non-Social Media Users
    if social_media_users != 'N/A' and non_social_media_users != 'N/A':
        axs[1].pie([float(social_media_users) * 1e6, non_social_media_users], labels=['Social Media Users', 'Non-Social Media Users'], autopct='%1.1f%%', colors=['green', 'grey'])
        axs[1].set_title(f'Social Media vs Non-Social Media Users in {country}')

    # Average Customer Spend
    if average_spend != 'N/A' and industry_average != 'N/A':
        axs[2].bar(['Country Spend', 'Industry Average'], [float(average_spend), float(industry_average)], color=['orange', 'blue'])
        axs[2].set_title(f'Average Customer Spend in {country} vs Industry Average (USD)')

    plt.tight_layout()
    st.pyplot(fig)

# Function to scrape conversion rate data
def scrape_conversion_rates():
    url = "https://www.statista.com/statistics/1106713/global-conversion-rate-by-industry-and-device/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    rows = table.find_all('tr')

    conversion_rate = {}
    for row in rows[1:]:
        cols = row.find_all('td')
        industry = cols[0].text.strip()
        rate_text = cols[1].text.strip().replace('%', '')
        try:
            rate = float(rate_text) / 100  # Convert to decimal
        except ValueError:
            rate = 0  # Default to 0 if the value is not a number
        conversion_rate[industry] = rate

    return conversion_rate

# Function to scrape CTR data
def scrape_ctr_data():
    url = "https://www.wordstream.com/blog/ws/2016/02/29/google-adwords-industry-benchmarks"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    rows = table.find_all('tr')

    ctr_data = {}
    for row in rows[1:]:
        cols = row.find_all('td')
        industry = cols[0].text.strip()
        ctr_text = cols[1].text.strip().replace('%', '')
        try:
            ctr = float(ctr_text)
        except ValueError:
            ctr = 0  # Default to 0 if the value is not a number
        ctr_data[industry] = ctr

    return ctr_data

# Mock data for industry average CPC and cost per conversion (for demonstration purposes)
industry_data = {
    'Advocacy': {'avg_cpc': 1.5, 'cost_per_conversion': 20},
    'Auto': {'avg_cpc': 2.0, 'cost_per_conversion': 30},
    'B2B': {'avg_cpc': 3.0, 'cost_per_conversion': 50},
    'Consumer Services': {'avg_cpc': 4.0, 'cost_per_conversion': 60},
    'Dating & Personals': {'avg_cpc': 2.5, 'cost_per_conversion': 40},
    'E-commerce': {'avg_cpc': 1.2, 'cost_per_conversion': 25},
    'Education': {'avg_cpc': 2.1, 'cost_per_conversion': 35},
    'Employment Services': {'avg_cpc': 1.8, 'cost_per_conversion': 30},
    'Finance & Insurance': {'avg_cpc': 3.5, 'cost_per_conversion': 55},
    'Health & Medical': {'avg_cpc': 2.8, 'cost_per_conversion': 45},
    'Home Goods': {'avg_cpc': 1.7, 'cost_per_conversion': 28},
    'Industrial Services': {'avg_cpc': 2.2, 'cost_per_conversion': 38},
    'Legal': {'avg_cpc': 5.0, 'cost_per_conversion': 75},
    'Real Estate': {'avg_cpc': 2.4, 'cost_per_conversion': 33},  # This is where you can adjust the values
    'Technology': {'avg_cpc': 3.2, 'cost_per_conversion': 50},
    'Travel & Hospitality': {'avg_cpc': 1.9, 'cost_per_conversion': 30}
}

# Streamlit App
st.title("Media Plan Calculator")

# Scrape data
conversion_rate = scrape_conversion_rates()
ctr_data = scrape_ctr_data()

# Select Industry
industry = st.selectbox("Select Industry", options=list(industry_data.keys()))

# Select Country
country = st.selectbox("Select Country", options=['USA', 'Canada', 'UK', 'Germany', 'France', 'India', 'China', 'Australia'])

# Enter Budget
budget = st.number_input("Enter Monthly Budget ($)", value=1000.0)

if st.button("Calculate"):
    ctr = ctr_data.get(industry, 0) / 100  # Convert percentage to decimal
    avg_cpc = industry_data[industry]['avg_cpc']
    cost_per_conversion = industry_data[industry]['cost_per_conversion']  # Directly use the benchmark

    # Retrieve conversion rate from your conversion_rate data
    conversion_rate_value = conversion_rate.get(industry, 0.01)  # Default to 1% if not available

    impressions = budget / avg_cpc
    clicks = impressions * ctr
    conversions = clicks * conversion_rate_value

    # Display Results
    st.write(f"Results for {industry} industry with a budget of ${budget} in {country}:")
    st.write(f"**Impressions:** {impressions:.0f}")
    st.write(f"**Clicks:** {clicks:.0f}")
    st.write(f"**Conversions:** {conversions:.0f}")
    st.write(f"**Cost Per Conversion (Benchmark):** ${cost_per_conversion:.2f}")

# Streamlit App for Market Trends
st.title("General Market Trend")

# Fetch country data
country_data = fetch_country_data()
industries = list(industry_average_spend.keys())
country_names = sorted(country_data.keys())

# Streamlit UI elements
industry = st.selectbox('Select Industry', industries)
country = st.selectbox('Select Country', country_names)

if st.button('Get Market Trend'):
    marketing_proposal, male_population, female_population, social_media_users, non_social_media_users, average_spend, industry_average = create_marketing_proposal(industry, country)
    st.write(marketing_proposal)
    plot_charts(male_population, female_population, social_media_users, non_social_media_users, average_spend, industry_average, country)

# Streamlit App for Website Summarization
st.header("Website Summarization")
url = st.text_input('Enter Website URL')

if st.button('Summarize Website'):
    content = scrape_website(url)
    preprocessed_content = preprocess_text(content)
    summarizer = pipeline('summarization')
    summary = summarizer(preprocessed_content, max_length=150, min_length=50, do_sample=False)
    st.subheader("Business Model Summary")
    st.write(summary[0]['summary_text'])

    # Generate ad copies and blog post
    google_ad, meta_ad = generate_ad_copies(summary[0]['summary_text'], country)
    blog_post = generate_blog(summary[0]['summary_text'], country)

    st.subheader("Google Ad Copy")
    st.write(google_ad)
    st.subheader("Meta Ad Copy")
    st.write(meta_ad)
    st.subheader("Sample Blog Post")
    st.write(blog_post)
