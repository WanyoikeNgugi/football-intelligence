with source as (
    select * from {{ source('raw', 'fpl_teams') }}
),

renamed as (
    select
        id as team_id,
        name as team_name,
        short_name as team_short_name,
        strength,
        strength_overall_home,
        strength_overall_away,
        strength_attack_home,
        strength_attack_away,
        strength_defence_home,
        strength_defence_away
    from source
)

select * from renamed
