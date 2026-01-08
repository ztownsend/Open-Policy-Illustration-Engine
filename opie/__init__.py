"""Open Policy Illustration Engine (OPIE)."""

from opie.core.engine import run_illustration as _run_illustration
from opie.core.solve import solve_illustration
from opie.core.types import IllustrationRequest, IllustrationResult
from opie.products.registry import get_product_hooks

__all__ = ["run_illustration", "IllustrationRequest", "IllustrationResult"]


def run_illustration(request: IllustrationRequest) -> IllustrationResult:
    hooks = get_product_hooks(request.product_code)
    if request.solve is not None:
        return solve_illustration(request, hooks)
    return _run_illustration(request, hooks)
