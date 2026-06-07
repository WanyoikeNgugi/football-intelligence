with gw as (
    select * from {{ ref('stg_vaastav_gw') }}
),

aggregated as (
    select
        player_name,
        position,
        season,
        count(gw)                           as games_played,
        sum(total_points)                   as total_points,
        avg(total_points)                   as avg_points_per_gw,
        sum(minutes)                        as total_minutes,
        sum(goals_scored)                   as total_goals,
        sum(assists)                        as total_assists,
        sum(clean_sheets)                   as total_clean_sheets,
        sum(bonus)                          as total_bonus,
        avg(ict_index)                      as avg_ict_index,
        avg(value) / 10.0                   as avg_price,
        sum(transfers_in)                   as total_transfers_in,
        sum(transfers_out)                  as total_transfers_out,
        avg(expected_goals)                 as avg_xg,
        avg(expected_assists)               as avg_xa,
        avg(expected_goal_involvements)     as avg_xgi,
        sum(case when was_home then total_points else 0 end) as home_points,
        sum(case when not was_home then total_points else 0 end) as away_points
    from gw
    group by player_name, position, season
)

select * from aggregated