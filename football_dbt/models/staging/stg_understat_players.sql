with source as (
    select * from {{ source('raw', 'understat_players') }}
),

renamed as (
    select
        id as player_id,
        player_name,
        games,
        time as minutes,
        goals,
        assists,
        shots,
        key_passes,
        "xG" as xg,
        "xA" as xa,
        npg as non_penalty_goals,
        "npxG" as npxg,
        "xGChain" as xg_chain,
        "xGBuildup" as xg_buildup,
        position,
        team_title as team,
        yellow_cards,
        red_cards
    from source
)

select * from renamed
