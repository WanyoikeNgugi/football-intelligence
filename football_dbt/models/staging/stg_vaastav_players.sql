with source as (
    select * from {{ source('raw', 'vaastav_players_raw') }}
), renamed as (
    select 
        first_name,
        second_name,
        goals_scored,
        assists, total_points,
        minutes,
        now_cost,
        element_type,
        season
    from 
        source
)
select * from renamed