#!/usr/bin/env python3
"""Image format converter"""
import argparse
import sys
import os

def convert_image(input_path, output_path, format=None, quality=90, resize=None):
    try:
        from PIL import Image
        
        with Image.open(input_path) as img:
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            if resize:
                width, height = map(int, resize.split('x'))
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Determine format from output extension if not specified
            if not format:
                format = os.path.splitext(output_path)[1].upper().replace('.', '')
                if format == 'JPG':
                    format = 'JPEG'
            
            save_kwargs = {}
            if format in ('JPEG', 'WEBP'):
                save_kwargs['quality'] = quality
            
            img.save(output_path, format=format, **save_kwargs)
            return {'success': True, 'output': output_path, 'format': format}
    except ImportError:
        return {'error': 'Pillow not installed. Run: pip install Pillow'}
    except Exception as e:
        return {'error': str(e)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', required=True)
    parser.add_argument('--output', '-o', required=True)
    parser.add_argument('--format', '-f')
    parser.add_argument('--quality', '-q', type=int, default=90)
    parser.add_argument('--resize', '-r')
    parser.add_argument('--json', '-j', action='store_true')
    args = parser.parse_args()
    
    result = convert_image(args.input, args.output, args.format, args.quality, args.resize)
    
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        if 'error' in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        print(f"Converted to {result['output']}")

if __name__ == '__main__':
    main()
