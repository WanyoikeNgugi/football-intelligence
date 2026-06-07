with source as (
    select * from {{ source('raw', 'fbref_standard') }}
),

renamed as (
    select
        player,
        team,
        pos as player_position,
        age,
        "Playing Time_MP" as matches_played,
        "Playing Time_Starts" as matches_started,
        "Playing Time_Min" as minutes_played,
        "Playing Time_90s" as nineties,
        "Performance_Gls" as goals,
        "Performance_Ast" as assists,
        "Performance_G+A" as goals_assists, -- noqa: RF05
        "Performance_G-PK" as non_penalty_goals, -- noqa: RF05
        "Performance_PK" as penalties_scored,
        "Performance_CrdY" as yellow_cards,
        "Performance_CrdR" as red_cards,
        "Per 90 Minutes_Gls" as goals_per90,
        "Per 90 Minutes_Ast" as assists_per90,
        "Per 90 Minutes_G+A" as goals_assists_per90 -- noqa: RF05
    from source
)

select * from renamed
