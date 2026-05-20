-- 002: user_profiles 增加 nickname 字段
ALTER TABLE public.user_profiles ADD COLUMN IF NOT EXISTS nickname TEXT;
