with source as (
    select * from {{ source('raw', 'fpl_gw') }}
),

renamed as (
    select
        element as player_id,
        fixture as fixture_id,
        round as gw,
        total_points,
        minutes,
        goals_scored,
        assists,
        clean_sheets,
        bonus,
        bps,
        expected_goals,
        expected_assists,
        was_home,
        team,
        name,
        position
    from source
)

select * from renamed
