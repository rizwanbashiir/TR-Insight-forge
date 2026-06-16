# Billing and Roles Implementation Walkthrough

The architecture has been successfully updated to meet your new billing, role limit, and super admin requirements!

## What was Changed

1. **Super Admin Role**: 
   - A `super_admin` role was added to the `UserRole` enum in the database.
   - On server startup, the `PREDEFINED_ADMIN_EMAILS` (defined in your `settings.py`) are now automatically seeded as `super_admin`.

2. **Organization User Management**:
   - `POST /organizations/users`: Allows an Organization Admin (or Super Admin) to add a user to their organization. 
   - Limits are strictly enforced here:
     - **Free**: Only 1 user.
     - **Pro**: Up to 3 users (enforces strict unique roles if they add "admin", "analyst", and "viewer").
     - **Enterprise**: Unlimited users.
   - When a user is added, a temporary password and a password reset token are generated.

3. **Password Reset Flow**:
   - `POST /auth/set-password`: Allows users to set their password using the reset token sent to their email.
   - `POST /auth/forgot-password`: Triggers a new reset link for users who forgot their password.
   - `POST /organizations/users/{user_id}/resend-invite`: Allows admins to resend the invite link to a user if they haven't changed their initial temporary password yet.
   - *Note: Since we are not currently connected to an SMTP server, the emails with the links are printed to your terminal console for testing.*

4. **Super Admin Features**:
   - `POST /superadmin/organizations`: Enables `super_admin`s to manually create Enterprise organizations.
   - `GET /superadmin/dashboard`: Returns an aggregated overview of all organizations, their current active subscription plans (free, pro, enterprise), and user counts.

## How to Test It in Postman

**1. Log in as Super Admin:**
Use `POST /auth/login` with your `admin@example.com` (or whatever you set in `settings.py`) and password `AdminPassword123!`. Grab the `access_token`.

**2. Test the Dashboard:**
- Method: `GET /superadmin/dashboard`
- Header: `Authorization: Bearer <your_access_token>`

**3. Create an Enterprise Org:**
- Method: `POST /superadmin/organizations`
- Header: `Authorization: Bearer <your_access_token>`
- Body: 
  ```json
  {
    "name": "Acme Corp",
    "admin_name": "John Doe",
    "admin_email": "john.enterprise@example.com"
  }
  ```

**4. Test Pro Plan Limits:**
- Register a new user, test upgrading them to "pro" via `/billing/test-upgrade`.
- Log in as them and try hitting `POST /organizations/users` to invite a viewer:
  ```json
  {
      "name": "Jane Viewer",
      "email": "jane@example.com",
      "role": "viewer"
  }
  ```
- Check your backend terminal to see the "Email Sent" log containing the reset token link!
