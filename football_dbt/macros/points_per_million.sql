{% macro points_per_million(points_col, price_col) %}
    {{ points_col }} / nullif({{ price_col }}, 0)
{% endmacro %}
