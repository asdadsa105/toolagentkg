import os
import shutil
from langchain.utilities.bing_search import BingSearchAPIWrapper
from langchain_community.utilities.wolfram_alpha import WolframAlphaAPIWrapper

import requests
import feedparser
from paperqa import Docs

from config import Config
# from ToolsFuns.utils.common import param_decorator_download_paper


def bing_search_tool(query: str) -> str:
    """
    Returns a summary of search results using the Bing Search API.

    Args:
        query (str): The query for the search.

    Returns:
        str: A summary of the search results.

    Notes: Do not use this tool when asking questions that need to be answered based on the literature
    """
    bing_search = BingSearchAPIWrapper(
        bing_subscription_key=Config().BING_SUBSCRIPTION_KEY,  
        bing_search_url=Config().BING_SEARCH_URL,     
        k=5
    )

    return bing_search.run(query)

def wolfram_alpha_query_tool(query: str) -> str:
    """
    Returns an answer to a query using the Wolfram Alpha API.

    Args:
        query (str): The query for the search.

    Returns:
        str: A summary of the answer from Wolfram Alpha.

    Notes:
    - Ensure you have a Wolfram Alpha developer account and an App ID.
    - Install the `wolframalpha` Python package via pip.
    - Set your Wolfram Alpha App ID in the WOLFRAM_ALPHA_APPID environment variable.
    """
    # Configuration for Wolfram Alpha API Wrapper
    wolfram_alpha_appid = Config().WOLFRAM_ALPHA_APPID  # Replace with your actual App ID or fetch from environment variable
    wolfram_alpha_api_wrapper = WolframAlphaAPIWrapper(
        wolfram_alpha_appid=wolfram_alpha_appid
    )

    # Run the query
    return wolfram_alpha_api_wrapper.run(query)

def get_paperqa(question):

    pdf_dir = "ToolsKG/TempFiles/arxiv_pdf"
    
    # Check if the specified directory exists
    if not os.path.exists(pdf_dir):
        return "PDF directory does not exist."

    # Get all the PDF files in the directory
    pdf_files = [os.path.join(pdf_dir, f) for f in os.listdir(pdf_dir) if f.endswith('.pdf')]

    # Check if there are any PDF files
    if not pdf_files:
        return "No PDF files in the directory."

    # Initialize Docs object and add PDF documents
    try:
        docs = Docs(llm=Config().MODEL_NAME)

        for pdf_file in pdf_files:
            docs.add(pdf_file)

        answer = docs.query(question)
        return answer.formatted_answer
    except Exception as e:
        return f"Error occurred while processing PDF files: {e}"


def download_pdf(url, filename):
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
        else:
            print(f"Failed to download {url}")

def clear_directory(path):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

# @param_decorator          
def download_papers_from_arxiv_single(keyword):
    """
    Download papers from arXiv based on a provided keyword, and return the information in Markdown format.

    Args:
        keyword (str): The keyword to search for.

    Returns:
        str: A Markdown formatted string containing the titles and URLs of the downloaded papers.

    Notes:
    Your input should ideally be in the form of something like "keyword='', max_results=10"
  """
    max_results=3
    ARXIV_API_URL = "http://export.arxiv.org/api/query"

    query_params = {
        "search_query": f"all:{keyword}",
        "start": 0,
        "max_results": max_results
    }

    download_path = "ToolsKG/TempFiles/arxiv_pdf"
    if os.path.exists(download_path) and os.listdir(download_path):
        clear_directory(download_path)
    else:
        os.makedirs(download_path, exist_ok=True)

    try:
        response = requests.get(ARXIV_API_URL, params=query_params)
        response.raise_for_status()  # Check if the request was successful
        feed = feedparser.parse(response.content)

        markdown_content = f"### Downloaded arXiv Papers (Keyword: `{keyword}`)\n\n"

        for entry in feed.entries:
            title = entry.title.replace('/', '-').replace(':', '-')
            pdf_url = entry.link.replace("abs", "pdf") + ".pdf"
            filename = os.path.join(download_path, f"{title}.pdf")

            # Download the PDF file (this step requires the definition of the download_pdf function)
            download_pdf(pdf_url, filename)

            markdown_content += f"- **[{title}]({pdf_url})**\n"

        return markdown_content

    except requests.exceptions.RequestException as e:
        return f"Error downloading papers: {e}"
    
# @param_decorator_download_paper
def download_papers_from_arxiv(keywords_str, max_results=5):
    """
    Download papers from arXiv based on provided keywords, and return the information in Markdown format.

    Args:
        keywords_str (str): A comma-separated string of keywords to search for.
        max_results (int): The maximum number of papers to download, default is 10.

    Returns:
        str: A Markdown formatted string containing the titles and URLs of the downloaded papers.

    Notes:
    Your input should ideally be in the form of something like "keywords_str='', max_results=5"
    """
    ARXIV_API_URL = "http://export.arxiv.org/api/query"

    keywords = [keyword.strip() for keyword in keywords_str.split(',') if keyword.strip()]

    # Joining the keywords with 'AND' for the query
    joined_keywords = " AND ".join(f"all:{keyword}" for keyword in keywords)
    # print(f"joined_keywords:{joined_keywords}")
    query_params = {
        "search_query": joined_keywords,
        "start": 0,
        "max_results": max_results
    }

    download_path = "ToolsKG/TempFiles/arxiv_pdf"
    if os.path.exists(download_path) and os.listdir(download_path):
        clear_directory(download_path)
    else:
        os.makedirs(download_path, exist_ok=True)

    try:
        response = requests.get(ARXIV_API_URL, params=query_params)
        response.raise_for_status()  # Check if the request was successful
        feed = feedparser.parse(response.content)
        markdown_content = f"### Downloaded arXiv Papers (Keywords: `{', '.join(keywords)}`)\n\n"

        for entry in feed.entries:
            title = entry.title.replace('/', '-').replace(':', '-')
            pdf_url = entry.link.replace("abs", "pdf") + ".pdf"
            filename = os.path.join(download_path, f"{title}.pdf")

            # Download the PDF file (this step requires the definition of the download_pdf function)
            download_pdf(pdf_url, filename)

            markdown_content += f"- **[{title}]({pdf_url})**\n"

        return markdown_content

    except requests.exceptions.RequestException as e:
        return f"Error downloading papers: {e}"


