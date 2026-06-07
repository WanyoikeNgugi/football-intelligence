with fpl as (
    select * from {{ ref('stg_fpl_players') }}
),

understat as (
    select * from {{ ref('stg_understat_players') }}
),

fbref as (
    select * from {{ ref('stg_fbref_standard') }}
),

fbref_agg as (
    select
        player,
        sum(goals) as goals,
        sum(assists) as assists,
        sum(goals_assists) as goals_assists,
        sum(non_penalty_goals) as non_penalty_goals,
        sum(matches_played) as total_matches,
        sum(matches_started) as total_starts,
        sum(minutes) as total_minutes,
        avg(goals_per90) as goals_per90,
        avg(assists_per90) as assists_per90,
        avg(goals_assists_per90) as goals_assists_per90
    from fbref
    group by player
),

joined as (
    select
        fpl.player_id,
        fpl.player_name,
        fpl.player_position,
        fpl.team_id,
        fpl.price,
        fpl.total_points,
        fpl.minutes,
        fpl.goals_scored,
        fpl.assists,
        fpl.clean_sheets,
        fpl.bonus,
        fpl.bps,
        fpl.ict_index,
        fpl.selected_by_percent,
        fpl.expected_goals as fpl_xg,
        fpl.expected_assists as fpl_xa,
        fpl.expected_goal_involvements as fpl_xgi,
        fpl.form,
        fpl.points_per_game,
        fpl.value_season,
        understat.xg as us_xg,
        understat.xa as us_xa,
        understat.xg_chain,
        understat.xg_buildup,
        understat.shots,
        understat.key_passes,
        understat.npxg,
        fbref.goals_per90,
        fbref.assists_per90,
        fbref.goals_assists_per90,
        fbref.total_starts
    from fpl
    left join understat
        on fpl.player_name = understat.player_name
    left join fbref_agg as fbref
        on fpl.player_name = fbref.player
)

select * from joined
