{# Division that returns null instead of failing when the denominator is zero. #}
{% macro razao_segura(numerador, denominador) %}
    {{ numerador }} / nullif({{ denominador }}, 0)
{% endmacro %}
