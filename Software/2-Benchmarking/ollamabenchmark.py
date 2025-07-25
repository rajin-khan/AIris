#!/usr/bin/env python3
"""
Ollama Model Performance Testing Framework
Created by AIris Team
Runs specified models with a test question and generates performance report
"""

import subprocess
import json
import re
import time
from datetime import datetime
from typing import List, Dict, Optional
import os

class OllamaModelTester:
    def __init__(self):
        
        # Configure models here - add/remove models as needed
        self.models_to_test = [
            "llama3.2:1b",         # Meta's Smallest Model
            "gemma2:2b",           # Excellent performance/efficiency ratio
            "phi3.5:3.8b",         # Microsoft's optimized 3.8B model
            "tinydolphin:1.1b",    # Very fast, good for basic tasks
            "qwen2.5:1.5b",        # Alibaba's efficient model
            "qwen2.5:3b",          # Alibaba's 3b odel
            "gemma3:1b",           # Google's Gemma 3 1b
            "llama3.2:3b",         # Meta's latest compact model
            "gemma3n:e2b"          # Gemma 3's efficient 2b model
        ]
        
        # Configure your test question here
        self.test_question = "Why is the sky blue?"
        
        # Results storage
        self.results = []
        
    def check_ollama_available(self) -> bool:
        """Check if Ollama is installed and running"""
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def ensure_model_available(self, model_name: str) -> bool:
        """Pull model if not available locally"""
        print(f"Checking if {model_name} is available...")
        
        # Check if model exists locally
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            if model_name in result.stdout:
                print(f"[+] {model_name} is already available")
                return True
        except subprocess.TimeoutExpired:
            print(f"[-] Timeout checking model availability")
            return False
            
        # Pull the model
        print(f"Pulling {model_name}... (this may take a while)")
        try:
            result = subprocess.run(['ollama', 'pull', model_name], 
                                  capture_output=True, text=True, timeout=600)
            if result.returncode == 0:
                print(f"[+] Successfully pulled {model_name}")
                return True
            else:
                print(f"[-] Failed to pull {model_name}: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print(f"[-] Timeout pulling {model_name}")
            return False
    
    def run_model_test(self, model_name: str) -> Optional[Dict]:
        """Run a single model test and extract performance metrics"""
        print(f"\nTesting {model_name}...")
        
        if not self.ensure_model_available(model_name):
            return None
            
        try:
            # Run ollama with verbose output
            start_time = time.time()
            cmd = ['ollama', 'run', model_name, '--verbose']
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send the question and get response
            stdout, stderr = process.communicate(input=self.test_question, timeout=120)
            end_time = time.time()
            
            if process.returncode != 0:
                print(f"[-] Error running {model_name}: {stderr}")
                return None
                
            # Parse performance metrics from verbose output
            eval_rate = self.extract_eval_rate(stdout + stderr)
            response_time = end_time - start_time
            
            # Extract response content (everything before performance stats)
            response_content = self.extract_response_content(stdout)
            
            result = {
                'model': model_name,
                'eval_rate': eval_rate,
                'response_time': response_time,
                'response_length': len(response_content.split()),
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
            
            print(f"[+] {model_name}: {eval_rate:.2f} tokens/s ({response_time:.1f}s total)")
            return result
            
        except subprocess.TimeoutExpired:
            print(f"[-] {model_name} timed out")
            return {
                'model': model_name,
                'eval_rate': 0.0,
                'response_time': 120.0,
                'response_length': 0,
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': 'Timeout'
            }
        except Exception as e:
            print(f"[-] Error testing {model_name}: {str(e)}")
            return {
                'model': model_name,
                'eval_rate': 0.0,
                'response_time': 0.0,
                'response_length': 0,
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            }
    
    def extract_eval_rate(self, output: str) -> float:
        """Extract eval rate (tokens/s) from ollama verbose output"""
        # Look for patterns like "eval rate: 123.45 tokens/s"
        patterns = [
            r'eval rate:\s*([\d.]+)\s*tokens/s',
            r'evaluation rate:\s*([\d.]+)\s*tokens/s',
            r'([\d.]+)\s*tokens/s',
            r'eval.*?(\d+\.?\d*)\s*tok/s'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, IndexError):
                    continue
        
        # If no rate found, return 0
        return 0.0
    
    def extract_response_content(self, output: str) -> str:
        """Extract the actual response content from stdout"""
        # Split by common verbose output markers
        lines = output.split('\n')
        content_lines = []
        
        for line in lines:
            # Skip verbose/debug lines
            if any(marker in line.lower() for marker in 
                   ['total duration', 'load duration', 'prompt eval', 'eval count', 'eval duration']):
                break
            content_lines.append(line)
        
        return '\n'.join(content_lines).strip()
    
    def run_all_tests(self):
        """Run tests on all configured models"""
        print("Starting Ollama Model Performance Tests - AIris Team")
        print(f"Test Question: {self.test_question}")
        print(f"Models to test: {', '.join(self.models_to_test)}")
        
        if not self.check_ollama_available():
            print("ERROR: Ollama is not available. Please install and start Ollama first.")
            return
        
        print(f"\nTesting {len(self.models_to_test)} models...\n")
        
        for i, model in enumerate(self.models_to_test, 1):
            print(f"[{i}/{len(self.models_to_test)}] Testing {model}")
            result = self.run_model_test(model)
            if result:
                self.results.append(result)
        
        print(f"\nCompleted testing. {len(self.results)} results collected.")
    
    def generate_markdown_report(self, filename: str = "ollama_performance_report.md"):
        """Generate a markdown report with ranked results"""
        if not self.results:
            print("No results to report")
            return
        
        # Sort by eval rate (highest first)
        successful_results = [r for r in self.results if r['success']]
        failed_results = [r for r in self.results if not r['success']]
        successful_results.sort(key=lambda x: x['eval_rate'], reverse=True)
        
        # Generate report
        report = f"""# Ollama Model Performance Report
**AIris Team Benchmark Suite**

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Test Configuration
- **Test Question**: {self.test_question}
- **Models Tested**: {len(self.models_to_test)}
- **Successful Tests**: {len(successful_results)}
- **Failed Tests**: {len(failed_results)}

## Performance Rankings

### Top Performers (by Evaluation Rate)

| Rank | Model | Eval Rate (tokens/s) | Response Time (s) | Response Length (words) |
|------|-------|---------------------|-------------------|------------------------|
"""
        
        for i, result in enumerate(successful_results, 1):
            report += f"| {i} | `{result['model']}` | **{result['eval_rate']:.2f}** | {result['response_time']:.1f} | {result['response_length']} |\n"
        
        if successful_results:
            report += f"""
## Performance Summary

- **Fastest Model**: `{successful_results[0]['model']}` ({successful_results[0]['eval_rate']:.2f} tokens/s)
- **Average Rate**: {sum(r['eval_rate'] for r in successful_results) / len(successful_results):.2f} tokens/s
- **Median Rate**: {sorted([r['eval_rate'] for r in successful_results])[len(successful_results)//2]:.2f} tokens/s
"""

        if failed_results:
            report += f"""
## Failed Tests

| Model | Error | Timestamp |
|-------|-------|-----------|
"""
            for result in failed_results:
                error = result.get('error', 'Unknown error')
                report += f"| `{result['model']}` | {error} | {result['timestamp']} |\n"
        
        report += f"""
## Detailed Results

"""
        for result in self.results:
            status = "SUCCESS" if result['success'] else "FAILED"
            report += f"""### {result['model']} [{status}]

- **Eval Rate**: {result['eval_rate']:.2f} tokens/s
- **Response Time**: {result['response_time']:.1f} seconds
- **Response Length**: {result['response_length']} words
- **Timestamp**: {result['timestamp']}
"""
            if not result['success']:
                report += f"- **Error**: {result.get('error', 'Unknown error')}\n"
            report += "\n"
        
        report += """---
*Report generated by AIris Team Ollama Performance Testing Framework*
"""
        
        # Write report to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Report saved to: {filename}")
        return filename

def main():
    """Main execution function"""
    tester = OllamaModelTester()
    
    # Run all tests
    tester.run_all_tests()
    
    # Generate report
    if tester.results:
        report_file = tester.generate_markdown_report()
        print(f"\nTesting complete! Check {report_file} for detailed results.")
        
        # Print quick summary
        successful = [r for r in tester.results if r['success']]
        if successful:
            successful.sort(key=lambda x: x['eval_rate'], reverse=True)
            print(f"\nTop 3 performers:")
            for i, result in enumerate(successful[:3], 1):
                print(f"  {i}. {result['model']}: {result['eval_rate']:.2f} tokens/s")
    else:
        print("No successful tests completed.")

if __name__ == "__main__":
    main()