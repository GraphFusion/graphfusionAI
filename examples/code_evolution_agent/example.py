from code_evolution_agent import CodeEvolutionAgent
from graphfusionai import Role
import asyncio

# Sample code to evolve
SAMPLE_CODE = '''
def process_data(data_list):
    result = []
    for item in data_list:
        if item > 0:
            result.append(item * 2)
    
    # Redundant database calls
    db = Database()
    user = db.get_user(user_id)
    profile = db.get_user(user_id)  # Redundant call
    
    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"
    results = db.execute(query)
    
    # Long function with duplicate code
    processed = []
    for result in results:
        if result.status == 'active':
            if result.type == 'user':
                data = process_user_data(result.data)
                processed.append(data)
            elif result.type == 'admin':
                data = process_admin_data(result.data)
                processed.append(data)
    
    return processed

def process_user_data(data):
    # Complex data processing
    step1 = data.get('field1', '')
    step2 = step1.upper()
    step3 = step2.replace(' ', '_')
    return step3

def process_admin_data(data):
    # Duplicate code from process_user_data
    step1 = data.get('field1', '')
    step2 = step1.upper()
    step3 = step2.replace(' ', '_')
    return step3
'''

async def main():
    # Create the Code Evolution Agent
    role = Role(
        name="code_optimizer",
        capabilities=[
            "optimize_performance",
            "enhance_security",
            "improve_maintainability"
        ],
        description="Evolves and optimizes Python code"
    )
    
    agent = CodeEvolutionAgent(
        name="CodeOptimizer",
        role=role,
        knowledge_base_path="knowledge_base.db"
    )
    
    # Evolve the code with all optimization goals
    result = await agent.evolve_codebase(
        code=SAMPLE_CODE,
        optimization_goals=["performance", "security", "maintainability"]
    )
    
    # Print the improvements
    print("Code Evolution Results:")
    print("\nOptimized Code:")
    print(result["evolved_code"])
    
    print("\nImprovements:")
    for metric, improvement in result["improvements"].items():
        print(f"{metric}: {improvement:.2f}%")
    
    print("\nFinal Metrics:")
    for metric, value in result["metrics"].items():
        print(f"{metric}: {value:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
