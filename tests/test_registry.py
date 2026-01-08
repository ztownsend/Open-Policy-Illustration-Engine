import pytest

from opie.products.registry import get_product_hooks
from opie.products.annuity_deferred import DeferredAnnuityHooks
from opie.products.annuity_spia import SPIAHooks
from opie.products.term_level import LevelTermHooks
from opie.products.ul_simple import SimpleULHooks
from opie.products.wl_nonpar import WLNonParHooks


def test_registry_returns_hooks_instances() -> None:
    assert isinstance(get_product_hooks("simple_ul"), SimpleULHooks)
    assert isinstance(get_product_hooks("level_term"), LevelTermHooks)
    assert isinstance(get_product_hooks("wl_nonpar"), WLNonParHooks)
    assert isinstance(get_product_hooks("annuity_deferred"), DeferredAnnuityHooks)
    assert isinstance(get_product_hooks("annuity_spia"), SPIAHooks)


def test_registry_unknown_product() -> None:
    with pytest.raises(KeyError):
        get_product_hooks("unknown")
