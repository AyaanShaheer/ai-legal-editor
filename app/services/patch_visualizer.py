from typing import Dict, Any, List
from colorama import init, Fore, Style

# Initialize colorama for Windows support
init(autoreset=True)


class PatchVisualizer:
    """Visualize patches with colored diff output"""
    
    @staticmethod
    def visualize_patch(patch_data: Dict[str, Any]) -> str:
        """
        Create colored visualization of patch
        
        Args:
            patch_data: Patch dictionary
            
        Returns:
            Formatted string with colors
        """
        lines = []
        lines.append("\n" + "="*60)
        lines.append("PATCH VISUALIZATION")
        lines.append("="*60)
        
        # Original
        lines.append(f"\n{Fore.YELLOW}Original:{Style.RESET_ALL}")
        lines.append(patch_data.get("original_text", ""))
        
        # Replacement
        lines.append(f"\n{Fore.GREEN}Replacement:{Style.RESET_ALL}")
        lines.append(patch_data.get("replacement_text", ""))
        
        # Operations
        lines.append(f"\n{Fore.CYAN}Operations:{Style.RESET_ALL}")
        
        for op in patch_data.get("operations", []):
            op_type = op["type"]
            text = repr(op["text"][:50])
            
            if op_type == "insert":
                lines.append(f"  {Fore.GREEN}+ INSERT:{Style.RESET_ALL} {text}")
            elif op_type == "delete":
                lines.append(f"  {Fore.RED}- DELETE:{Style.RESET_ALL} {text}")
            else:
                lines.append(f"  {Fore.WHITE}= EQUAL: {Style.RESET_ALL} {text}")
        
        lines.append("="*60 + "\n")
        
        return "\n".join(lines)
    
    @staticmethod
    def visualize_inline_diff(patch_data: Dict[str, Any]) -> str:
        """
        Create inline diff visualization
        
        Args:
            patch_data: Patch dictionary
            
        Returns:
            Inline diff string
        """
        result = []
        
        for op in patch_data.get("operations", []):
            op_type = op["type"]
            text = op["text"]
            
            if op_type == "insert":
                result.append(f"{Fore.GREEN}[+{text}]{Style.RESET_ALL}")
            elif op_type == "delete":
                result.append(f"{Fore.RED}[-{text}]{Style.RESET_ALL}")
            else:
                result.append(text)
        
        return "".join(result)
