# Pine Time API Reference

This document provides a summary of the main REST API endpoints for the Pine Time application backend. Use this as a quick reference for endpoint URLs, methods, request/response schemas, authentication, and error handling conventions.

---

## Authentication

### POST `/auth/token`
- **Description:** Obtain JWT access token
- **Request:** `{ "username": str, "password": str }`
- **Response:** `{ "access_token": str, "token_type": "bearer" }`
- **Auth Required:** No

### POST `/auth/refresh`
- **Description:** Refresh JWT access token
- **Request:** `{ "refresh_token": str }`
- **Response:** `{ "access_token": str, "token_type": "bearer" }`
- **Auth Required:** No

### POST `/auth/verify`
- **Description:** Verify validity of access token
- **Request:** `{ "token": str }`
- **Response:** `{ "valid": bool }`
- **Auth Required:** No

---

## Users

### GET `/users/`
- **Description:** List all users
- **Response:** `List[User]`
- **Auth Required:** Yes (admin)

### POST `/users/`
- **Description:** Create a new user
- **Request:** `UserCreate`
- **Response:** `User`
- **Auth Required:** Yes (admin)

### GET `/users/me`
- **Description:** Get current user's profile
- **Response:** `User`
- **Auth Required:** Yes

### PUT `/users/me`
- **Description:** Update current user's profile
- **Request:** `UserUpdate`
- **Response:** `User`
- **Auth Required:** Yes

### GET `/users/{user_id}`
- **Description:** Get user by ID
- **Response:** `User`
- **Auth Required:** Yes (admin)

### PUT `/users/{user_id}`
- **Description:** Update user by ID
- **Request:** `UserUpdate`
- **Response:** `User`
- **Auth Required:** Yes (admin)

### POST `/users/register`
- **Description:** Register a new user (public)
- **Request:** `UserRegister`
- **Response:** `User`
- **Auth Required:** No

---

## Events

### GET `/events/`
- **Description:** List all events
- **Response:** `List[Event]`
- **Auth Required:** Yes

### POST `/events/`
- **Description:** Create new event
- **Request:** `EventCreate`
- **Response:** `Event`
- **Auth Required:** Yes (admin)

### GET `/events/{event_id}`
- **Description:** Get event details
- **Response:** `Event`
- **Auth Required:** Yes

### PUT `/events/{event_id}`
- **Description:** Update event
- **Request:** `EventUpdate`
- **Response:** `Event`
- **Auth Required:** Yes (admin)

### DELETE `/events/{event_id}`
- **Description:** Delete event
- **Response:** `Event`
- **Auth Required:** Yes (admin)

### POST `/events/{event_id}/register`
- **Description:** Register for event
- **Request:** `{}`
- **Response:** `Registration`
- **Auth Required:** Yes

### POST `/events/{event_id}/check-in`
- **Description:** Check-in user to event
- **Request:** `{ "user_id": int }`
- **Response:** `Registration`
- **Auth Required:** Yes (admin)

### POST `/events/{event_id}/self-check-in`
- **Description:** Self check-in to event
- **Request:** `{}`
- **Response:** `Registration`
- **Auth Required:** Yes

---

## Registrations

### GET `/registrations/events/{event_id}/registrations`
- **Description:** List registrations for event
- **Response:** `List[Registration]`
- **Auth Required:** Yes (admin)

### GET `/registrations/users/me/registrations`
- **Description:** List current user's registrations
- **Response:** `List[Registration]`
- **Auth Required:** Yes

### DELETE `/registrations/events/{event_id}/register`
- **Description:** Cancel registration for event
- **Response:** `Registration`
- **Auth Required:** Yes

---

## Badges

### GET `/badges/`
- **Description:** List all badge types
- **Response:** `List[BadgeType]`
- **Auth Required:** Yes

### GET `/badges/me`
- **Description:** List current user's badges
- **Response:** `List[Badge]`
- **Auth Required:** Yes

### GET `/badges/users/{user_id}`
- **Description:** List badges for user
- **Response:** `List[Badge]`
- **Auth Required:** Yes (admin)

### GET `/badges/{badge_id}`
- **Description:** Get badge details
- **Response:** `Badge`
- **Auth Required:** Yes

---

## Badges (Admin)

### POST `/badges_admin/types/`
- **Description:** Create badge type
- **Request:** `BadgeTypeCreate`
- **Response:** `BadgeType`
- **Auth Required:** Yes (admin)

### PUT `/badges_admin/types/{badge_type_id}`
- **Description:** Update badge type
- **Request:** `BadgeTypeUpdate`
- **Response:** `BadgeType`
- **Auth Required:** Yes (admin)

### DELETE `/badges_admin/types/{badge_type_id}`
- **Description:** Delete badge type
- **Response:** None
- **Auth Required:** Yes (admin)

### POST `/badges_admin/assign`
- **Description:** Assign badge to user
- **Request:** `{ "user_id": int, "badge_type_id": int }`
- **Response:** `Badge`
- **Auth Required:** Yes (admin)

### POST `/badges_admin/revoke`
- **Description:** Revoke badge from user
- **Request:** `{ "user_id": int, "badge_id": int }`
- **Response:** `Badge`
- **Auth Required:** Yes (admin)

---

## Points

### GET `/points/balance`
- **Description:** Get current user's points balance
- **Response:** `int`
- **Auth Required:** Yes

### GET `/points/transactions`
- **Description:** List current user's points transactions
- **Response:** `List[PointsTransaction]`
- **Auth Required:** Yes

### POST `/points/award`
- **Description:** Award points to user
- **Request:** `{ "user_id": int, "amount": int }`
- **Response:** `PointsTransaction`
- **Auth Required:** Yes (admin)

### POST `/points/redeem`
- **Description:** Redeem points
- **Request:** `{ "amount": int }`
- **Response:** `PointsTransaction`
- **Auth Required:** Yes

### GET `/points/leaderboard`
- **Description:** Get points leaderboard
- **Response:** `List[dict]`
- **Auth Required:** Yes

---

## Error Handling & Conventions
- All endpoints return JSON with appropriate HTTP status codes.
- Errors are returned as `{ "detail": str }` or custom error objects.
- Authentication required for most endpoints; use JWT Bearer tokens.
- API is resilient to response format changes and provides detailed error messages.

---

For detailed request/response schemas, refer to the backend `schemas/` directory or OpenAPI docs if available.
