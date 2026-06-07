with source as (
    select * from {{ source('raw', 'vaastav_merged_gw') }}
),

renamed as (
    select
        name as player_name,
        position,
        team,
        season,
        "GW" as gw,
        total_points,
        minutes,
        goals_scored,
        assists,
        clean_sheets,
        bonus,
        bps,
        ict_index,
        selected,
        value,
        transfers_in,
        transfers_out,
        was_home,
        opponent_team,
        expected_goals,
        expected_assists,
        expected_goal_involvements
    from source
)

select * from renamed
