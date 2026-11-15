# Proyecto_analitica_3

## Entrega AE3: preparación y análisis de salarios

### Preguntas abordadas

- ¿Cómo se comparan los salarios en USD por experiencia, modalidad de trabajo y tamaño de empresa?
- ¿Cuántos registros hay por año de referencia, experiencia y tipo de empleo?
- ¿Qué cargos tienen más registros y cuál es su salario mediano?
- ¿Cómo cambia la mediana salarial entre los años disponibles?

### Transformaciones y controles

Se conservaron las 3.755 filas del dataset original y se creó un DataFrame preparado de 16 columnas. Se cambiaron los códigos de experiencia, tipo de empleo y tamaño de empresa por etiquetas legibles, y se derivaron cinco variables: `remote_work_mode`, `experience_level_order`, `company_size_order`, `work_location_relation` y `salary_usd_quartile`.

No se encontraron valores nulos. Se conservaron las 1.171 filas exactamente repetidas (31,2 %) porque no hay un identificador para determinar si son errores o registros distintos con valores iguales. El notebook documenta la comparación antes/después y la sensibilidad de excluirlas: la mediana pasa de USD 135.000 a USD 130.000 y el promedio de USD 137.570,39 a USD 133.409,28. Las comparaciones salariales usan `salary_in_usd`. Se usa `work_year` como año de referencia porque el dataset no proporciona una fecha exacta de pago.

### Archivos generados

- Notebook ejecutado: `src/AE3/Semana_3_AE3.ipynb`
- Script de procesamiento: `src/AE3/procesar_dataset.py`
- Dataset original: `src/AE3/datos/demo-salaries-original.csv`
- Dataset preparado: `src/AE3/datos/demo-salaries-preparado.csv`
- Comparación antes/después y resultados CSV: `src/AE3/resultados/`

El notebook genera el dataset preparado, cuatro tablas CSV, `comparacion_antes_despues.csv` y `resumen_dataframe.txt`. Las tablas contienen conteos por combinación o cargo y estadísticas salariales para responder las preguntas.

### Ejecución

Desde la raíz del proyecto, ejecuta el script:

```bash
python src/AE3/procesar_dataset.py