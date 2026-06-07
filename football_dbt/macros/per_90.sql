{% macro per_90(stat_col, minutes_col) %}
    {{ stat_col }} / nullif({{ minutes_col }}, 0) * 90
{% endmacro %}
