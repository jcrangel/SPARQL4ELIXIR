"""
python generate_dataset_community.py xsearch_cell20240822.ttl path_dataset.json --use_labels --filter_empty_results
"""

import argparse
import os
from GraphDatasetGenerator import GraphDatasetGenerator  # Assuming this is in 'graph_dataset_generator.py'
from EndpointRiken import Endpoint as EndpointRiken # Import the Endpoint class
from Endpoint import Endpoint  # Import the Endpoint class
from configs import ENDPOINT_T_BOX_URL
import csv
# from bs4 import BeautifulSoup
import json

def main():
    parser = argparse.ArgumentParser(description="Generate NL2SPARQL datasets from an RDF graph.")
    parser.add_argument('graph_file', type=str, help="The path to the RDF graph file.")
    parser.add_argument('output_file', type=str, help="The path to the output JSON file.")
    parser.add_argument('--model_name', type=str, default="gpt-4o", help="The OpenAI model to use.")
    parser.add_argument('--use_labels', action='store_true', help="Use labels for entities and predicates.")
    parser.add_argument('--k', type=int, default=2, help="Path length k.")
    parser.add_argument('--top_n', type=int, default=10, help="Number of top paths to consider.")
    parser.add_argument('--sample_size', type=int, default=1, help="Number of samples per path.")
    parser.add_argument('--filter_empty_results', action='store_true', help="Filter out queries with empty results.")
    parser.add_argument('--use_riken', action='store_true', help="Use Riken's SPARQL endpoint.",default=False)
    parser.add_argument('--url_endpoint', type=str, required=True, help="SPARQL endpoint URL.")
    parser.add_argument('--database', type=str, help="Database name or URL for the endpoint (required if --use_riken is set).")
    parser.add_argument('--community_detection_method', type=str, default='path', choices=['path', 'louvain'],
                        help="Community detection method to use ('path' or 'louvain').")
    parser.add_argument('--examples_file', type=str, help="The examples of questions and SPARQL queries.")
    
    args = parser.parse_args()

    print("Using model: ", args.model_name) 
    # Initialize the Endpoint
    if args.use_riken:
        print("Using Riken's SPARQL endpoint.")
        if not args.database:
            parser.error("--database is required when --use_riken is set")

        endpoint_t_box = EndpointRiken(url_endpoint=args.url_endpoint, database=args.database)
    else:
        endpoint_t_box = Endpoint(url_endpoint=args.url_endpoint)

    # def clean_html(text):
    #     return BeautifulSoup(text, "html.parser").get_text()


    def concatenate_question_query(json_file_path):
        # Read the JSON file
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        
        # Extract bindings
        bindings = data.get("results", {}).get("bindings", [])
        concatenated_strings = ""
        
        # Iterate through each binding and concatenate "question" and "query" values
        for binding in bindings:
            question = binding.get("question", {}).get("value", "")
            query = binding.get("query", {}).get("value", "")
            concatenated_strings += f"QUESTION: {question}\n QUERY:\n  {query}\n"
        
        return concatenated_strings



    # Initialize the GraphDatasetGenerator with the selected method
    generator = GraphDatasetGenerator(
        graph_file=args.graph_file,
        endpoint=endpoint_t_box,
        model_name=args.model_name,
        use_labels=args.use_labels,
        # community_detection_method=args.community_detection_method  # Pass the new parameter
    )

    print(" Generating the dataset " )
    
    generator.generate_dataset(
        output_file=args.output_file,
        k=args.k,
        top_n=args.top_n,
        sample_size=args.sample_size,#For each class paths how many samples(instance paths) use to generate question, one per sample
        filter_empty_results=args.filter_empty_results,
        examples=concatenate_question_query(args.examples_file) if args.examples_file else None
    )

if __name__ == "__main__":
    main()
