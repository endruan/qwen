import docker
import json
import time
import tempfile
import os
from typing import Tuple
from app.core.config import get_settings

settings = get_settings()


class CodeExecutor:
    """Execute Python code in isolated Docker container."""
    
    def __init__(self):
        self.client = docker.from_env()
        self.timeout = settings.SANDBOX_TIMEOUT
        self.memory_limit = f"{settings.SANDBOX_MEMORY_LIMIT}m"
    
    def execute_code(
        self, 
        code: str, 
        input_data: str = ""
    ) -> Tuple[str, str, float, int]:
        """
        Execute Python code in isolated environment.
        
        Returns:
            Tuple of (output, error, execution_time, memory_used)
        """
        start_time = time.time()
        
        # Create temporary file with code
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.py', 
            delete=False
        ) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Run container with resource limits
            container = self.client.containers.run(
                "python:3.11-slim",
                command=f"python /code/script.py",
                volumes={temp_file: {'bind': '/code/script.py', 'mode': 'ro'}},
                mem_limit=self.memory_limit,
                nano_cpus=500000000,  # 0.5 CPU
                network_disabled=True,
                remove=True,
                detach=False,
                stderr=True,
                stdout=True,
                tty=False,
            )
            
            execution_time = time.time() - start_time
            
            # Decode output
            if isinstance(container, bytes):
                output = container.decode('utf-8')
                error = ""
            else:
                output = container
                error = ""
            
            # Simple memory estimation (not accurate without cgroups access)
            memory_used = settings.SANDBOX_MEMORY_LIMIT // 2
            
            return output, error, execution_time, memory_used
            
        except docker.errors.ContainerError as e:
            execution_time = time.time() - start_time
            return "", e.stderr.decode('utf-8') if isinstance(e.stderr, bytes) else str(e), execution_time, 0
        except Exception as e:
            return "", str(e), 0, 0
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def check_output(
        self, 
        actual_output: str, 
        expected_output: str
    ) -> bool:
        """Check if actual output matches expected output."""
        # Normalize whitespace
        actual_normalized = '\n'.join(actual_output.strip().split('\n'))
        expected_normalized = '\n'.join(expected_output.strip().split('\n'))
        
        return actual_normalized == expected_normalized
    
    def run_tests(
        self, 
        code: str, 
        test_cases: list
    ) -> Tuple[bool, list]:
        """
        Run multiple test cases against code.
        
        Returns:
            Tuple of (all_passed, results_list)
        """
        results = []
        all_passed = True
        
        for test_case in test_cases:
            input_data = test_case.get('input', '')
            expected_output = test_case.get('expected_output', '')
            
            output, error, exec_time, memory = self.execute_code(code, input_data)
            
            if error:
                passed = False
                results.append({
                    'passed': False,
                    'error': error,
                    'execution_time': exec_time,
                    'memory_used': memory
                })
                all_passed = False
            else:
                passed = self.check_output(output, expected_output)
                results.append({
                    'passed': passed,
                    'actual_output': output,
                    'expected_output': expected_output,
                    'execution_time': exec_time,
                    'memory_used': memory
                })
                
                if not passed:
                    all_passed = False
        
        return all_passed, results


# Singleton instance
_executor = None


def get_code_executor() -> CodeExecutor:
    """Get code executor instance."""
    global _executor
    if _executor is None:
        _executor = CodeExecutor()
    return _executor
