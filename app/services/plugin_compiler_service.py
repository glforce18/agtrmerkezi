"""
AGTR Merkezi - Plugin Compiler Service
Handles online AMXModX plugin compilation (.sma to .amxx)
"""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class PluginCompilerService:
    """Service for compiling AMXModX plugins"""

    def __init__(self):
        # AMXModX compiler path (amxxpc)
        self.compiler_path = Path("/usr/local/bin/amxxpc")  # Default path
        self.include_path = Path("/usr/local/share/amxmodx/include")  # Include files

        # Check if compiler exists
        if not self.compiler_path.exists():
            # Try alternative path
            self.compiler_path = Path("/opt/amxmodx/scripting/amxxpc")

        if not self.compiler_path.exists():
            logger.warning("AMXModX compiler (amxxpc) not found")

    def compile_plugin(self, source_code: str, plugin_name: str = "plugin") -> Dict[str, any]:
        """
        Compile a plugin from source code

        Args:
            source_code: .sma source code
            plugin_name: Plugin filename (without extension)

        Returns:
            Dict with success, compiled_data, errors
        """
        if not self.compiler_path.exists():
            return {
                "success": False,
                "error": "AMXModX compiler not installed on server",
                "compiled_data": None,
            }

        # Create temporary directory for compilation
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Write source file
            source_file = tmpdir_path / f"{plugin_name}.sma"
            try:
                with open(source_file, "w", encoding="utf-8") as f:
                    f.write(source_code)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to write source file: {e}",
                    "compiled_data": None,
                }

            # Run compiler
            try:
                # amxxpc plugin.sma -ooutput.amxx
                output_file = tmpdir_path / f"{plugin_name}.amxx"
                cmd = [
                    str(self.compiler_path),
                    str(source_file),
                    f"-o{output_file}",
                ]

                # Add include path if it exists
                if self.include_path.exists():
                    cmd.append(f"-i{self.include_path}")

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=tmpdir_path,
                )

                # Check for errors
                if result.returncode != 0:
                    return {
                        "success": False,
                        "error": result.stderr or result.stdout,
                        "warnings": [],
                        "compiled_data": None,
                    }

                # Read compiled .amxx file
                if output_file.exists():
                    with open(output_file, "rb") as f:
                        compiled_data = f.read()

                    # Parse warnings from output
                    warnings = []
                    for line in result.stdout.split("\n"):
                        if "warning" in line.lower():
                            warnings.append(line)

                    return {
                        "success": True,
                        "compiled_data": compiled_data,
                        "warnings": warnings,
                        "output": result.stdout,
                    }
                else:
                    return {
                        "success": False,
                        "error": "Compiler succeeded but .amxx file not found",
                        "output": result.stdout,
                        "compiled_data": None,
                    }

            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "error": "Compilation timeout (30s)",
                    "compiled_data": None,
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Compilation failed: {e}",
                    "compiled_data": None,
                }

    def validate_syntax(self, source_code: str) -> Dict[str, any]:
        """
        Validate plugin syntax without generating output

        Returns:
            Dict with valid (bool), errors, warnings
        """
        # Just try to compile to check syntax
        result = self.compile_plugin(source_code, "syntax_check")

        return {
            "valid": result["success"],
            "errors": result.get("error", ""),
            "warnings": result.get("warnings", []),
        }

    def get_compiler_version(self) -> Optional[str]:
        """Get AMXModX compiler version"""
        if not self.compiler_path.exists():
            return None

        try:
            result = subprocess.run(
                [str(self.compiler_path), "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip()
        except Exception:
            return None

    def is_compiler_available(self) -> bool:
        """Check if compiler is available"""
        return self.compiler_path.exists()
