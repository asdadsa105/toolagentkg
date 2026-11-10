
from bs4 import BeautifulSoup
import pandas as pd

def extract_and_process_protparam_html(html_content):
    """
    Extract and clean relevant content from ProtParam HTML response.

    Args:
        html_content (str): Raw HTML content.

    Returns:
        str: Processed content with only relevant sections.
    """
    try:
        soup = BeautifulSoup(html_content, "html.parser")

        pre_tags = soup.find_all("pre")
        if not pre_tags or len(pre_tags) < 2:
            raise ValueError("Failed to locate the correct <pre> tag in the HTML content.")

        parameter_pre = pre_tags[1]

        # Extract lines of interest
        pre_lines = parameter_pre.get_text().strip().split("\n")

        # print("Extracted <pre> lines:")
        # for line in pre_lines:
        #     print(line)

        # Find start and end lines
        start_line = next((i for i, line in enumerate(pre_lines) if "Number of amino acids:" in line), None)
        end_line = next((i for i, line in enumerate(pre_lines) if "Grand average of hydropathicity (GRAVY):" in line), None)

        if start_line is None or end_line is None:
            raise ValueError("Failed to locate the required content in <pre>.")

        # Extract relevant lines
        relevant_lines = pre_lines[start_line:end_line + 1]

        # Convert to readable Markdown-like format
        formatted_output = "\n".join(relevant_lines)
        return formatted_output

    except Exception as e:
        return f"Error processing ProtParam HTML: {e}"

def convert_protparam_to_markdown(cleaned_html_content):
    """
    Convert ProtParam cleaned HTML content to Markdown.

    Args:
        cleaned_html_content (str): Cleaned HTML content.

    Returns:
        str: Markdown representation of the content.
    """
    lines = cleaned_html_content.strip().split("\n")
    markdown_output = "## ProtParam Results\n\n"

    for line in lines:
        # Use basic formatting for Markdown
        markdown_output += f"- {line.strip()}\n"

    return markdown_output

def parse_pd_data(pd_data):
    """
    Parse protein transmembrane prediction data into a DataFrame.

    Args:
        pd_data (list): List of strings representing prediction data.

    Returns:
        pd.DataFrame: Parsed data in tabular form.
    """
    try:
        parsed_data = {"Type": [], "Start": [], "End": []}

        for item in pd_data:
            parts = item.split()
            if len(parts) == 3:
                region = parts[0]
                start = int(parts[1])
                end = int(parts[2])

                parsed_data["Type"].append(region)
                parsed_data["Start"].append(start)
                parsed_data["End"].append(end)
            else:
                print(f"Data format error: {item}")

        return pd.DataFrame(parsed_data)
    except Exception as e:
        print("Error parsing data:", e)
        return pd.DataFrame()