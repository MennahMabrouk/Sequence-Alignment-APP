import streamlit as st
import requests
import time

# Define the base URL for BLAST API
BLAST_API_URL = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"

def submit_blast_search(query, program, database, expect=10, word_size=11):
    """Submit a BLAST search and return the Request ID (RID)"""
    params = {
        "CMD": "Put",
        "QUERY": query,
        "PROGRAM": program,
        "DATABASE": database,
        "EXPECT": expect,
        "WORD_SIZE": word_size,
        "FORMAT_TYPE": "JSON2"  # Return results in JSON2 format
    }
    response = requests.get(BLAST_API_URL, params=params)
    
    # Check if response was successful
    if response.status_code == 200:
        return response.text.split("RID = ")[1].split("\n")[0]
    else:
        st.error("Failed to submit BLAST search. Please check your inputs.")
        return None

def check_blast_status(rid):
    """Check the status of a submitted BLAST job using the RID"""
    params = {
        "CMD": "Get",
        "RID": rid,
        "FORMAT_TYPE": "JSON2"
    }
    response = requests.get(BLAST_API_URL, params=params)
    
    if "Status=WAITING" in response.text:
        return False  # Still waiting
    elif "Status=FAILED" in response.text:
        return "Failed"
    else:
        return response.json()

# Main Streamlit app
def main():
    st.title("NCBI BLAST Search App")
    
    # Input fields
    query = st.text_area("Enter your DNA Sequence (FASTA format):")
    program = st.selectbox("Select BLAST Program", ["blastn", "blastp", "blastx", "tblastn", "tblastx"])
    database = st.selectbox("Select Database", ["nt", "nr", "swissprot", "pdb", "env_nr"])
    expect_value = st.number_input("Expect Value (E-value)", value=10.0)
    word_size = st.number_input("Word Size", value=11)
    
    if st.button("Submit Search"):
        if query:
            with st.spinner("Submitting BLAST search..."):
                rid = submit_blast_search(query, program, database, expect=expect_value, word_size=word_size)
                
                if rid:
                    st.success(f"BLAST search submitted successfully! RID: {rid}")
                    
                    # Check the status of the search
                    st.write("Checking BLAST search status...")
                    time.sleep(2)  # Wait a bit before checking status
                    
                    status = check_blast_status(rid)
                    while status == False:
                        st.write("BLAST search still processing. Checking again in 10 seconds...")
                        time.sleep(10)
                        status = check_blast_status(rid)
                    
                    if status == "Failed":
                        st.error("BLAST search failed.")
                    else:
                        st.success("BLAST search completed!")
                        st.json(status)
        else:
            st.error("Please enter a DNA sequence in FASTA format.")

if __name__ == "__main__":
    main()

