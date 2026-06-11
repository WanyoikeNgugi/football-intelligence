with players as (
    select * from {{ ref('int_player_performance') }}
),

final as (
    select
        player_id,
        player_name,
        player_position,
        price,
        total_points,
        minutes,
        goals_scored,
        assists,
        clean_sheets,
        bonus,
        selected_by_percent,
        form,
        points_per_game,
        fpl_xg,
        fpl_xa,
        fpl_xgi,
        us_xg,
        us_xa,
        npxg,
        shots,
        -- value metrics
       {{ points_per_million('total_points', 'price') }} as points_per_million,  -- noqa
        us_xg / nullif(price, 0) as xg_per_million,
        fpl_xgi / nullif(price, 0) as xgi_per_million,
        -- efficiency metrics
        {{ per_90('total_points::float', 'minutes') }} as points_per90,  -- noqa
        {{ per_90('us_xg', 'minutes') }} as xg_per90,  -- noqa
        -- value flag
        coalesce(
            total_points / nullif(price, 0)
            > avg(total_points / nullif(price, 0)) over ()
            and selected_by_percent < 20,
            false
        ) as is_undervalued
    from players
    where minutes > 0
)

select * from final
