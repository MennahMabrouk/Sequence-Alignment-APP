import streamlit as st
import requests

# Define the base URL for NCBI E-utilities API
NCBI_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
NCBI_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

def search_ncbi(query, db="nucleotide", retmax=5):
    """Search NCBI database with a query"""
    params = {
        "db": db,           # Database to search (e.g., nucleotide, gene)
        "term": query,      # The search query
        "retmax": retmax,   # Number of results to return
        "retmode": "json",  # Return results in JSON format
    }
    response = requests.get(NCBI_SEARCH_URL, params=params)
    
    # Debugging: print the raw URL for checking
    st.write(f"Search URL: {response.url}")
    
    if response.status_code == 200:
        st.write(f"Search Response: {response.json()}")  # Debugging: Show the full response
        return response.json()
    else:
        st.error("Failed to retrieve data from NCBI. Please try again later.")
        return None

def fetch_ncbi_data(id_list, db="nucleotide"):
    """Fetch data for the given NCBI IDs"""
    ids = ",".join(id_list)
    params = {
        "db": db,
        "id": ids,
        "retmode": "text",  # Can be set to "xml" or "text" depending on need
        "rettype": "fasta"  # Return FASTA sequence data
    }
    response = requests.get(NCBI_FETCH_URL, params=params)
    
    # Debugging: print the raw URL for checking
    st.write(f"Fetch URL: {response.url}")
    
    if response.status_code == 200:
        st.write(f"Fetch Response: {response.text[:500]}...")  # Debugging: Show a part of the fetched data
        return response.text
    else:
        st.error("Failed to fetch data from NCBI. Please try again later.")
        return None

# Main Streamlit app
def main():
    st.title("NCBI Gene/Sequence Search")
    
    # Input field for gene name or term
    query = st.text_input("Enter a term (e.g., ADHD, depression, partial sequence):")
    
    if st.button("Search"):
        if query:
            with st.spinner("Searching NCBI for relevant data..."):
                # Search NCBI for the query in the nucleotide database
                search_results = search_ncbi(query)
                
                if search_results and "esearchresult" in search_results:
                    id_list = search_results["esearchresult"].get("idlist", [])
                    
                    if id_list:
                        st.success(f"Found {len(id_list)} results. Fetching data...")
                        
                        # Fetch data for the first few IDs
                        fasta_data = fetch_ncbi_data(id_list)
                        
                        # Display the fetched FASTA data
                        st.text_area("FASTA Sequence Data", fasta_data, height=300)
                    else:
                        st.warning("No relevant results found for the query.")
        else:
            st.error("Please enter a search term.")

