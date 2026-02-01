# Email Classification Skill

Knowledge for classifying emails by type, purpose, and filing destination.

## Email Categories

### Transactional
- Order confirmations, shipping, receipts
- Password resets, verification codes
- Time-sensitive, usually automated

### Financial
- Bank statements, bill notifications
- Payment confirmations, investment updates
- Often has masked account numbers

### Travel
- Flight/hotel confirmations
- Itineraries with dates and confirmation numbers
- Often time-sensitive

### Social/Notifications
- Social platform updates
- App notifications
- Generally low priority

### Marketing
- Promotions, newsletters
- Usually has unsubscribe link
- Often from marketing@ addresses

## Confidence Factors

**High (90%+):**
- Domain-only rules with >95% historical accuracy
- Exact sender match with consistent history

**Medium (70-89%):**
- Domain appears in multiple folders
- Subject pattern with generic domain

**Low (<70%):**
- Generic domains (gmail.com, outlook.com)
- No clear pattern match

## Pattern Detection

### Security Alerts
```
subject: sign-in, login, new device, password reset, 2FA
sender: security@, noreply@, alert@
```

### Payment Issues
```
subject: declined, failed, payment required, billing
```

### Marketing
```
subject: sale, % off, limited time
sender: marketing@, promotions@, newsletter@
has: unsubscribe link
```

## Best Practices

1. Domain rules > subject rules (more reliable)
2. Don't file by date (unmanageable)
3. Keep folder structure flat
4. Always review security alerts
5. Separate transactional from conversational
