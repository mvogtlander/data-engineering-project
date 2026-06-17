{% macro get_vendor_names(vendor_id) %}
    case
        when vendor_id = 1
            then 'Marc Voggie'
        when vendor_id = 2
            then 'Isabel de Wit'
        when vendor_id = 4
            then 'Onbekend'
{% endmacro %}
