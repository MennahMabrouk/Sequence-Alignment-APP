import streamlit as st
import requests

# Define the base URL for NCBI E-utilities API
NCBI_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
NCBI_SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
NCBI_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# Function to search NCBI database with a query
def search_ncbi(query, db="nucleotide", retmax=5):
    """Search NCBI database with a query"""
    params = {
        "db": db,           # Database to search (e.g., nucleotide, gene)
        "term": query,      # The search query
        "retmax": retmax,   # Number of results to return
        "retmode": "json",  # Return results in JSON format
    }
    response = requests.get(NCBI_SEARCH_URL, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to retrieve data from NCBI. Please try again later.")
        return None

# Function to fetch gene metadata (like gene name) from NCBI using esummary
def fetch_ncbi_summary(id_list, db="nucleotide"):
    """Fetch gene metadata (summary) for the given NCBI IDs"""
    ids = ",".join(id_list)
    params = {
        "db": db,
        "id": ids,
        "retmode": "json",  # Return JSON summary
    }
    response = requests.get(NCBI_SUMMARY_URL, params=params)
    
    if response.status_code == 200:
        summaries = response.json()["result"]
        return summaries
    else:
        st.error("Failed to fetch gene summary from NCBI. Please try again later.")
        return None

# Function to fetch FASTA data for given NCBI IDs
def fetch_ncbi_fasta(id_list, db="nucleotide"):
    """Fetch FASTA sequence data for the given NCBI IDs"""
    ids = ",".join(id_list)
    params = {
        "db": db,
        "id": ids,
        "retmode": "text",  # Fetch as text format
        "rettype": "fasta"  # Return FASTA sequence data
    }
    response = requests.get(NCBI_FETCH_URL, params=params)
    
    if response.status_code == 200:
        return response.text
    else:
        st.error("Failed to fetch FASTA data from NCBI. Please try again later.")
        return None

# Main Streamlit app function
def main():
    st.title("NCBI Gene/Sequence Search")
    
    # State to store the current query
    if 'query' not in st.session_state:
        st.session_state.query = ''
    
    # Function to trigger search when "Enter" is pressed
    def on_query_change():
        query = st.session_state.query
        if query:
            with st.spinner("Searching NCBI for relevant data..."):
                # Search NCBI for the query in the nucleotide database
                search_results = search_ncbi(query)
                
                if search_results and "esearchresult" in search_results:
                    id_list = search_results["esearchresult"].get("idlist", [])
                    
                    if id_list:
                        # Limit to the first two IDs
                        id_list = id_list[:2]  # Take the first two results
                        
                        # Fetch gene metadata (gene name)
                        summaries = fetch_ncbi_summary(id_list)
                        fasta_data = fetch_ncbi_fasta(id_list)
                        
                        # Display the gene names and FASTA sequence
                        for gene_id in id_list:
                            gene_info = summaries.get(gene_id, {})
                            gene_name = gene_info.get("title", "Unknown Gene Name")
                            st.write(f"**Gene Name**: {gene_name}")
                        
                        # Display the fetched FASTA data
                        st.text_area("FASTA Sequence Data", fasta_data, height=300)
                    else:
                        st.warning("No relevant results found for the query.")
        else:
            st.error("Please enter a search term.")
    
    # Input field for gene name or term, with on_change to search when pressing Enter
    st.text_input("Enter a term (e.g., ADHD, depression, partial sequence):", 
                  key='query', 
                  on_change=on_query_change)

if __name__ == "__main__":
    main()
