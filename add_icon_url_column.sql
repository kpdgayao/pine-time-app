-- Add icon_url column to badges table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name='badges' AND column_name='icon_url'
    ) THEN
        ALTER TABLE badges ADD COLUMN icon_url VARCHAR;
        
        -- Update existing records with a default value
        UPDATE badges SET icon_url = '/static/images/badges/default_badge.png';
    END IF;
END $$;
