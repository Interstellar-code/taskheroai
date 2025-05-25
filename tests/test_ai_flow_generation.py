import asyncio
import sys
sys.path.append('.')
from mods.project_management.ai_task_creator import AITaskCreator

async def test_ai_flow_generation():
    """Test AI flow diagram generation directly."""
    print("🔍 Testing AI Flow Diagram Generation...")
    
    creator = AITaskCreator()
    
    # Test the AI flow diagram generation function directly
    description = "Enhance the Windows installation script to include user configuration prompts and better error handling"
    context = {
        'task_type': 'Development',
        'title': 'Test Install Script Enhancement',
        'description': description
    }
    
    print("🚀 Testing _ai_generate_flow_diagrams...")
    try:
        flow_diagrams = await creator._ai_generate_flow_diagrams(description, context)
        
        print(f"✅ Flow diagrams generated: {len(flow_diagrams)} diagrams")
        
        for i, diagram in enumerate(flow_diagrams):
            print(f"\n📊 Diagram {i+1}:")
            print(f"   Type: {diagram.get('type', 'unknown')}")
            print(f"   Title: {diagram.get('title', 'Untitled')}")
            content = diagram.get('content', '')
            print(f"   Content preview: {content[:200]}...")
            
    except Exception as e:
        print(f"❌ Flow diagram generation failed: {e}")
    
    print("\n🚀 Testing _ai_generate_visual_elements...")
    try:
        visual_elements = await creator._ai_generate_visual_elements(description, context)
        
        print(f"✅ Visual elements generated")
        
        for key, value in visual_elements.items():
            print(f"\n🎨 {key}:")
            if key == 'mermaid_diagram' and isinstance(value, dict):
                print(f"   Type: {value.get('type', 'unknown')}")
                content = value.get('content', '')
                print(f"   Content preview: {content[:200]}...")
            else:
                print(f"   Value: {type(value)}")
                
    except Exception as e:
        print(f"❌ Visual elements generation failed: {e}")
    
    print("\n🚀 Testing template optimizer flow diagram relevance...")
    try:
        from mods.project_management.template_optimizer import TemplateOptimizer
        optimizer = TemplateOptimizer()
        
        # Test if installation tasks are considered relevant for flow diagrams
        is_relevant = optimizer._is_flow_diagram_relevant('DEV', description)
        print(f"✅ Flow diagram relevant for install task: {is_relevant}")
        
        # Test flow diagram generation
        flow_context = optimizer.generate_task_specific_flow_diagram('DEV', description, context)
        print(f"✅ Template optimizer flow context: {flow_context}")
        
    except Exception as e:
        print(f"❌ Template optimizer test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_ai_flow_generation()) 