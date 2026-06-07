with gw as (
    select * from {{ ref('stg_fpl_gw') }}
),

players as (
    select * from {{ ref('stg_fpl_players') }}
),

joined as (
    select
        gw.player_id,
        gw.gw,
        gw.fixture_id,
        gw.total_points,
        gw.minutes,
        gw.goals_scored,
        gw.assists,
        gw.clean_sheets,
        gw.bonus,
        gw.expected_goals,
        gw.expected_assists,
        gw.was_home,
        gw.team,
        gw.position,
        gw.name                     as player_name,
        --gw.multiplier,
        players.price,
        players.selected_by_percent,
        players.form
    from gw
    left join players
        on gw.player_id = players.player_id
)

select * from joined