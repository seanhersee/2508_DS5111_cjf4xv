-- Step 3a: Flatten Tech Terms into Fact Table
{{ config(materialized='table') }}

SELECT
    VIDEO_ID,
    f.value::STRING AS TECH_TERM,
    LOADED_AT AS PROCESSED_AT
FROM {{ ref('STG_YOUTUBE_TRANSCRIPTS') }}
LATERAL FLATTEN(input => TECH_TERMS_ARRAY) f
