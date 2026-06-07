-- Test that points per million is positive for players with minutes
select
    player_id,
    player_name,
    points_per_million
from {{ ref('mart_player_value') }}
where
    minutes > 0
    and points_per_million < 0
