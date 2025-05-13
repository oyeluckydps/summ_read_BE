"""
Command-line interface for MD Preprocess library.
"""

import argparse
import os
import sys
import time

from md_preprocess.core import MDPreprocessManager
from md_preprocess.utils.logging_utils import log_progress


def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Preprocess markdown files extracted from PDFs using LLMs"
    )
    
    parser.add_argument(
        "input_file", 
        help="Path to input markdown file"
    )
    
    parser.add_argument(
        "--output-dir", 
        help="Directory for final output file (default: parent directory of input file)"
    )
    
    parser.add_argument(
        "--max-attempts", 
        type=int, 
        default=3,
        help="Maximum retry attempts for code execution (default: 3)"
    )
    
    parser.add_argument(
        "--llm", 
        default="claude",
        help="LLM provider to use (default: claude)"
    )
    
    parser.add_argument(
        "--api-key", 
        help="API key for LLM service (can also use environment variable)"
    )
    
    parser.add_argument(
        "--no-cache", 
        action="store_true",
        help="Disable LLM response caching"
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()


def main():
    """
    Main CLI entry point.
    """
    # Parse arguments
    args = parse_arguments()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        log_progress(f"Input file not found: {args.input_file}", level="error")
        sys.exit(1)
    
    # Get API key from args or environment
    api_key = args.api_key
    if not api_key:
        if args.llm == "claude":
            api_key = os.environ.get("ANTHROPIC_API_KEY")
        
        if not api_key:
            log_progress(f"API key for {args.llm} not provided", level="error")
            sys.exit(1)
    
    # Use parent directory of input file as default output directory if not specified
    output_dir = args.output_dir if args.output_dir else os.path.dirname(os.path.abspath(args.input_file))
    
    # Initialize and run MDPreprocessManager
    start_time = time.time()
    
    manager = MDPreprocessManager(
        input_file=args.input_file,
        output_dir=output_dir,
        max_attempts=args.max_attempts,
        llm_name=args.llm,
        api_key=api_key,
        use_cache=not args.no_cache,
        verbose=args.verbose
    )
    
    # Process the file
    result = manager.process()
    
    # Display results
    if result["success"]:
        stats = result["statistics"]
        elapsed_time = time.time() - start_time
        
        print("\n" + "=" * 50)
        print("PREPROCESSING SUCCESSFUL")
        print("=" * 50)
        print(f"Output file: {result['output_file']}")
        print(f"Difference: {stats['diff_percentage']:.2f}%")
        print(f"Size change: {stats['size_difference']} bytes")
        print(f"Processing time: {elapsed_time:.2f} seconds")
        print("=" * 50)
    else:
        elapsed_time = time.time() - start_time
        print("\n" + "=" * 50)
        print("PREPROCESSING FAILED")
        print("=" * 50)
        print(f"Errors encountered: {', '.join(result['errors'])}")
        print(f"Processing time: {elapsed_time:.2f} seconds")
        print("=" * 50)
        sys.exit(1)


if __name__ == "__main__":
    main()