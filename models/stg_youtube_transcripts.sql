-- Step 1: Staging View (JSON Variant Parsing)
{{ config(materialized='view') }}

SELECT
    PAYLOAD:video_id::STRING AS VIDEO_ID,
    PAYLOAD:cleaned_text::STRING AS CLEANED_TEXT,
    PAYLOAD:tech_terms AS TECH_TERMS_ARRAY,
    PAYLOAD:book_names AS BOOK_NAMES_ARRAY,
    LOADED_AT
FROM CJF4XV.RAW_TRANSCRIPTS
