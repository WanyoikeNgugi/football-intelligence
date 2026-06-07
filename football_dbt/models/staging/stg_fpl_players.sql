with source as (
    select * from {{ source('raw', 'fpl_players_raw') }}
),
renamed as (
    select 
        id as player_id,
        first_name,
        second_name,
        first_name || ' ' || second_name as player_name,
        web_name,
        element_type as position_id,
        case element_type
            when 1 then 'GKP'
            when 2 then 'DEF'
            when 3 then 'MID'
            when 4 then 'FWD'
        end as position,
        team as team_id,
        now_cost / 10.0 as price,
        total_points,
        minutes,
        goals_scored,
        assists,
        clean_sheets,
        goals_conceded,
        bonus,
        bps,
        ict_index,
        selected_by_percent,
        expected_goals,
        expected_assists,
        expected_goal_involvements,
        form,
        points_per_game,
        value_season
    from source

)
select * from renamed