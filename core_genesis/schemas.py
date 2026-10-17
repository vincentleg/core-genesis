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


def program_schema(nodes):
    target = enum(sorted(FIELDS))
    rule = {"anyOf": [
        obj({"target": target, "operation": enum(["copy", "increment", "decrement"]), "source": enum(sorted(REFERENCES))}),
        obj({"target": target, "operation": enum(["literal"]), "value": {"anyOf": [{"type": "integer", "minimum": 0, "maximum": 100000}, {"type": "string", "maxLength": 100}]}}),
    ]}
    variants = []
    for node in nodes:
        programs = obj({agent["id"]: array(rule, maximum=12) for agent in node["team"]["agents"]})
        variants.append(obj({"node_id": enum([node["id"]]), "program": programs}))
    return strict("repair_programs", obj({"programs": array({"anyOf": variants}, len(nodes), len(nodes))}))


def mutation_schema():
    text = {"type": "string", "maxLength": 600}
    agent = obj({"id": {"type": "string", "pattern": "^[A-Za-z][A-Za-z0-9_]{0,31}$"}, "specialty": enum(OWNERSHIP), "tools": array(enum(sorted(TOOLS)), maximum=4), "instructions": text})
    workflow = obj({"agent": {"type": "string"}, "action": enum(sorted(ACTIONS))})
    fields = {"instructions": text, "agents": array(agent, 1, 4), "workflow": array(workflow, 1, 24),
              "review_policy": enum(["schema", "contract", "protected_fields"]), "memory_policy": enum(["none", "inherit_verified"]), "cache_evidence": {"type": "boolean"}}
    change = obj(fields, required=[])
    mutation = obj({"name": text, "reason": text, "changes": change})
    return strict("team_mutations", obj({"observation": obj({"weakness": text, "lesson": text}), "mutations": array(mutation, 2, 2)}))
