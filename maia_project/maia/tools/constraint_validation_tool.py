"""Constraint validation tool for MAIA agents."""

from crewai.tools import BaseTool
from typing import Type, Dict, Any, List
from pydantic import BaseModel, Field
import z3


class Z3SolverInput(BaseModel):
    """Input schema for Z3SolverTool."""
    query: str = Field(..., description="SMT-LIB 2 format query string to be processed by Z3 solver.")

class Z3SolverTool(BaseTool):
    name: str = "z3_solver"
    description: str = (
        "Uses a constraint input string in SMT-LIB format to call the Z3 solver, "
        "which can be used to verify constraint satisfaction, check satisfiability, and return models. "
        "Input should be a string in SMT-LIB 2 (.smt2) style."
    )
    args_schema: Type[BaseModel] = Z3SolverInput
    
    def _run(self, query: str) -> Any:
        try:
            # Create a solver instance
            solver = z3.Solver()
            
            # Parse SMT-LIB input and add to solver
            parsed_formulas = z3.parse_smt2_string(query)
            for formula in parsed_formulas:
                solver.add(formula)

            # Check satisfiability
            result = solver.check()
            if result == z3.sat:
                model = solver.model()
                return f"SAT\nModel:\n{model}"
            elif result == z3.unsat:
                return "UNSAT: No solution exists."
            else:
                return "UNKNOWN: Z3 cannot determine satisfiability."
        except Exception as e:
            return f"Error during Z3 solving: {str(e)}"
