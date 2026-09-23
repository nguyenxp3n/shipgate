# TeamNotes Product Specification

## Scope
TeamNotes lets authenticated users work in one or more organizations, author organization-owned notes, share notes with selected organization members, invite members, and inspect scoped administrative audit history.

## Actors and access
Guests receive no application data. Members operate only inside organizations where membership is active. Organization admins may manage membership and view organization audit records. System support does not imply silent impersonation.

## Core journeys
1. Authenticate and select an organization.
2. Create, update, and read an organization-scoped note.
3. Share or unshare a note only with members of the same organization.
4. Invite a member by email; invitation links expire after 24 hours per `DR-TN-001`.
5. Commit business state even if asynchronous email delivery is delayed.

## Non-goals
Payments and AI are excluded from this example release.
