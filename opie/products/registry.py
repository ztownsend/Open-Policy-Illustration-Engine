"""Product registry for mapping product codes to hooks."""

from __future__ import annotations

from opie.products.annuity_deferred import DeferredAnnuityHooks
from opie.products.annuity_spia import SPIAHooks
from opie.products.term_level import LevelTermHooks
from opie.products.ul_simple import SimpleULHooks
from opie.products.wl_nonpar import WLNonParHooks

PRODUCT_REGISTRY = {
    "simple_ul": SimpleULHooks(),
    "level_term": LevelTermHooks(),
    "wl_nonpar": WLNonParHooks(),
    "annuity_deferred": DeferredAnnuityHooks(),
    "annuity_spia": SPIAHooks(),
}


def get_product_hooks(product_code: str):
    try:
        return PRODUCT_REGISTRY[product_code]
    except KeyError as exc:
        raise KeyError(f"Unknown product_code: {product_code}") from exc
