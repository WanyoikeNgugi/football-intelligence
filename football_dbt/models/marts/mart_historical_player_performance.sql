with current as (
    select * from {{ ref('mart_player_points') }}
),

historical as (
    select * from {{ ref('int_vaastav_player_history') }}
),

historical_aggregated as (
    select
        player_name,
        position,
        avg(avg_points_per_gw) as career_avg_points_per_gw,
        avg(avg_xg) as career_avg_xg,
        avg(avg_xa) as career_avg_xa,
        avg(avg_xgi) as career_avg_xgi,
        avg(avg_ict_index) as career_avg_ict,
        sum(total_goals) as career_goals,
        sum(total_assists) as career_assists,
        sum(total_clean_sheets) as career_clean_sheets,
        count(season) as seasons_played
    from historical
    group by player_name, position
),

final as (
    select
        c.player_id,
        c.player_name,
        c.position,
        c.team,
        c.price,
        c.total_points,
        c.avg_points_per_gw,
        c.total_goals,
        c.total_assists,
        c.total_clean_sheets,
        c.avg_xg,
        c.avg_xa,
        c.home_points,
        c.away_points,
        c.avg_home_points,
        c.avg_away_points,
        h.career_avg_points_per_gw,
        h.career_avg_xg,
        h.career_avg_xa,
        h.career_avg_xgi,
        h.career_avg_ict,
        h.career_goals,
        h.career_assists,
        h.career_clean_sheets,
        h.seasons_played
    from current as c
    left join historical_aggregated as h
        on c.player_name = h.player_name
)

select * from final
