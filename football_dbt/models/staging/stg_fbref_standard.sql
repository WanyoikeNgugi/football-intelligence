with source as (
    select * from {{ source('raw', 'fbref_standard') }}
),

renamed as (
    select
        player,
        team,
        pos                             as position,
        age,
        "Playing Time_MP"               as matches_played,
        "Playing Time_Starts"           as starts,
        "Playing Time_Min"              as minutes,
        "Playing Time_90s"              as nineties,
        "Performance_Gls"               as goals,
        "Performance_Ast"               as assists,
        "Performance_G+A"               as goals_assists,
        "Performance_G-PK"              as non_penalty_goals,
        "Performance_PK"                as penalties_scored,
        "Performance_CrdY"              as yellow_cards,
        "Performance_CrdR"              as red_cards,
        "Per 90 Minutes_Gls"            as goals_per90,
        "Per 90 Minutes_Ast"            as assists_per90,
        "Per 90 Minutes_G+A"            as goals_assists_per90
    from source
)

select * from renamed