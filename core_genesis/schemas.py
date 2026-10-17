"""Provider-constrained JSON grammars; semantic capabilities remain runtime-checked."""
from .team import FIELDS, REFERENCES, OWNERSHIP, TOOLS, ACTIONS


def strict(name, schema):
    return {"type": "json_schema", "json_schema": {"name": name, "strict": True, "schema": schema}}


def obj(properties, required=None):
    return {"type": "object", "properties": properties, "required": list(properties) if required is None else required, "additionalProperties": False}


def array(items, minimum=0, maximum=24):
    return {"type": "array", "items": items, "minItems": minimum, "maxItems": maximum}


def enum(values):
    return {"type": "string", "enum": list(values)}


def program_schema(nodes, allow_literals=True):
    target = enum(sorted(FIELDS))
    variants_of_rule = [
        obj({"target": target, "operation": enum(["copy", "increment", "decrement"]), "source": enum(sorted(REFERENCES))}),
    ]
    if allow_literals:
        variants_of_rule.extend([
            obj({"target": enum(sorted(FIELDS - {"health_path"})), "operation": enum(["literal"]), "value": {"type": "integer", "minimum": 0, "maximum": 100000}}),
            obj({"target": enum(["health_path"]), "operation": enum(["literal"]), "value": {"type": "string", "maxLength": 100}}),
        ])
    rule = {"anyOf": variants_of_rule}
    programs_by_node = {}
    for node in nodes:
        programs = obj({agent["id"]: array(rule, maximum=12) for agent in node["team"]["agents"]})
        programs_by_node[node["id"]] = programs
    return strict("repair_programs", obj({"programs": obj(programs_by_node)}))


def mutation_schema():
    text = {"type": "string", "maxLength": 600}
    agent = obj({"id": {"type": "string", "pattern": "^[A-Za-z][A-Za-z0-9_]{0,31}$"}, "specialty": enum(OWNERSHIP), "tools": array(enum(sorted(TOOLS)), maximum=4), "instructions": text})
    workflow = obj({"agent": {"type": "string"}, "action": enum(sorted(ACTIONS))})
    fields = {"instructions": text, "agents": array(agent, 1, 4), "workflow": array(workflow, 1, 24),
              "review_policy": enum(["schema", "contract", "protected_fields"]), "memory_policy": enum(["none", "inherit_verified"]), "cache_evidence": {"type": "boolean"}}
    change = obj(fields, required=[])
    mutation = obj({"name": text, "reason": text, "changes": change})
    return strict("team_mutations", obj({"observation": obj({"weakness": text, "lesson": text}), "mutations": array(mutation, 2, 2)}))


def design_schema(allow_memory_reuse=False):
    text = {"type": "string", "maxLength": 180}
    worker = obj({"specialty": enum(OWNERSHIP), "tools": array(enum(sorted(TOOLS)), maximum=4), "instructions": {"type": "string", "maxLength": 120}})
    workers = array(worker, 1, 4)
    design = obj({"instructions": text, "workers": workers,
                  "coordination": enum(["shared_evidence", "specialist_pipeline", "memory_first"]),
                  "review_policy": enum(["schema", "contract", "protected_fields"]),
                  "memory_policy": enum(["none", "inherit_verified"]), "cache_evidence": {"type": "boolean"},
                  "extra_review": {"type": "boolean"}, "procedure_source": enum(["compile", "reuse_memory"] if allow_memory_reuse else ["compile"])})
    mutation = obj({"name": {"type": "string", "maxLength": 80}, "reason": text, "design": design})
    return strict("team_designs", obj({"observation": obj({"weakness": text, "lesson": text}), "mutations": array(mutation, 2, 2)}))


def architect_schema():
    return strict("objective_and_team", obj({
        "approach": {"type": "string", "maxLength": 500},
        "success_criteria": array({"type": "string", "maxLength": 120}, 1, 3),
        "initial_specialties": array(enum(["general", "latency", "capacity", "routing"]), 1, 3),
    }))
