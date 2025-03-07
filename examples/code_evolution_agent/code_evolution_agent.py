from graphfusionai import Agent, Role, KnowledgeGraph, Memory
from typing import Dict, Any, List, Optional
import ast
import astor
import radon.metrics as metrics
from datetime import datetime
import difflib
import logging
import asyncio

class CodeEvolutionAgent(Agent):
    """An intelligent agent that evolves and optimizes code through continuous learning."""
    
    def __init__(
        self,
        name: str,
        role: Role,
        knowledge_base_path: str
    ):
        super().__init__(name=name, role=role)
        self.kg = KnowledgeGraph()
        self.memory = Memory()
        self.patterns_db = self._initialize_patterns()
        self.metrics_history = []
        
    def _initialize_patterns(self) -> Dict[str, Any]:
        """Initialize known code patterns and their optimizations."""
        return {
            "performance_patterns": {
                "list_comprehension": {
                    "detect": lambda node: isinstance(node, ast.For) and isinstance(node.parent, ast.List),
                    "optimize": self._convert_to_list_comprehension
                },
                "redundant_calls": {
                    "detect": self._detect_redundant_calls,
                    "optimize": self._optimize_redundant_calls
                }
            },
            "security_patterns": {
                "sql_injection": {
                    "detect": self._detect_sql_injection,
                    "optimize": self._secure_sql_query
                },
                "unsafe_deserialization": {
                    "detect": self._detect_unsafe_deserialization,
                    "optimize": self._secure_deserialization
                }
            },
            "maintainability_patterns": {
                "long_function": {
                    "detect": lambda node: isinstance(node, ast.FunctionDef) and len(node.body) > 20,
                    "optimize": self._split_long_function
                },
                "duplicate_code": {
                    "detect": self._detect_duplicate_code,
                    "optimize": self._extract_common_function
                }
            }
        }

    async def evolve_codebase(
        self,
        code: str,
        optimization_goals: List[str]
    ) -> Dict[str, Any]:
        """
        Evolve code based on specified optimization goals.
        
        Args:
            code: Source code to evolve
            optimization_goals: List of goals ("performance", "security", "maintainability")
            
        Returns:
            Dict containing evolved code and improvement metrics
        """
        try:
            # Parse and analyze code
            tree = ast.parse(code)
            initial_metrics = self._calculate_metrics(code)
            
            # Store initial state in knowledge graph
            await self._store_code_state(tree, initial_metrics)
            
            # Apply optimizations based on goals
            evolved_tree = await self._apply_optimizations(tree, optimization_goals)
            evolved_code = astor.to_source(evolved_tree)
            
            # Calculate improvement metrics
            final_metrics = self._calculate_metrics(evolved_code)
            improvements = self._calculate_improvements(initial_metrics, final_metrics)
            
            # Store evolution results
            await self._store_evolution_results(
                original_code=code,
                evolved_code=evolved_code,
                improvements=improvements
            )
            
            return {
                "evolved_code": evolved_code,
                "improvements": improvements,
                "metrics": final_metrics
            }
            
        except Exception as e:
            logging.error(f"Error during code evolution: {str(e)}")
            raise

    async def _apply_optimizations(
        self,
        tree: ast.AST,
        goals: List[str]
    ) -> ast.AST:
        """Apply optimizations based on specified goals."""
        for goal in goals:
            patterns = self.patterns_db.get(f"{goal}_patterns", {})
            for pattern_name, pattern in patterns.items():
                tree = self._apply_pattern(tree, pattern)
        return tree

    def _apply_pattern(
        self,
        tree: ast.AST,
        pattern: Dict[str, Any]
    ) -> ast.AST:
        """Apply a specific optimization pattern to the AST."""
        class Transformer(ast.NodeTransformer):
            def visit(self, node):
                if pattern["detect"](node):
                    return pattern["optimize"](node)
                return self.generic_visit(node)
                
        return Transformer().visit(tree)

    def _calculate_metrics(self, code: str) -> Dict[str, float]:
        """Calculate code quality metrics."""
        return {
            "complexity": metrics.cyclomatic_complexity(code),
            "maintainability": metrics.mi_visit(code),
            "loc": len(code.splitlines()),
            "halstead_metrics": metrics.h_visit(code)
        }

    def _calculate_improvements(
        self,
        initial: Dict[str, float],
        final: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate improvement percentages."""
        return {
            metric: ((final[metric] - initial[metric]) / initial[metric]) * 100
            for metric in initial.keys()
        }

    async def _store_code_state(
        self,
        tree: ast.AST,
        metrics: Dict[str, float]
    ):
        """Store code state in knowledge graph."""
        state_node = {
            "timestamp": datetime.now(),
            "metrics": metrics,
            "ast_summary": self._summarize_ast(tree)
        }
        self.kg.add_node(state_node)

    async def _store_evolution_results(
        self,
        original_code: str,
        evolved_code: str,
        improvements: Dict[str, float]
    ):
        """Store evolution results for learning."""
        result = {
            "timestamp": datetime.now(),
            "improvements": improvements,
            "diff": self._generate_diff(original_code, evolved_code)
        }
        
        # Store in memory for short-term reference
        await self.memory.store(
            f"evolution_{datetime.now().isoformat()}",
            result
        )
        
        # Store in knowledge graph for long-term learning
        self.kg.add_node(result)

    def _generate_diff(
        self,
        original: str,
        evolved: str
    ) -> str:
        """Generate a readable diff between original and evolved code."""
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            evolved.splitlines(keepends=True)
        )
        return ''.join(diff)

    def _summarize_ast(self, tree: ast.AST) -> Dict[str, Any]:
        """Create a summary of the AST for storage."""
        summary = {
            "node_types": {},
            "function_count": 0,
            "class_count": 0,
            "max_depth": 0
        }
        
        for node in ast.walk(tree):
            node_type = type(node).__name__
            summary["node_types"][node_type] = summary["node_types"].get(node_type, 0) + 1
            
            if isinstance(node, ast.FunctionDef):
                summary["function_count"] += 1
            elif isinstance(node, ast.ClassDef):
                summary["class_count"] += 1
                
        return summary

    # Pattern Detection Methods
    def _detect_redundant_calls(self, node: ast.AST) -> bool:
        """Detect redundant function calls."""
        # Implementation
        pass

    def _detect_sql_injection(self, node: ast.AST) -> bool:
        """Detect potential SQL injection vulnerabilities."""
        # Implementation
        pass

    def _detect_unsafe_deserialization(self, node: ast.AST) -> bool:
        """Detect unsafe deserialization patterns."""
        # Implementation
        pass

    def _detect_duplicate_code(self, node: ast.AST) -> bool:
        """Detect duplicate code blocks."""
        # Implementation
        pass

    # Optimization Methods
    def _convert_to_list_comprehension(self, node: ast.For) -> ast.ListComp:
        """Convert for loop to list comprehension."""
        # Implementation
        pass

    def _optimize_redundant_calls(self, node: ast.AST) -> ast.AST:
        """Optimize redundant function calls."""
        # Implementation
        pass

    def _secure_sql_query(self, node: ast.AST) -> ast.AST:
        """Secure SQL queries against injection."""
        # Implementation
        pass

    def _secure_deserialization(self, node: ast.AST) -> ast.AST:
        """Implement secure deserialization."""
        # Implementation
        pass

    def _split_long_function(self, node: ast.FunctionDef) -> List[ast.FunctionDef]:
        """Split long functions into smaller, more manageable ones."""
        # Implementation
        pass

    def _extract_common_function(self, nodes: List[ast.AST]) -> ast.FunctionDef:
        """Extract duplicate code into a separate function."""
        # Implementation
        pass
