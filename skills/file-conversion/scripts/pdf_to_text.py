#!/usr/bin/env python3
"""PDF to text converter"""
import argparse
import sys

def pdf_to_text(input_path, output_path=None, pages=None):
    try:
        import pdfplumber
        
        text_parts = []
        with pdfplumber.open(input_path) as pdf:
            page_nums = range(len(pdf.pages))
            if pages:
                page_nums = [int(p)-1 for p in pages.split(',')]
            
            for i in page_nums:
                if i < len(pdf.pages):
                    page = pdf.pages[i]
                    text_parts.append(page.extract_text() or '')
        
        full_text = '\n\n'.join(text_parts)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(full_text)
            return {'success': True, 'pages': len(page_nums), 'output': output_path}
        else:
            return {'success': True, 'text': full_text, 'pages': len(page_nums)}
    except ImportError:
        return {'error': 'pdfplumber not installed. Run: pip install pdfplumber'}
    except Exception as e:
        return {'error': str(e)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', required=True)
    parser.add_argument('--output', '-o')
    parser.add_argument('--pages', '-p')
    parser.add_argument('--json', '-j', action='store_true')
    args = parser.parse_args()
    
    result = pdf_to_text(args.input, args.output, args.pages)
    
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        if 'error' in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        elif args.output:
            print(f"Extracted {result['pages']} pages to {args.output}")
        else:
            print(result['text'])

if __name__ == '__main__':
    main()
