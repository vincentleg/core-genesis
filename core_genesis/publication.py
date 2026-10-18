"""Publish reviewable mission evidence without exposing unapproved social drafts."""
import copy
import hashlib
import json


def public_company_record(mission, governance):
    if (mission.get('snapshot') or {}).get('external_transmission_allowed') is False:
        raise ValueError('Private local CORE snapshots cannot enter public evidence exports')
    result = copy.deepcopy(mission)
    growth = result.get("artifacts", {}).get("growth")
    if growth:
        growth["strategy"] = "Draft strategy withheld from the public export pending CEO publication review."
        growth["public_content_withheld"] = True
        for post in growth["posts"]:
            post["text"] = "[Draft content withheld pending CEO publication approval]"
            post["visual_brief"] = "[Withheld]"
    for event in result.get("events", []):
        if event.get("agent") == "Growth Director" and event.get("output") is not None:
            event["output_sha256"] = hashlib.sha256(event["output"].encode()).hexdigest()
            event["output"] = "[Draft output withheld; hash retained for local audit]"
    return {"mission": result, "governance": copy.deepcopy(governance), "publication_note": "Recorded evidence only. Pending social draft content is withheld. No public CEO authority or inference endpoint."}
