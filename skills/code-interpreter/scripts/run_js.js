#!/usr/bin/env node
/**
 * Execute JavaScript code in a sandboxed environment.
 * Supports: npm packages, async/await, timeout
 */
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

function parseArgs() {
    const args = process.argv.slice(2);
    const options = { timeout: 30000 };
    
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--code':
            case '-c':
                options.code = args[++i];
                break;
            case '--packages':
            case '-p':
                options.packages = args[++i];
                break;
            case '--timeout':
            case '-t':
                options.timeout = parseInt(args[++i]);
                break;
            case '--workdir':
            case '-w':
                options.workdir = args[++i];
                break;
            case '--json':
            case '-j':
                options.json = true;
                break;
        }
    }
    return options;
}

function installPackages(packages, workdir) {
    if (!packages) return;
    const pkgList = packages.split(',').map(p => p.trim());
    const pkgJson = { name: 'temp-script', version: '1.0.0', dependencies: {} };
    pkgList.forEach(p => pkgJson.dependencies[p] = '*');
    fs.writeFileSync(path.join(workdir, 'package.json'), JSON.stringify(pkgJson, null, 2));
    execSync('npm install --silent', { cwd: workdir, stdio: 'ignore' });
}

async function runCode(code, timeout, workdir) {
    workdir = workdir || fs.mkdtempSync(path.join(os.tmpdir(), 'js_exec_'));
    
    const scriptPath = path.join(workdir, 'script.js');
    const wrappedCode = `
const console_log = console.log;
const console_error = console.error;
let output = [];
let errors = [];
console.log = (...args) => { output.push(args.join(' ')); console_log(...args); };
console.error = (...args) => { errors.push(args.join(' ')); console_error(...args); };

(async () => {
    try {
        ${code}
    } catch (e) {
        console.error(e.message);
        process.exitCode = 1;
    }
})();
`;
    fs.writeFileSync(scriptPath, wrappedCode);
    
    return new Promise((resolve) => {
        const { spawn } = require('child_process');
        const child = spawn('node', [scriptPath], { cwd: workdir, env: process.env });
        
        let stdout = '';
        let stderr = '';
        
        child.stdout.on('data', (data) => { stdout += data; });
        child.stderr.on('data', (data) => { stderr += data; });
        
        const timer = setTimeout(() => {
            child.kill();
            resolve({ error: `Code execution timed out after ${timeout}ms`, workdir });
        }, timeout);
        
        child.on('close', (code) => {
            clearTimeout(timer);
            resolve({ stdout, stderr, returncode: code, workdir });
        });
    });
}

async function main() {
    const args = parseArgs();
    
    if (!args.code) {
        console.error('Error: --code is required');
        process.exit(1);
    }
    
    if (args.packages) {
        const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'js_exec_'));
        installPackages(args.packages, tempDir);
        args.workdir = tempDir;
    }
    
    const result = await runCode(args.code, args.timeout, args.workdir);
    
    if (args.json) {
        console.log(JSON.stringify(result, null, 2));
    } else {
        if (result.stdout) console.log(result.stdout);
        if (result.stderr) console.error(result.stderr);
        if (result.error) {
            console.error(`Error: ${result.error}`);
            process.exit(1);
        }
    }
    
    process.exit(result.returncode || 0);
}

main().catch(e => {
    console.error(e.message);
    process.exit(1);
});
