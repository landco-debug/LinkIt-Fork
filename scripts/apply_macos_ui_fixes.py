#!/usr/bin/env python3
"""Apply minimal macOS presentation fixes to the pinned upstream Linkit source.

No Android source, signed protocol, transfer code or preference keys are changed.
The patch is deliberately strict and fails when upstream code changes.
"""
from pathlib import Path
import sys


def replace_once(source: str, old: str, new: str, label: str) -> str:
    n = source.count(old)
    if n != 1:
        raise RuntimeError(f"{label}: expected one match, got {n}; upstream changed")
    return source.replace(old, new, 1)


def main(root: Path) -> None:
    path = root / "macos/Sources/LinkitMacMenu/main.swift"
    source = path.read_text(encoding="utf-8")

    # The upstream Android app currently describes unrequested call permissions
    # and the optional battery-optimization exemption as 'attention'. Keep those
    # statuses in Diagnostics; exclude them only from the global menu banner.
    old = (
        "        panelViewModel.peerAttentionCount = androidTargets.first?.features.filter "
        "{ $0.state == .attention }.count ?? 0"
    )
    new = """        // Upstream Android reports optional call-control and Doze permissions as
        // 'attention' even when the user hasn't opted into them. Keep these
        // statuses visible in Diagnostics, but don't nag in the compact menu.
        // Receiver and notification-mirroring faults remain actionable here.
        let optionalPermissionIDs: Set<String> = ["phone_control", "battery_exemption"]
        panelViewModel.peerAttentionCount = androidTargets.first?.features.filter {
            $0.state == .attention && !optionalPermissionIDs.contains($0.id)
        }.count ?? 0"""
    source = replace_once(source, old, new, "menu attention filter")

    # The transparent rounded progress NSPanel has an AppKit-generated shadow
    # around its unrounded window bounds. Fix only the transfer window.
    class_start = source.find("private final class LinkitTransferPanel {")
    view_start = source.find("private final class LinkitTransferPanelView:", class_start)
    if class_start < 0 or view_start < 0:
        raise RuntimeError("transfer panel class boundaries were not found")
    transfer_class = source[class_start:view_start]
    transfer_class = replace_once(
        transfer_class,
        "        panel.hasShadow = true",
        "        // Avoid a rectangular NSPanel shadow outside the rounded content.\n"
        "        panel.hasShadow = false",
        "transfer panel shadow",
    )
    source = source[:class_start] + transfer_class + source[view_start:]

    view_start = source.find("private final class LinkitTransferPanelView:")
    view = source[view_start:]
    view = replace_once(
        view,
        "        layer?.cornerRadius = 18\n        layer?.masksToBounds = true",
        "        layer?.cornerRadius = 18\n"
        "        layer?.cornerCurve = .continuous\n"
        "        layer?.masksToBounds = true",
        "transfer panel corner style",
    )
    source = source[:view_start] + view
    path.write_text(source, encoding="utf-8")
    print("Applied macOS-only panel and attention-banner fixes")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: apply_macos_ui_fixes.py UPSTREAM_ROOT")
    main(Path(sys.argv[1]).resolve())
