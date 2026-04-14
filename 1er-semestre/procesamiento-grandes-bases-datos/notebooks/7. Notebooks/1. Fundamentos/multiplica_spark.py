import findspark
findspark.init()
from pyspark import SparkContext

# Crea un contexto Spark
sc = SparkContext("local", "EjemploRDD")
#sc=  SparkContext(appName="MyAppName")

# Crea un RDD a partir de una lista
rdd = sc.parallelize([1, 2, 3, 4, 5])

# Realiza una transformación: multiplica cada elemento por 2
rdd_multiplicado = rdd.map(lambda x: x * 2)

# Realiza una acción: muestra los resultados
print(rdd_multiplicado.collect())
#rdd_multiplicado.collect()
# Detén el contexto Spark
# sc.stop()