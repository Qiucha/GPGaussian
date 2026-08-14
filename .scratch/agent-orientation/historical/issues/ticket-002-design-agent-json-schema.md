# Ticket 002: Design Segmenter Agent JSON Execution Plan Schema

**Type**: `wayfinder:task`
**Status**: Closed (Resolved)
**Blocks**: [Implement LLM Segmenter Agent Pipeline](file:///home/q/Projects/mit/PBL/Phys4DGS/issues/ticket-004-implement-llm-segmenter-agent.md)

## Question

How should the LLM Segmenter Agent express its multi-heuristic segmentation decisions so that the pipeline can validate and execute them deterministically?

## Resolution

- Defined data models in `src/llm/schema.py`:
  1. `MaterialTagDefinition`: Dataclass capturing `tag_id`, `name`, `E` (Young's modulus), `nu` (Poisson's ratio), `density`, `material_type`, and `description`.
  2. `HeuristicStepConfig`: Dataclass capturing `primitive_type`, `params` dictionary, and rationale `description`.
  3. `SegmenterExecutionPlan`: Container capturing `scene_name`, `materials` list, and ordered `steps` list, supporting bidirection JSON conversion (`to_dict()`, `from_dict()`).
- Implemented `validate_segmenter_execution_plan(plan_dict)` enforcing:
  - Non-negative integer tag IDs.
  - Registered primitive types matching `HeuristicRegistry`.
  - Physical material constraints ($E > 0$, $0.0 \le \nu \le 0.49$, $\text{density} > 0$).
- Implemented automated tests in `tests/test_schema_and_cfl.py` (5/5 tests passing).
