"""One small real request to confirm the Crusoe connection works."""

import sys
from pathlib import Path
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core_genesis import CrusoeClient, CrusoeError  # noqa: E402
from core_genesis.budget import RequestBudget, BudgetError  # noqa: E402


def main() -> int:
    client = CrusoeClient(max_retries=0, timeout=30)
    try:
        resp, metrics = RequestBudget().chat("smoke-" + uuid.uuid4().hex, 0, "Smoke",
            [{"role": "user", "content": "Reply with exactly: pong"}],
            max_tokens=256,
            client=client,
        )
    except BudgetError as e:
        print(str(e))
        return 1
    except CrusoeError as e:
        print(f"model={client.model} status={e.status} valid=False error={e.body[:300]}")
        return 1
    choice = resp["choices"][0]
    content = (choice["message"].get("content") or "").strip()
    print(f"model={resp.get('model')} status={client.last_status} finish={choice.get('finish_reason')}")
    print(f"content={content!r}")
    print(f"usage={resp.get('usage')}")
    print(f"estimated_cost_usd={metrics['cost_estimate_usd']}")
    print(f"valid={bool(content)}")
    return 0 if content else 1


if __name__ == "__main__":
    sys.exit(main())
