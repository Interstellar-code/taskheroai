import asyncio
import sys
sys.path.append('.')
from mods.project_management.ai_task_creator import AITaskCreator

async def test_ai_enhancement_debug():
    """Debug test to see what's happening with AI enhancement and flow diagrams."""
    print("🔍 Debugging AI Enhancement and Flow Diagram Generation...")
    
    creator = AITaskCreator()
    
    # Test the progressive creation to see the AI enhancement step
    creator.creation_state = {
        'title': 'Debug Install Script Enhancement',
        'description': 'Enhance the Windows installation script to include user configuration prompts and better error handling',
        'task_type': 'Development',
        'priority': 'medium',
        'assigned_to': 'Developer',
        'effort_estimate': 'Medium',
        'tags': ['install', 'script', 'enhancement'],
        'dependencies': [],
        'selected_context': []
    }
    
    print("🚀 Step 3: AI Enhancement...")
    success = await creator._progressive_step_3_ai_enhancement()
    
    if success:
        print("✅ AI Enhancement completed")
        
        # Check what enhancements were generated
        enhancements = creator.creation_state.get('ai_enhancements', {})
        
        print(f"\n📊 Generated Enhancements:")
        for key, value in enhancements.items():
            if key == 'visual_elements':
                print(f"   🎨 {key}: {type(value)} - {len(value) if isinstance(value, dict) else 'N/A'} items")
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        print(f"      - {sub_key}: {type(sub_value)}")
                        if sub_key == 'mermaid_diagram' and isinstance(sub_value, dict):
                            content = sub_value.get('content', '')
                            print(f"        Content preview: {content[:100]}...")
            elif key == 'flow_diagrams':
                print(f"   📊 {key}: {type(value)} - {len(value) if isinstance(value, list) else 'N/A'} diagrams")
                if isinstance(value, list):
                    for i, diagram in enumerate(value):
                        if isinstance(diagram, dict):
                            print(f"      Diagram {i+1}: {diagram.get('title', 'Untitled')} ({diagram.get('type', 'unknown')})")
                            content = diagram.get('content', '')
                            print(f"        Content preview: {content[:100]}...")
            else:
                print(f"   📝 {key}: {type(value)}")
        
        # Now test the final creation step
        print(f"\n🚀 Step 4: Final Creation...")
        success, task_id, file_path = await creator._progressive_step_4_final_creation()
        
        if success:
            print(f"✅ Task created: {task_id}")
            print(f"📄 File: {file_path}")
            
            # Check the generated file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if '```mermaid' in content:
                print('✅ Mermaid diagram found in final task!')
                # Extract the diagram
                start = content.find('```mermaid')
                end = content.find('```', start + 10)
                if start != -1 and end != -1:
                    diagram = content[start:end+3]
                    print('📊 Final diagram:')
                    print(diagram)
            else:
                print('❌ No Mermaid diagram in final task')
                
        else:
            print(f"❌ Final creation failed: {file_path}")
    else:
        print("❌ AI Enhancement failed")

if __name__ == "__main__":
    asyncio.run(test_ai_enhancement_debug()) 