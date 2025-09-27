-- Fix Supabase RLS Security Issues
-- Enable Row Level Security on all public tables

-- 1. Enable RLS on enhanced_analytics table
ALTER TABLE public.enhanced_analytics ENABLE ROW LEVEL SECURITY;

-- 2. Enable RLS on all other public tables
ALTER TABLE public."user" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.script ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.systemlogs ENABLE ROW LEVEL SECURITY;

-- 3. Create RLS policies for enhanced_analytics
CREATE POLICY "Users can view their own analytics" ON public.enhanced_analytics
    FOR SELECT USING (auth.uid()::text = user_id OR user_id IS NULL);

CREATE POLICY "Users can insert their own analytics" ON public.enhanced_analytics
    FOR INSERT WITH CHECK (auth.uid()::text = user_id OR user_id IS NULL);

CREATE POLICY "Service role can manage all analytics" ON public.enhanced_analytics
    FOR ALL USING (auth.role() = 'service_role');

-- 4. Create RLS policies for user table
CREATE POLICY "Users can view their own profile" ON public."user"
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can update their own profile" ON public."user"
    FOR UPDATE USING (auth.uid()::text = user_id);

CREATE POLICY "Service role can manage all users" ON public."user"
    FOR ALL USING (auth.role() = 'service_role');

-- 5. Create RLS policies for content table
CREATE POLICY "Users can view all content" ON public.content
    FOR SELECT USING (true);

CREATE POLICY "Users can insert their own content" ON public.content
    FOR INSERT WITH CHECK (auth.uid()::text = uploader_id);

CREATE POLICY "Users can update their own content" ON public.content
    FOR UPDATE USING (auth.uid()::text = uploader_id);

CREATE POLICY "Service role can manage all content" ON public.content
    FOR ALL USING (auth.role() = 'service_role');

-- 6. Create RLS policies for script table
CREATE POLICY "Users can view all scripts" ON public.script
    FOR SELECT USING (true);

CREATE POLICY "Users can insert their own scripts" ON public.script
    FOR INSERT WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update their own scripts" ON public.script
    FOR UPDATE USING (auth.uid()::text = user_id);

CREATE POLICY "Service role can manage all scripts" ON public.script
    FOR ALL USING (auth.role() = 'service_role');

-- 7. Create RLS policies for feedback table
CREATE POLICY "Users can view all feedback" ON public.feedback
    FOR SELECT USING (true);

CREATE POLICY "Users can insert their own feedback" ON public.feedback
    FOR INSERT WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update their own feedback" ON public.feedback
    FOR UPDATE USING (auth.uid()::text = user_id);

CREATE POLICY "Service role can manage all feedback" ON public.feedback
    FOR ALL USING (auth.role() = 'service_role');

-- 8. Create RLS policies for analytics table
CREATE POLICY "Users can view their own analytics data" ON public.analytics
    FOR SELECT USING (auth.uid()::text = user_id OR user_id IS NULL);

CREATE POLICY "Users can insert their own analytics data" ON public.analytics
    FOR INSERT WITH CHECK (auth.uid()::text = user_id OR user_id IS NULL);

CREATE POLICY "Service role can manage all analytics data" ON public.analytics
    FOR ALL USING (auth.role() = 'service_role');

-- 9. Create RLS policies for systemlogs table
CREATE POLICY "Only service role can access system logs" ON public.systemlogs
    FOR ALL USING (auth.role() = 'service_role');

-- 10. Grant necessary permissions to authenticated users
GRANT SELECT ON public.content TO authenticated;
GRANT SELECT ON public.script TO authenticated;
GRANT SELECT ON public.feedback TO authenticated;
GRANT SELECT, INSERT ON public.analytics TO authenticated;
GRANT SELECT, INSERT ON public.enhanced_analytics TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public."user" TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.content TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.script TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.feedback TO authenticated;

-- 11. Grant full access to service role
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;

-- 12. Create function to bypass RLS for service operations
CREATE OR REPLACE FUNCTION public.bypass_rls_for_service()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- This function allows service operations to bypass RLS
    -- Only callable by service_role
    IF auth.role() != 'service_role' THEN
        RAISE EXCEPTION 'Access denied';
    END IF;
END;
$$;