-- Step 3b: Flatten Book Mentions into Fact Table
{{ config(materialized='table') }}

SELECT
    VIDEO_ID,
    f.value::STRING AS BOOK_NAME,
    LOADED_AT AS PROCESSED_AT
FROM {{ ref('stg_youtube_transcripts') }}
WHERE book_title IS NOT NULL
LATERAL FLATTEN(input => BOOK_NAMES_ARRAY) f
