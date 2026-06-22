"""
Local Code Execution Route
Executes Python and C/C++ code locally using subprocess.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
import os
import tempfile
import asyncio

router = APIRouter(prefix="/execute", tags=["Execution"])

class ExecuteRequest(BaseModel):
    language: str
    code: str
    stdin: str = ""

import subprocess

@router.post("/")
async def execute_code(body: ExecuteRequest):
    lang = body.language.lower()
    
    if lang not in ["c", "cpp", "python", "py"]:
        return {"message": f"Language {lang} is not supported locally. Try 'c' or 'python'."}
        
    def run_sync():
        with tempfile.TemporaryDirectory() as temp_dir:
            if lang in ["python", "py"]:
                file_path = os.path.join(temp_dir, "script.py")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(body.code)
                
                try:
                    proc = subprocess.run(
                        [sys.executable, file_path],
                        input=body.stdin.encode(),
                        capture_output=True,
                        timeout=5.0
                    )
                    return {
                        "compile": {"code": 0, "output": ""},
                        "run": {
                            "code": proc.returncode,
                            "stdout": proc.stdout.decode(errors="ignore"),
                            "stderr": proc.stderr.decode(errors="ignore")
                        }
                    }
                except subprocess.TimeoutExpired:
                    return {"message": "Execution timed out"}
                except Exception as e:
                    return {"message": f"Execution failed: {repr(e)}"}

            elif lang in ["c", "cpp"]:
                ext = ".c" if lang == "c" else ".cpp"
                compiler = "gcc" if lang == "c" else "g++"
                file_path = os.path.join(temp_dir, f"main{ext}")
                out_path = os.path.join(temp_dir, "main.exe")
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(body.code)
                
                # Compile
                try:
                    compile_proc = subprocess.run(
                        [compiler, file_path, "-o", out_path],
                        capture_output=True,
                        timeout=5.0
                    )
                    if compile_proc.returncode != 0:
                        return {
                            "compile": {
                                "code": compile_proc.returncode,
                                "output": compile_proc.stderr.decode(errors="ignore")
                            }
                        }
                except subprocess.TimeoutExpired:
                    return {"message": "Compilation timed out"}
                except FileNotFoundError:
                    return {"message": f"Compiler '{compiler}' not found. Please ensure MinGW/GCC is in PATH."}
                except Exception as e:
                    return {"message": f"Compiler error: {repr(e)}"}
                    
                # Run
                try:
                    run_proc = subprocess.run(
                        [out_path],
                        input=body.stdin.encode(),
                        capture_output=True,
                        timeout=5.0
                    )
                    return {
                        "compile": {"code": 0, "output": ""},
                        "run": {
                            "code": run_proc.returncode,
                            "stdout": run_proc.stdout.decode(errors="ignore"),
                            "stderr": run_proc.stderr.decode(errors="ignore")
                        }
                    }
                except subprocess.TimeoutExpired:
                    return {"message": "Execution timed out"}
                except Exception as e:
                    return {"message": f"Runtime error: {repr(e)}"}

    return await asyncio.to_thread(run_sync)
