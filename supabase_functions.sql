-- Function to check if a user exists in the auth.users table
CREATE OR REPLACE FUNCTION public.check_user_exists(user_id_param UUID)
RETURNS INT AS $$
DECLARE
  user_count INT;
BEGIN
  SELECT COUNT(*) INTO user_count FROM auth.users WHERE id = user_id_param;
  RETURN user_count;
END;
$$ LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public;

-- Grant access to the authenticated users
GRANT EXECUTE ON FUNCTION public.check_user_exists TO authenticated;
