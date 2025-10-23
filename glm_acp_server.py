#!/usr/bin/env python3
"""
Agent Client Protocol (ACP) Server for GLM 4.6 model from z.ai
This server acts as a bridge between ACP clients (like Toad) and the GLM 4.6 API
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional
import httpx
from pathlib import Path

# Load environment variables from .env file if it exists
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# Get API key from environment variable
GLM_API_KEY = os.environ.get("GLM_API_KEY")
if not GLM_API_KEY:
    print("Error: GLM_API_KEY environment variable not set", file=sys.stderr)
    sys.exit(1)

# GLM API configuration
GLM_API_BASE = "https://open.bigmodel.cn/api/paas/v4/"
GLM_MODEL = "glm-4.6"

class ACPServer:
    """ACP Server implementation for GLM 4.6"""
    
    def __init__(self):
        self.conversation_history = []
        self.session_id = "glm-session-001"
        self.project_root = Path("./").resolve()
    
    async def call_glm_api(self, messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """Make a call to the GLM API"""
        headers = {
            "Authorization": f"Bearer {GLM_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": GLM_MODEL,
            "messages": messages,
            **kwargs
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GLM_API_BASE}chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()
    
    async def handle_request(self, request_data):
        """Handle ACP request"""
        try:
            method = request_data.get("method")
            params = request_data.get("params", {})
            request_id = request_data.get("id")
            
            if method == "initialize":
                return await self.handle_initialize(params, request_id)
            elif method == "session/new":
                return await self.handle_session_new(params, request_id)
            elif method == "session/prompt":
                return await self.handle_session_prompt(params, request_id)
            elif method == "session/cancel":
                return await self.handle_session_cancel(params, request_id)
            elif method == "session/set_mode":
                return await self.handle_session_set_mode(params, request_id)
            elif method == "fs/read_text_file":
                return await self.handle_read_text_file(params, request_id)
            elif method == "fs/write_text_file":
                return await self.handle_write_text_file(params, request_id)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def handle_initialize(self, params, request_id):
        """Handle initialize request"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "agentCapabilities": {
                    "loadSession": False,
                    "promptCapabilities": {
                        "audio": False,
                        "embeddedContent": False,
                        "image": False,
                    }
                },
                "authMethods": []
            }
        }
    
    async def handle_session_new(self, params, request_id):
        """Handle session/new request"""
        project_path = params.get("projectPath", str(self.project_root))
        self.project_root = Path(project_path).resolve()
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "sessionId": self.session_id,
                "modes": {
                    "currentModeId": "chat",
                    "availableModes": [
                        {
                            "id": "chat",
                            "name": "Chat",
                            "description": "General conversation mode"
                        }
                    ]
                }
            }
        }
    
    async def handle_session_prompt(self, params, request_id):
        """Handle session/prompt request"""
        prompt_content = params.get("content", [])
        session_id = params.get("sessionId", self.session_id)
        
        # Extract text from prompt content
        user_message = ""
        for content_block in prompt_content:
            if content_block.get("type") == "text":
                user_message += content_block.get("text", "")
        
        if not user_message:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32602,
                    "message": "No message content provided"
                }
            }
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        try:
            # Call GLM API
            response = await self.call_glm_api(
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=1024
            )
            
            assistant_message = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            # Send the response in chunks (simulating streaming)
            await self.send_streaming_response(assistant_message, request_id)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "stopReason": "completed"
                }
            }
            
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"GLM API error: {str(e)}"
                }
            }
    
    async def send_streaming_response(self, message, request_id):
        """Send streaming response to client"""
        # Split message into chunks for streaming effect
        chunks = [message[i:i+50] for i in range(0, len(message), 50)]
        
        for chunk in chunks:
            notification = {
                "jsonrpc": "2.0",
                "method": "session/update",
                "params": {
                    "sessionId": self.session_id,
                    "sessionUpdate": "agent_message_chunk",
                    "content": {
                        "type": "text",
                        "text": chunk
                    }
                }
            }
            print(json.dumps(notification), flush=True)
            await asyncio.sleep(0.1)  # Simulate streaming delay
    
    async def handle_session_cancel(self, params, request_id):
        """Handle session/cancel request"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {}
        }
    
    async def handle_session_set_mode(self, params, request_id):
        """Handle session/set_mode request"""
        mode_id = params.get("modeId", "chat")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {}
        }
    
    async def handle_read_text_file(self, params, request_id):
        """Handle fs/read_text_file request"""
        file_path = params.get("path", "")
        line = params.get("line")
        limit = params.get("limit")
        
        try:
            full_path = self.project_root / file_path
            if not full_path.exists():
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": f"File not found: {file_path}"
                    }
                }
            
            content = full_path.read_text(encoding="utf-8", errors="ignore")
            
            if line is not None:
                line = max(0, line - 1)
                lines = content.splitlines()
                if limit is None:
                    content = "\n".join(lines[line:])
                else:
                    content = "\n".join(lines[line:line + limit])
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": content
                }
            }
            
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Error reading file: {str(e)}"
                }
            }
    
    async def handle_write_text_file(self, params, request_id):
        """Handle fs/write_text_file request"""
        file_path = params.get("path", "")
        content = params.get("content", "")
        
        try:
            full_path = self.project_root / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8", errors="ignore")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {}
            }
            
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Error writing file: {str(e)}"
                }
            }

async def _async_main():
    """Async main entry point"""
    server = ACPServer()
    
    try:
        while True:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
            
            try:
                request_data = json.loads(line)
                response = await server.handle_request(request_data)
                if response:
                    print(json.dumps(response), flush=True)
            except json.JSONDecodeError:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request_data.get("id") if 'request_data' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
                
    except KeyboardInterrupt:
        pass

def main():
    """Synchronous entry point for package scripts"""
    asyncio.run(_async_main())

if __name__ == "__main__":
    main()