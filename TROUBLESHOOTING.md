# Interview App - Supabase Integration Troubleshooting

## Common Issues and Solutions

If your interviews are not being saved to the database despite tables being created, try these solutions:

### 1. Check Authentication Status

The most common reason for data not being saved is authentication issues:

- **Session Mismatch**: The user session token might be invalid or expired
- **User ID Format**: Make sure the user ID is properly formatted as a valid UUID

**Diagnostic Tool**: Navigate to `/auth-diagnostic` to check the current authentication status.

### 2. Run the Complete SQL Setup

Make sure all required SQL has been executed, including:

- Tables creation (interviews, conversation_messages, feedback)
- Row Level Security (RLS) policies
- Helper functions like `check_user_exists`

**Setup Files**:
- `/supabase_setup.sql` - Main tables and RLS policies
- `/supabase_functions.sql` - Helper functions
- `/supabase_diagnostic.sql` - Diagnostic tables and tools

### 3. Check RLS Policies

Row Level Security policies can prevent data insertion:

```sql
-- Check if RLS is blocking inserts for your user ID
-- Run this in SQL Editor with your user ID:
SELECT auth.uid() as current_user_id;
```

### 4. Verify Browser Console for Errors

Check the browser console during the interview save process for detailed error messages:
1. Open Developer Tools (F12 or right-click > Inspect)
2. Go to the Console tab
3. Look for errors containing "saveInterviewData", "Supabase", or "insert"

### 5. Test Direct Database Insert

Run a direct insert test using the Auth Diagnostic tool:
1. Navigate to `/auth-diagnostic`
2. Click "Check Auth Status" to verify your session
3. Click "Test Direct Insert" to attempt a direct database insert

### 6. Database Schema Issues

Ensure your Supabase database matches the expected schema:
- Table names should be exactly: `interviews`, `conversation_messages`, `feedback`
- Column names and types should match the schema in `supabase_setup.sql`
- Foreign key constraints should be properly set up

### 7. Clear Browser Data

Try clearing your browser cache and cookies:
1. Sign out of the application
2. Clear browser cache and cookies
3. Sign in again

### 8. Common Error Codes

| Error Code | Description | Solution |
|------------|-------------|----------|
| 23503 | Foreign key violation | User ID doesn't exist in auth.users table |
| 42P01 | Relation does not exist | Tables haven't been created properly |
| PGRST301 | RLS policy error | Review RLS policies in setup SQL |

## Contact Support

If you're still experiencing issues after trying these steps, please contact our support team with:
1. Screenshots of any error messages
2. Output from the Auth Diagnostic tool
3. Output from the Database Diagnostic tool
