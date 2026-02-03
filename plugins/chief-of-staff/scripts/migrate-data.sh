#!/bin/bash
#
# migrate-data.sh - Migrate data from old inbox plugins to Chief-of-Staff
#
# Usage: ./migrate-data.sh [--dry-run]
#
# This script migrates data files from the old standalone plugins:
#   - inbox-triage
#   - inbox-to-parcel
#   - inbox-to-reminder
#   - newsletter-unsubscriber
#
# Into the new unified chief-of-staff plugin.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    echo -e "${YELLOW}DRY RUN MODE - No files will be modified${NC}"
    echo ""
fi

# Base paths
PLUGIN_CACHE="$HOME/.claude/plugins/cache/omarshahine-agent-plugins"
COS_DATA="$PLUGIN_CACHE/chief-of-staff/data"
BACKUP_DIR="$HOME/Desktop/inbox-plugins-backup-$(date +%Y%m%d-%H%M%S)"

# Old plugin paths
INBOX_TRIAGE_DATA="$PLUGIN_CACHE/inbox-triage/data"
INBOX_TO_PARCEL_DATA="$PLUGIN_CACHE/inbox-to-parcel/data"
INBOX_TO_REMINDER_DATA="$PLUGIN_CACHE/inbox-to-reminder/data"
NEWSLETTER_DATA="$PLUGIN_CACHE/newsletter-unsubscriber/data"

echo -e "${BLUE}=== Chief-of-Staff Data Migration ===${NC}"
echo ""

# Check if chief-of-staff is installed
if [[ ! -d "$COS_DATA" ]]; then
    echo -e "${RED}Error: Chief-of-Staff plugin not found at $COS_DATA${NC}"
    echo "Please install it first: /plugin install chief-of-staff@omarshahine-agent-plugins"
    exit 1
fi

# Check for old plugins
found_old=false
if [[ -d "$INBOX_TRIAGE_DATA" ]]; then
    echo -e "${GREEN}Found: inbox-triage/data${NC}"
    found_old=true
fi
if [[ -d "$INBOX_TO_PARCEL_DATA" ]]; then
    echo -e "${GREEN}Found: inbox-to-parcel/data${NC}"
    found_old=true
fi
if [[ -d "$INBOX_TO_REMINDER_DATA" ]]; then
    echo -e "${GREEN}Found: inbox-to-reminder/data${NC}"
    found_old=true
fi
if [[ -d "$NEWSLETTER_DATA" ]]; then
    echo -e "${GREEN}Found: newsletter-unsubscriber/data${NC}"
    found_old=true
fi

if [[ "$found_old" == false ]]; then
    echo -e "${YELLOW}No old plugin data found. Nothing to migrate.${NC}"
    exit 0
fi

echo ""

# Create backup directory
if [[ "$DRY_RUN" == false ]]; then
    echo -e "${BLUE}Creating backup at: $BACKUP_DIR${NC}"
    mkdir -p "$BACKUP_DIR"
fi

# Function to migrate a file
migrate_file() {
    local src="$1"
    local dest="$2"
    local desc="$3"

    if [[ -f "$src" ]]; then
        if [[ -f "$dest" ]]; then
            echo -e "${YELLOW}  [EXISTS] $desc - destination exists, backing up and replacing${NC}"
            if [[ "$DRY_RUN" == false ]]; then
                cp "$dest" "$BACKUP_DIR/$(basename $dest).existing"
            fi
        else
            echo -e "${GREEN}  [COPY] $desc${NC}"
        fi

        if [[ "$DRY_RUN" == false ]]; then
            # Backup source
            cp "$src" "$BACKUP_DIR/$(basename $src)"
            # Copy to destination
            cp "$src" "$dest"
        else
            echo "         Would copy: $src -> $dest"
        fi
    fi
}

# Function to merge settings files
merge_settings() {
    echo -e "${BLUE}Merging settings files...${NC}"

    # Start with inbox-triage settings as base (most comprehensive)
    if [[ -f "$INBOX_TRIAGE_DATA/settings.yaml" ]]; then
        migrate_file "$INBOX_TRIAGE_DATA/settings.yaml" "$COS_DATA/settings.yaml" "inbox-triage/settings.yaml"
    fi

    # Note: inbox-to-parcel and inbox-to-reminder settings would need manual review
    # as they may have different provider configurations
    if [[ -f "$INBOX_TO_PARCEL_DATA/settings.yaml" ]]; then
        echo -e "${YELLOW}  [MANUAL] inbox-to-parcel/settings.yaml - review and merge manually${NC}"
        if [[ "$DRY_RUN" == false ]]; then
            cp "$INBOX_TO_PARCEL_DATA/settings.yaml" "$BACKUP_DIR/inbox-to-parcel-settings.yaml"
        fi
    fi

    if [[ -f "$INBOX_TO_REMINDER_DATA/settings.yaml" ]]; then
        echo -e "${YELLOW}  [MANUAL] inbox-to-reminder/settings.yaml - review and merge manually${NC}"
        if [[ "$DRY_RUN" == false ]]; then
            cp "$INBOX_TO_REMINDER_DATA/settings.yaml" "$BACKUP_DIR/inbox-to-reminder-settings.yaml"
        fi
    fi

    if [[ -f "$NEWSLETTER_DATA/settings.yaml" ]]; then
        echo -e "${YELLOW}  [MANUAL] newsletter-unsubscriber/settings.yaml - review and merge manually${NC}"
        if [[ "$DRY_RUN" == false ]]; then
            cp "$NEWSLETTER_DATA/settings.yaml" "$BACKUP_DIR/newsletter-unsubscriber-settings.yaml"
        fi
    fi
}

echo -e "${BLUE}Migrating from inbox-triage...${NC}"
if [[ -d "$INBOX_TRIAGE_DATA" ]]; then
    migrate_file "$INBOX_TRIAGE_DATA/filing-rules.yaml" "$COS_DATA/filing-rules.yaml" "filing-rules.yaml (learned patterns)"
    migrate_file "$INBOX_TRIAGE_DATA/user-preferences.yaml" "$COS_DATA/user-preferences.yaml" "user-preferences.yaml"
    migrate_file "$INBOX_TRIAGE_DATA/delete-patterns.yaml" "$COS_DATA/delete-patterns.yaml" "delete-patterns.yaml"
    migrate_file "$INBOX_TRIAGE_DATA/decision-history.yaml" "$COS_DATA/decision-history.yaml" "decision-history.yaml"
    migrate_file "$INBOX_TRIAGE_DATA/interview-state.yaml" "$COS_DATA/interview-state.yaml" "interview-state.yaml"
else
    echo -e "  ${YELLOW}Not found - skipping${NC}"
fi

echo ""
echo -e "${BLUE}Migrating from newsletter-unsubscriber...${NC}"
if [[ -d "$NEWSLETTER_DATA" ]]; then
    migrate_file "$NEWSLETTER_DATA/newsletter-lists.yaml" "$COS_DATA/newsletter-lists.yaml" "newsletter-lists.yaml (allowlist/unsubscribed)"
else
    echo -e "  ${YELLOW}Not found - skipping${NC}"
fi

echo ""
merge_settings

echo ""
echo -e "${BLUE}=== Migration Summary ===${NC}"

if [[ "$DRY_RUN" == false ]]; then
    echo -e "${GREEN}Backup created at: $BACKUP_DIR${NC}"
    echo ""
    echo "Files migrated to: $COS_DATA"
    echo ""
    ls -la "$COS_DATA"/*.yaml 2>/dev/null || echo "No yaml files found"
    echo ""
    echo -e "${YELLOW}IMPORTANT: Review the backup directory for any settings that need manual merging:${NC}"
    echo "  - inbox-to-parcel-settings.yaml"
    echo "  - inbox-to-reminder-settings.yaml"
    echo "  - newsletter-unsubscriber-settings.yaml"
    echo ""
    echo -e "${GREEN}Migration complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review merged settings in $COS_DATA/settings.yaml"
    echo "  2. Test with: /chief-of-staff:status"
    echo "  3. If everything works, uninstall old plugins:"
    echo "     /plugin uninstall inbox-triage@omarshahine-agent-plugins"
    echo "     /plugin uninstall inbox-to-parcel@omarshahine-agent-plugins"
    echo "     /plugin uninstall inbox-to-reminder@omarshahine-agent-plugins"
    echo "     /plugin uninstall newsletter-unsubscriber@omarshahine-agent-plugins"
else
    echo -e "${YELLOW}DRY RUN complete. Run without --dry-run to perform migration.${NC}"
fi
