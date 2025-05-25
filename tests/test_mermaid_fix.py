import asyncio
import sys
sys.path.append('.')
from mods.project_management.ai_task_creator import AITaskCreator

async def test_mermaid_fix():
    """Test if Mermaid diagrams are now being properly generated."""
    print("🧪 Testing Mermaid diagram generation fix...")
    
    creator = AITaskCreator()
    
    # Test with a simple installation task
    success, task_id, file_path = await creator.create_enhanced_task(
        title='Test Install Script Enhancement',
        description='Enhance the Windows installation script to include user configuration prompts and better error handling',
        task_type='Development',
        priority='medium',
        use_ai_enhancement=True
    )
    
    if success:
        print(f'✅ Task created: {task_id}')
        print(f'📄 File: {file_path}')
        
        # Check if the file contains Mermaid diagrams
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if '```mermaid' in content:
            print('✅ Mermaid diagram found in generated task!')
            # Extract and show the diagram
            start = content.find('```mermaid')
            end = content.find('```', start + 10)
            if start != -1 and end != -1:
                diagram = content[start:end+3]
                print('📊 Generated diagram:')
                print(diagram[:300] + '...' if len(diagram) > 300 else diagram)
        else:
            print('❌ No Mermaid diagram found in generated task')
            
        # Check for Flow Diagram section
        if '## 2. Flow Diagram' in content:
            print('✅ Flow Diagram section found')
        else:
            print('❌ Flow Diagram section missing')
            
        # Show first few lines of the task to verify structure
        lines = content.split('\n')
        print('\n📋 Task structure preview:')
        for i, line in enumerate(lines[:20]):
            if line.strip():
                print(f'{i+1:2d}: {line}')
                
    else:
        print(f'❌ Task creation failed: {file_path}')

if __name__ == "__main__":
    asyncio.run(test_mermaid_fix()) 