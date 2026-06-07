with source as (
    select * from {{ source('raw', 'vaastav_fixtures') }}
),

renamed as (
    select
        id,
        team_h,
        team_a,
        team_h_score,
        team_a_score,
        kickoff_time,
        season
    from source
)

select * from renamed
