#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Sync Claude Code configuration from this project to user-level ~/.claude directory.

Usage:
    # Preview what would be synced (dry-run)
    uv run scripts/sync-to-user.py

    # Actually sync (copy files)
    uv run scripts/sync-to-user.py --apply

    # Use symlinks instead of copies (stays in sync automatically)
    uv run scripts/sync-to-user.py --apply --symlink

    # Sync specific components only
    uv run scripts/sync-to-user.py --apply --only agents,commands

    # Force overwrite without prompts
    uv run scripts/sync-to-user.py --apply --force
"""

import argparse
import shutil
import sys
from pathlib import Path
from datetime import datetime


# Components that can be synced
SYNCABLE_COMPONENTS = {
    "agents": "Sub-agent definitions",
    "commands": "Slash commands",
    "hooks": "Lifecycle hook scripts",
    "output-styles": "Response formatting templates",
    "status_lines": "Terminal status bar scripts",
}

# Files/patterns to exclude from sync
EXCLUDE_PATTERNS = [
    ".DS_Store",
    "__pycache__",
    "*.pyc",
    ".git",
    "data",  # Session data should not be synced
    "settings.json",  # Project-specific settings
    "settings.local.json",  # Local overrides
]


def should_exclude(path: Path) -> bool:
    """Check if a path should be excluded from sync."""
    name = path.name
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith("*"):
            if name.endswith(pattern[1:]):
                return True
        elif name == pattern:
            return True
    return False


def get_project_claude_dir() -> Path:
    """Get the .claude directory in this project."""
    script_dir = Path(__file__).parent.parent
    claude_dir = script_dir / ".claude"
    if not claude_dir.exists():
        print(f"Error: Project .claude directory not found at {claude_dir}")
        sys.exit(1)
    return claude_dir


def get_user_claude_dir() -> Path:
    """Get the user-level ~/.claude directory."""
    return Path.home() / ".claude"


def collect_files(source_dir: Path) -> list[Path]:
    """Recursively collect all files in a directory, respecting exclusions."""
    files = []
    if not source_dir.exists():
        return files

    for item in source_dir.rglob("*"):
        if item.is_file() and not should_exclude(item):
            # Check parent directories for exclusions too
            exclude = False
            for parent in item.relative_to(source_dir).parents:
                if should_exclude(Path(parent.name)):
                    exclude = True
                    break
            if not exclude:
                files.append(item)
    return files


def format_size(size: int | float) -> str:
    """Format file size in human-readable form."""
    for unit in ['B', 'KB', 'MB']:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}GB"


def sync_component(
    component: str,
    project_dir: Path,
    user_dir: Path,
    dry_run: bool = True,
    use_symlink: bool = False,
    force: bool = False,
) -> tuple[int, int, int]:
    """
    Sync a single component from project to user directory.

    Returns: (files_added, files_updated, files_skipped)
    """
    source = project_dir / component
    target = user_dir / component

    if not source.exists():
        print(f"  ⚠ Source not found: {source}")
        return (0, 0, 0)

    files = collect_files(source)
    added, updated, skipped = 0, 0, 0

    for src_file in files:
        rel_path = src_file.relative_to(source)
        dst_file = target / rel_path

        # Check if destination exists
        dst_exists = dst_file.exists() or dst_file.is_symlink()

        # Determine action
        if dst_exists:
            if dst_file.is_symlink():
                # Already a symlink - check if points to same source
                if dst_file.resolve() == src_file.resolve():
                    skipped += 1
                    continue
                action = "update (symlink)"
            else:
                # Regular file - check if identical
                if dst_file.read_bytes() == src_file.read_bytes():
                    skipped += 1
                    continue
                action = "update"

            if not force and not dry_run:
                print(f"    ! Would overwrite: {rel_path}")
                skipped += 1
                continue
            updated += 1
        else:
            action = "add"
            added += 1

        # Show what would happen
        size = format_size(src_file.stat().st_size)
        symlink_indicator = " → symlink" if use_symlink else ""
        print(f"    [{action}] {rel_path} ({size}){symlink_indicator}")

        if not dry_run:
            # Create parent directories
            dst_file.parent.mkdir(parents=True, exist_ok=True)

            # Remove existing file/symlink if updating
            if dst_exists:
                if dst_file.is_symlink():
                    dst_file.unlink()
                else:
                    dst_file.unlink()

            # Create symlink or copy
            if use_symlink:
                dst_file.symlink_to(src_file.resolve())
            else:
                shutil.copy2(src_file, dst_file)

    return (added, updated, skipped)


def main():
    parser = argparse.ArgumentParser(
        description="Sync Claude Code configuration to user-level ~/.claude directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually perform the sync (default is dry-run preview)",
    )
    parser.add_argument(
        "--symlink",
        action="store_true",
        help="Use symlinks instead of copies (keeps files in sync automatically)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files without prompting",
    )
    parser.add_argument(
        "--only",
        type=str,
        help=f"Comma-separated list of components to sync: {','.join(SYNCABLE_COMPONENTS.keys())}",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create backup of existing ~/.claude before syncing",
    )

    args = parser.parse_args()

    # Determine which components to sync
    if args.only:
        components = [c.strip() for c in args.only.split(",")]
        invalid = [c for c in components if c not in SYNCABLE_COMPONENTS]
        if invalid:
            print(f"Error: Invalid components: {', '.join(invalid)}")
            print(f"Valid components: {', '.join(SYNCABLE_COMPONENTS.keys())}")
            sys.exit(1)
    else:
        components = list(SYNCABLE_COMPONENTS.keys())

    project_dir = get_project_claude_dir()
    user_dir = get_user_claude_dir()

    print("=" * 60)
    print("Claude Code Configuration Sync")
    print("=" * 60)
    print(f"Source: {project_dir}")
    print(f"Target: {user_dir}")
    print(f"Mode:   {'APPLY' if args.apply else 'DRY-RUN (preview only)'}")
    if args.symlink:
        print("Method: Symlinks (auto-sync)")
    else:
        print("Method: Copy files")
    print("=" * 60)

    # Create backup if requested
    if args.backup and args.apply and user_dir.exists():
        backup_name = f".claude.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = Path.home() / backup_name
        print(f"\nCreating backup: {backup_path}")
        shutil.copytree(user_dir, backup_path)
        print("  ✓ Backup created")

    # Ensure user directory exists
    if args.apply:
        user_dir.mkdir(parents=True, exist_ok=True)

    # Sync each component
    total_added, total_updated, total_skipped = 0, 0, 0

    for component in components:
        print(f"\n📁 {component}/ - {SYNCABLE_COMPONENTS[component]}")
        added, updated, skipped = sync_component(
            component,
            project_dir,
            user_dir,
            dry_run=not args.apply,
            use_symlink=args.symlink,
            force=args.force,
        )
        total_added += added
        total_updated += updated
        total_skipped += skipped

        if added == 0 and updated == 0 and skipped == 0:
            print("    (empty or not found)")
        elif added == 0 and updated == 0:
            print(f"    ✓ All {skipped} files up to date")

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"  Added:   {total_added}")
    print(f"  Updated: {total_updated}")
    print(f"  Skipped: {total_skipped} (already up to date)")

    if not args.apply:
        print("\n⚠ This was a dry-run. Use --apply to actually sync files.")
        if total_updated > 0 and not args.force:
            print("  Use --force to overwrite existing files.")
        print("\nExamples:")
        print("  uv run scripts/sync-to-user.py --apply          # Copy files")
        print("  uv run scripts/sync-to-user.py --apply --symlink  # Use symlinks")
        print("  uv run scripts/sync-to-user.py --apply --force    # Overwrite existing")
    else:
        print("\n✓ Sync complete!")
        if args.symlink:
            print("  Files are symlinked - changes in project auto-propagate to ~/.claude")
        else:
            print("  Files were copied - run again to sync future changes")


if __name__ == "__main__":
    main()
