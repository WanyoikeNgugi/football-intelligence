-- Test that all player prices are positive
select
    player_id,
    player_name,
    price
from {{ ref('mart_player_value') }}
where price <= 0
