from custom_components.evaplex.application.feature_map import (
    FEATURE_KEYS,
    FEATURE_PLATFORMS,
    HaPlatform,
    decls_for,
    decls_for_platform,
    resolve_feature_keys,
    unique_id_for,
)


def test_every_known_feature_has_mapping() -> None:
    for key in FEATURE_KEYS:
        assert key in FEATURE_PLATFORMS
        assert FEATURE_PLATFORMS[key]


def test_unknown_feature_is_skipped() -> None:
    keys = resolve_feature_keys(("feeding", "unknown_key"), ())
    assert keys == ("feeding",)
    platforms = {decl.platform for decl in decls_for(keys)}
    assert HaPlatform.BUTTON in platforms
    assert HaPlatform.NUMBER in platforms


def test_empty_or_missing_manifest_falls_back_to_capabilities() -> None:
    assert resolve_feature_keys(None, ("feed",)) == ("feeding",)
    assert resolve_feature_keys((), ("on_off",)) == ("power",)
    assert resolve_feature_keys([], ("feed", "on_off")) == ("feeding", "power")


def test_unknown_capability_does_not_invent_entities() -> None:
    assert resolve_feature_keys(None, ("other",)) == ()
    decls = decls_for(())
    assert [decl.entity_key for decl in decls] == ["online"]


def test_unique_id_uses_feature_and_entity_keys() -> None:
    assert unique_id_for("dev-1", "feeding", "feed") == "dev-1_feeding_feed"
    assert unique_id_for("dev-1", "feeding", "default_portions") == "dev-1_feeding_default_portions"
    assert unique_id_for("dev-1", "", "online") == "dev-1_online"


def test_platform_filter_keeps_single_registry() -> None:
    buttons = decls_for_platform(("feeding", "power"), HaPlatform.BUTTON)
    switches = decls_for_platform(("feeding", "power"), HaPlatform.SWITCH)
    assert [decl.entity_key for decl in buttons] == ["feed"]
    assert [decl.entity_key for decl in switches] == ["power"]
