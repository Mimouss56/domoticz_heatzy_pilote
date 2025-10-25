#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Version management script for Heatzy Pilote Plugin

This script handles automatic version bumping, changelog generation,
and release preparation.
"""

import argparse
import re
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Tuple, List, Optional


class VersionManager:
    """Manages version bumping and release preparation."""
    
    def __init__(self, project_root: Path = None):
        """Initialize version manager."""
        self.project_root = project_root or Path(__file__).parent
        self.version_file = self.project_root / ".version.toml"
        
    def get_current_version(self) -> str:
        """Get current version from plugin file."""
        plugin_file = self.project_root / "plugin_modular.py"
        
        if not plugin_file.exists():
            return "1.0.0"
            
        with open(plugin_file, 'r') as f:
            content = f.read()
            
        match = re.search(r'version="([^"]+)"', content)
        if match:
            return match.group(1)
        
        return "1.0.0"
    
    def parse_version(self, version: str) -> Tuple[int, int, int]:
        """Parse semantic version string."""
        try:
            major, minor, patch = version.split('.')
            return int(major), int(minor), int(patch)
        except ValueError:
            raise ValueError(f"Invalid version format: {version}")
    
    def bump_version(self, current: str, bump_type: str) -> str:
        """Bump version according to type."""
        major, minor, patch = self.parse_version(current)
        
        if bump_type == "major":
            return f"{major + 1}.0.0"
        elif bump_type == "minor":
            return f"{major}.{minor + 1}.0"
        elif bump_type == "patch":
            return f"{major}.{minor}.{patch + 1}"
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")
    
    def detect_version_bump_type(self) -> str:
        """Detect version bump type from git commits."""
        try:
            # Get commits since last tag
            result = subprocess.run(
                ["git", "log", "--oneline", "$(git describe --tags --abbrev=0)..HEAD"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0:
                # No tags yet, get all commits
                result = subprocess.run(
                    ["git", "log", "--oneline"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root
                )
            
            commits = result.stdout.strip()
            if not commits:
                return "patch"
            
            # Analyze commit messages
            commit_messages = commits.lower()
            
            # Check for breaking changes
            if any(keyword in commit_messages for keyword in ["break", "breaking", "major"]):
                return "major"
            
            # Check for features
            if any(keyword in commit_messages for keyword in ["feat", "feature", "add", "minor"]):
                return "minor"
            
            # Default to patch
            return "patch"
            
        except Exception:
            return "patch"
    
    def update_version_in_files(self, new_version: str) -> None:
        """Update version in all relevant files."""
        files_to_update = [
            {
                "file": "plugin_modular.py",
                "pattern": r'version="[^"]*"',
                "replacement": f'version="{new_version}"'
            },
            {
                "file": "src/__init__.py", 
                "pattern": r'__version__ = "[^"]*"',
                "replacement": f'__version__ = "{new_version}"'
            }
        ]
        
        for file_info in files_to_update:
            file_path = self.project_root / file_info["file"]
            
            if file_path.exists():
                with open(file_path, 'r') as f:
                    content = f.read()
                
                updated_content = re.sub(
                    file_info["pattern"],
                    file_info["replacement"],
                    content
                )
                
                with open(file_path, 'w') as f:
                    f.write(updated_content)
                
                print(f"✅ Updated version in {file_info['file']}")
    
    def update_changelog(self, new_version: str, bump_type: str) -> None:
        """Update CHANGELOG.md with new version."""
        changelog_path = self.project_root / "CHANGELOG.md"
        
        if not changelog_path.exists():
            print("⚠️  CHANGELOG.md not found, skipping update")
            return
        
        with open(changelog_path, 'r') as f:
            content = f.read()
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Create new version section
        new_section = f"""## [{new_version}] - {today}

### {bump_type.title()}
- Automated version bump
- See git commits for detailed changes

"""
        
        # Find where to insert new section
        if "## [Unreleased]" in content:
            # Replace unreleased section
            content = re.sub(
                r"## \[Unreleased\].*?(?=\n## \[|\n$)",
                new_section.rstrip(),
                content,
                flags=re.DOTALL
            )
        else:
            # Insert after first heading
            lines = content.split('\n')
            insert_pos = 0
            
            for i, line in enumerate(lines):
                if line.startswith('## ') and '[' in line:
                    insert_pos = i
                    break
            
            if insert_pos > 0:
                lines.insert(insert_pos, new_section.rstrip())
                lines.insert(insert_pos + 1, "")
            else:
                # Add at the end of first section
                for i, line in enumerate(lines):
                    if line.startswith('## '):
                        insert_pos = i
                        break
                if insert_pos > 0:
                    lines.insert(insert_pos, new_section.rstrip())
                    lines.insert(insert_pos + 1, "")
            
            content = '\n'.join(lines)
        
        with open(changelog_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated CHANGELOG.md with version {new_version}")
    
    def create_git_tag(self, version: str) -> None:
        """Create git tag for the new version."""
        try:
            # Create annotated tag
            subprocess.run([
                "git", "tag", "-a", f"v{version}",
                "-m", f"Release version {version}"
            ], check=True, cwd=self.project_root)
            
            print(f"✅ Created git tag v{version}")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create git tag: {e}")
    
    def commit_changes(self, version: str) -> None:
        """Commit version changes."""
        try:
            # Add all changed files
            subprocess.run(["git", "add", "."], check=True, cwd=self.project_root)
            
            # Commit changes
            subprocess.run([
                "git", "commit", "-m", f"chore: bump version to {version}"
            ], check=True, cwd=self.project_root)
            
            print(f"✅ Committed version changes")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to commit changes: {e}")
    
    def bump(self, bump_type: str = None, tag: bool = False, commit: bool = False) -> str:
        """Perform version bump."""
        current_version = self.get_current_version()
        print(f"Current version: {current_version}")
        
        # Auto-detect bump type if not specified
        if bump_type is None:
            bump_type = self.detect_version_bump_type()
            print(f"Auto-detected bump type: {bump_type}")
        
        # Calculate new version
        new_version = self.bump_version(current_version, bump_type)
        print(f"New version: {new_version}")
        
        # Update files
        self.update_version_in_files(new_version)
        self.update_changelog(new_version, bump_type)
        
        # Commit changes if requested
        if commit:
            self.commit_changes(new_version)
        
        # Create tag if requested
        if tag:
            self.create_git_tag(new_version)
        
        return new_version
    
    def status(self) -> None:
        """Show current version status."""
        current_version = self.get_current_version()
        suggested_bump = self.detect_version_bump_type()
        
        print(f"📋 Version Status")
        print(f"   Current version: {current_version}")
        print(f"   Suggested bump:  {suggested_bump}")
        
        # Show what new version would be
        for bump_type in ["patch", "minor", "major"]:
            new_version = self.bump_version(current_version, bump_type)
            print(f"   {bump_type:6} -> {new_version}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Version management for Heatzy Pilote Plugin"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Status command
    subparsers.add_parser("status", help="Show version status")
    
    # Bump command
    bump_parser = subparsers.add_parser("bump", help="Bump version")
    bump_parser.add_argument(
        "type",
        nargs="?",
        choices=["patch", "minor", "major"],
        help="Version bump type (auto-detected if not specified)"
    )
    bump_parser.add_argument(
        "--tag", action="store_true",
        help="Create git tag"
    )
    bump_parser.add_argument(
        "--commit", action="store_true", 
        help="Commit changes"
    )
    
    # Current command
    subparsers.add_parser("current", help="Show current version")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    version_manager = VersionManager()
    
    if args.command == "status":
        version_manager.status()
    elif args.command == "current":
        print(version_manager.get_current_version())
    elif args.command == "bump":
        new_version = version_manager.bump(
            args.type,
            tag=args.tag,
            commit=args.commit
        )
        print(f"🎉 Version bumped to {new_version}")


if __name__ == "__main__":
    main()