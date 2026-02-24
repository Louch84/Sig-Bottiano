---
name: code-interpreter
description: Execute Python and JavaScript code in a sandboxed environment with support for file I/O, package installation (pip/npm), result capture, timeouts, and resource limits. Use when the user needs to run code, analyze data, perform calculations, or generate outputs programmatically.
---

# Code Interpreter

Execute Python and JavaScript safely with controlled resource limits.

## Quick Start

Run Python code:
```bash
python3 scripts/run_python.py --code "print('Hello World')"
```

Run JavaScript code:
```bash
node scripts/run_js.js --code "console.log('Hello World')"
```

## Scripts

- `scripts/run_python.py` - Execute Python with timeout, file I/O, pip install support
- `scripts/run_js.js` - Execute JavaScript with timeout, npm install support
- `scripts/install_package.py` - Install pip/npm packages

## Safety Features

- **Timeout**: Default 30s (configurable with `--timeout`)
- **Memory**: Limited to 512MB
- **Network**: Allowed for package installation
- **File Access**: Restricted to temp workspace

## Usage Examples

### Python with packages
```bash
python3 scripts/run_python.py --code "
import requests
r = requests.get('https://api.github.com')
print(r.status_code)
" --packages requests
```

### JavaScript with npm packages
```bash
node scripts/run_js.js --code "
const axios = require('axios');
const res = await axios.get('https://api.github.com');
console.log(res.status);
" --packages axios
```

### Save output to file
```bash
python3 scripts/run_python.py --code "
import json
data = {'key': 'value'}
with open('output.json', 'w') as f:
    json.dump(data, f)
" --output output.json
```

## File I/O

All file operations happen in a temporary workspace. Use `--workdir` to specify a custom directory.
