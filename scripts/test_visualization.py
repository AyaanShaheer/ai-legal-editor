import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.patch_engine import PatchEngine
from app.services.patch_visualizer import PatchVisualizer


def test_visualization():
    """Test patch visualization"""
    
    engine = PatchEngine()
    visualizer = PatchVisualizer()
    
    original = "The Employee shall serve as Senior Software Engineer and report to the Manager."
    replacement = "The Employee shall serve as Principal Software Architect and report to the Chief Technology Officer."
    
    patch = engine.generate_patch(original, replacement)
    
    # Standard visualization
    print(visualizer.visualize_patch(patch))
    
    # Inline diff
    print("\nINLINE DIFF:")
    print(visualizer.visualize_inline_diff(patch))


if __name__ == "__main__":
    test_visualization()
