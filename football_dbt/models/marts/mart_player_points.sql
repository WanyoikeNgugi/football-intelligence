with gw as (
    select * from {{ ref('int_manager_picks') }}
),

aggregated as (
    select
        player_id,
        player_name,
        position,
        team,
        price,
        selected_by_percent,
        count(gw) as games_played,
        sum(total_points) as total_points,
        avg(total_points) as avg_points_per_gw,
        sum(minutes) as total_minutes,
        avg(minutes) as avg_minutes,
        sum(goals_scored) as total_goals,
        sum(assists) as total_assists,
        sum(clean_sheets) as total_clean_sheets,
        sum(bonus) as total_bonus,
        avg(expected_goals) as avg_xg,
        avg(expected_assists) as avg_xa,
        sum(case when was_home then total_points else 0 end) as home_points,
        sum(case when not was_home then total_points else 0 end) as away_points,
        avg(case when was_home then total_points end)
        as avg_home_points,
        avg(case when not was_home then total_points end)
        as avg_away_points
    from gw
    group by
        player_id,
        player_name,
        position,
        team,
        price,
        selected_by_percent
)

select * from aggregated
