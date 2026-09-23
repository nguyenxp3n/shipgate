# TeamNotes Product Notes

## Purpose
TeamNotes is a small multi-tenant web SaaS for teams to create notes, share notes with organization members, invite new members by email, and administer membership safely.

## Actors
- Guest: may view the marketing shell only.
- Member: may access only organizations they belong to and notes authorized for that organization.
- Organization admin: may invite or remove members and inspect organization audit history.
- System admin: may operate support tooling but may not silently impersonate a member.

## Core behavior
- Authentication is required for all application data.
- A user may belong to more than one organization.
- Notes are owned by one organization and one author.
- Notes can be private-to-author or shared with selected organization members.
- Sharing outside the note's organization is forbidden.
- Organization admins may invite users by email.
- Product draft says invitation links expire after **24 hours**.
- Notification delivery is asynchronous and must not roll back the underlying business transaction.
- Payments and AI features are out of scope for the base example.
