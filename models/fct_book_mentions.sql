-- Step 3b: Flatten Book Mentions into Fact Table
{{ config(materialized='table') }}

SELECT
    VIDEO_ID,
    f.value::STRING AS BOOK_NAME,
    LOADED_AT AS PROCESSED_AT
FROM {{ ref('STG_YOUTUBE_TRANSCRIPTS') }}
LATERAL FLATTEN(input => BOOK_NAMES_ARRAY) f
