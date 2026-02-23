"""
MCP (Model Context Protocol) Client
Free implementation for connecting to any data source
Based on Anthropic's open standard
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import subprocess
import os

@dataclass
class MCPTool:
    """Represents a tool available via MCP"""
    name: str
    description: str
    parameters: Dict[str, Any]
    server: str

@dataclass
class MCPResource:
    """Represents a data resource available via MCP"""
    uri: str
    name: str
    mime_type: str
    server: str

class MCPClient:
    """
    Model Context Protocol Client
    Connects to MCP servers for tool/resource access
    
    Free implementation - no API costs
    """
    
    def __init__(self):
        self.servers: Dict[str, Dict] = {}
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.connected = False
    
    def add_server(self, name: str, command: str, args: List[str] = None, env: Dict = None):
        """
        Add an MCP server configuration
        
        Example:
            client.add_server(
                name="yahoo-finance",
                command="python",
                args=["mcp_servers/yahoo_server.py"]
            )
        """
        self.servers[name] = {
            'command': command,
            'args': args or [],
            'env': env or {},
            'process': None,
            'tools': [],
            'resources': []
        }
    
    async def connect(self, server_name: str) -> bool:
        """Connect to an MCP server and discover capabilities"""
        if server_name not in self.servers:
            print(f"❌ Server '{server_name}' not configured")
            return False
        
        server = self.servers[server_name]
        
        try:
            # Start MCP server process
            env = os.environ.copy()
            env.update(server['env'])
            
            process = await asyncio.create_subprocess_exec(
                server['command'],
                *server['args'],
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            server['process'] = process
            
            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "options-trading-agent",
                        "version": "1.0.0"
                    }
                }
            }
            
            await self._send_request(server_name, init_request)
            response = await self._read_response(server_name)
            
            if response and 'result' in response:
                print(f"✅ Connected to MCP server: {server_name}")
                
                # List available tools
                await self._discover_tools(server_name)
                await self._discover_resources(server_name)
                
                self.connected = True
                return True
            else:
                print(f"❌ Failed to initialize {server_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error connecting to {server_name}: {e}")
            return False
    
    async def _send_request(self, server_name: str, request: Dict):
        """Send JSON-RPC request to server"""
        server = self.servers[server_name]
        process = server['process']
        
        message = json.dumps(request) + '\n'
        process.stdin.write(message.encode())
        await process.stdin.drain()
    
    async def _read_response(self, server_name: str) -> Optional[Dict]:
        """Read JSON-RPC response from server"""
        server = self.servers[server_name]
        process = server['process']
        
        try:
            line = await asyncio.wait_for(
                process.stdout.readline(),
                timeout=10.0
            )
            return json.loads(line.decode().strip())
        except asyncio.TimeoutError:
            return None
        except json.JSONDecodeError:
            return None
    
    async def _discover_tools(self, server_name: str):
        """Discover available tools from server"""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        await self._send_request(server_name, request)
        response = await self._read_response(server_name)
        
        if response and 'result' in response:
            tools = response['result'].get('tools', [])
            for tool in tools:
                mcp_tool = MCPTool(
                    name=tool['name'],
                    description=tool.get('description', ''),
                    parameters=tool.get('inputSchema', {}),
                    server=server_name
                )
                self.tools[tool['name']] = mcp_tool
                self.servers[server_name]['tools'].append(tool['name'])
            
            print(f"   📋 Discovered {len(tools)} tools")
    
    async def _discover_resources(self, server_name: str):
        """Discover available resources from server"""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "resources/list"
        }
        
        await self._send_request(server_name, request)
        response = await self._read_response(server_name)
        
        if response and 'result' in response:
            resources = response['result'].get('resources', [])
            for resource in resources:
                mcp_resource = MCPResource(
                    uri=resource['uri'],
                    name=resource.get('name', ''),
                    mime_type=resource.get('mimeType', 'text/plain'),
                    server=server_name
                )
                self.resources[resource['uri']] = mcp_resource
                self.servers[server_name]['resources'].append(resource['uri'])
            
            print(f"   📁 Discovered {len(resources)} resources")
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> Any:
        """Call an MCP tool"""
        if tool_name not in self.tools:
            return {'error': f'Tool {tool_name} not found'}
        
        tool = self.tools[tool_name]
        server_name = tool.server
        
        request = {
            "jsonrpc": "2.0",
            "id": int(datetime.now().timestamp()),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        await self._send_request(server_name, request)
        response = await self._read_response(server_name)
        
        if response and 'result' in response:
            return response['result']
        elif response and 'error' in response:
            return {'error': response['error']}
        else:
            return {'error': 'No response from server'}
    
    async def read_resource(self, uri: str) -> Any:
        """Read an MCP resource"""
        if uri not in self.resources:
            return {'error': f'Resource {uri} not found'}
        
        resource = self.resources[uri]
        server_name = resource.server
        
        request = {
            "jsonrpc": "2.0",
            "id": int(datetime.now().timestamp()),
            "method": "resources/read",
            "params": {
                "uri": uri
            }
        }
        
        await self._send_request(server_name, request)
        response = await self._read_response(server_name)
        
        if response and 'result' in response:
            return response['result']
        else:
            return {'error': 'Failed to read resource'}
    
    def list_tools(self) -> List[str]:
        """List all available tools"""
        return list(self.tools.keys())
    
    def list_resources(self) -> List[str]:
        """List all available resources"""
        return list(self.resources.keys())
    
    async def disconnect(self, server_name: str = None):
        """Disconnect from server(s)"""
        if server_name:
            servers = [server_name] if server_name in self.servers else []
        else:
            servers = list(self.servers.keys())
        
        for name in servers:
            server = self.servers[name]
            if server['process']:
                server['process'].terminate()
                await server['process'].wait()
                server['process'] = None
                print(f"🔌 Disconnected from {name}")


class MCPTradingConnectors:
    """
    Pre-built MCP connectors for trading
    All free implementations
    """
    
    @staticmethod
    def yahoo_finance_connector() -> Dict:
        """Yahoo Finance MCP server config (free)"""
        return {
            'name': 'yahoo-finance',
            'command': 'python',
            'args': ['-c', '''
import sys
import json
import yfinance as yf

while True:
    line = sys.stdin.readline()
    if not line:
        break
    
    request = json.loads(line)
    method = request.get('method', '')
    req_id = request.get('id', 0)
    
    if method == 'initialize':
        response = {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": {"name": "yahoo-finance", "version": "1.0"}
            }
        }
    
    elif method == 'tools/list':
        response = {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "get_quote",
                        "description": "Get stock quote",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "symbol": {"type": "string"}
                            }
                        }
                    },
                    {
                        "name": "get_options",
                        "description": "Get options chain",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "symbol": {"type": "string"}
                            }
                        }
                    }
                ]
            }
        }
    
    elif method == 'tools/call':
        params = request.get('params', {})
        tool_name = params.get('name', '')
        args = params.get('arguments', {})
        
        if tool_name == 'get_quote':
            ticker = yf.Ticker(args['symbol'])
            info = ticker.info
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps({
                        "symbol": args['symbol'],
                        "price": info.get('currentPrice', 0),
                        "change": info.get('regularMarketChange', 0)
                    })}]
                }
            }
        else:
            response = {"jsonrpc": "2.0", "id": req_id, "result": {"content": []}}
    
    else:
        response = {"jsonrpc": "2.0", "id": req_id, "result": {}}
    
    print(json.dumps(response), flush=True)
''']
        }
    
    @staticmethod
    def file_system_connector(root_path: str = "/Users/sigbotti/.openclaw/workspace") -> Dict:
        """File system MCP server config (free, built-in)"""
        return {
            'name': 'filesystem',
            'command': 'python',
            'args': ['-c', f'''
import sys
import json
import os
from pathlib import Path

ROOT = "{root_path}"

while True:
    line = sys.stdin.readline()
    if not line:
        break
    
    request = json.loads(line)
    method = request.get('method', '')
    req_id = request.get('id', 0)
    
    if method == 'initialize':
        response = {{
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {{
                "protocolVersion": "2024-11-05",
                "capabilities": {{"resources": {{}}}},
                "serverInfo": {{"name": "filesystem", "version": "1.0"}}
            }}
        }}
    
    elif method == 'resources/list':
        files = []
        for f in Path(ROOT).rglob("*.py"):
            rel_path = f.relative_to(ROOT)
            files.append({{
                "uri": f"file://{{rel_path}}",
                "name": str(rel_path),
                "mimeType": "text/x-python"
            }})
        
        response = {{
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {{"resources": files[:50]}}  # Limit to 50
        }}
    
    elif method == 'resources/read':
        uri = request.get('params', {{}}).get('uri', '')
        file_path = uri.replace('file://', '')
        full_path = Path(ROOT) / file_path
        
        try:
            content = full_path.read_text()
            response = {{
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {{
                    "contents": [{{
                        "uri": uri,
                        "mimeType": "text/x-python",
                        "text": content[:10000]  # Limit size
                    }}]
                }}
            }}
        except Exception as e:
            response = {{
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {{"message": str(e)}}
            }}
    
    else:
        response = {{"jsonrpc": "2.0", "id": req_id, "result": {{}}}}
    
    print(json.dumps(response), flush=True)
''']
        }


# Usage example
async def demo():
    """Demonstrate MCP client"""
    client = MCPClient()
    
    # Add Yahoo Finance connector
    config = MCPTradingConnectors.yahoo_finance_connector()
    client.add_server(**config)
    
    # Connect
    success = await client.connect('yahoo-finance')
    
    if success:
        print("\nAvailable tools:", client.list_tools())
        
        # Call tool
        result = await client.call_tool('get_quote', {'symbol': 'AAPL'})
        print("\nAAPL Quote:", result)
        
        # Disconnect
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(demo())
