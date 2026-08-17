# 1. Introducción y objetivos

## 1.1 Visión general

**LostVault** es una plataforma independiente, con identidad visual de
la Universidad Tecnológica de Bolívar (UTB), concebida como un
**Marketplace para la gestión de objetos perdidos y encontrados dentro
de la universidad**.

El proyecto nace de un proceso actualmente manual: cuando un estudiante
pierde un objeto, debe contactar a la persona encargada de la gestión de
objetos perdidos o desplazarse físicamente para preguntar si el objeto
fue encontrado. De forma equivalente, un estudiante que encuentra un
objeto no dispone de un mecanismo sencillo para reportarlo sin pasar
físicamente por la oficina.

LostVault propone centralizar esta información en una plataforma digital
donde los objetos encontrados puedan publicarse y consultarse. El
sistema busca que la consulta del inventario no dependa del horario de
atención de la oficina ni de la disponibilidad inmediata de un
encargado.

La aplicación se plantea como **un sistema autónomo**, no como una
extensión de la aplicación oficial de la universidad. De acuerdo con la
documentación de contexto, LostVault no tiene integración, acoplamiento
ni relación de contención con sistemas externos en el alcance actual.

## 1.2 Propósito y problema que resuelve

El problema central de LostVault es la **gestión manual y poco accesible
de los objetos perdidos dentro de la universidad**.

Actualmente, la persona que pierde un objeto debe realizar acciones
como:

-   Contactar directamente a la persona encargada mediante mensajes.
-   Acercarse físicamente a la oficina de objetos perdidos.
-   Depender de que la oficina esté abierta y de que exista una persona
    disponible para atender la consulta.

Este proceso genera varias fricciones:

-   Se pierde tiempo en desplazamientos que pueden resultar
    innecesarios.
-   La consulta depende de la disponibilidad del encargado.
-   No existe un inventario visible y centralizado de los objetos
    encontrados.
-   La información depende de la memoria y disponibilidad de la persona
    encargada.
-   Un estudiante que encuentra un objeto no tiene una forma sencilla de
    reportarlo sin acudir físicamente a la oficina.

LostVault busca solucionar estas dificultades mediante un **inventario
digital centralizado**, accesible para consulta y publicación.

## 1.3 Alcance del sistema

El alcance actual de LostVault comprende una plataforma independiente
para centralizar objetos perdidos y encontrados.

Dentro del alcance se encuentran:

1.  **Publicación de objetos encontrados:** tanto los estudiantes como
    el encargado de la oficina pueden publicar objetos encontrados.
2.  **Información del objeto:** las publicaciones contemplan fotografía
    y descripción.
3.  **Búsqueda de objetos:** los estudiantes pueden buscar objetos
    publicados.
4.  **Filtrado:** los estudiantes pueden filtrar los objetos disponibles
    para facilitar la localización de una posible coincidencia.
5.  **Consulta independiente del horario de la oficina:** la información
    publicada puede consultarse sin necesidad de contactar
    presencialmente a un encargado.
6.  **Verificación para la entrega:** la propuesta contempla solicitar
    al reclamante una fotografía sosteniendo su cédula y carné
    estudiantil como mecanismo básico de identificación antes de la
    entrega presencial.

### Fuera del alcance actual

El proyecto establece explícitamente que LostVault:

-   No forma parte de la aplicación oficial de la universidad.
-   No depende de una integración con los sistemas oficiales de la
    universidad.
-   No tiene sistemas externos definidos en el nivel de contexto actual.
-   No reemplaza físicamente el proceso de entrega del objeto; la
    propuesta contempla una verificación previa y una entrega
    presencial.

## 1.4 Actores principales

El contexto C4 Nivel 1 del proyecto identifica tres actores principales:

### Estudiante que perdió un objeto

Utiliza LostVault para buscar y filtrar los objetos publicados, con el
objetivo de determinar si alguno corresponde al objeto que perdió.

**Necesidad principal:** consultar el inventario disponible sin tener
que contactar directamente a un encargado o desplazarse hasta la
oficina.

### Estudiante que encontró un objeto

Puede publicar un objeto encontrado adjuntando una fotografía y una
descripción.

**Necesidad principal:** disponer de una forma sencilla de reportar el
objeto y aumentar las posibilidades de que su propietario lo encuentre.

### Encargado de la oficina de objetos perdidos

Puede publicar en la plataforma los objetos que recibe físicamente en la
oficina.

**Necesidad principal:** centralizar la información y disminuir la carga
de responder manualmente consultas repetitivas.

> Un mismo estudiante puede desempeñar los roles de persona que pierde
> un objeto y persona que encuentra un objeto en momentos diferentes. Se
> representan como actores separados porque sus interacciones con el
> sistema son distintas.

## 1.5 Objetivos del sistema

A partir de la ficha del problema, el contexto y los aspectos de calidad
declarados, los objetivos principales de LostVault son:

1.  **Centralizar la información** de los objetos encontrados en un
    único inventario digital.
2.  **Hacer visible el inventario** para que los estudiantes puedan
    consultar qué objetos han sido reportados.
3.  **Facilitar la búsqueda y filtrado** de objetos perdidos mediante
    una experiencia similar a un Marketplace.
4.  **Permitir que los estudiantes reporten objetos encontrados** sin
    necesidad de llevarlos inicialmente a la oficina.
5.  **Permitir que el encargado publique los objetos** que recibe
    físicamente.
6.  **Reducir desplazamientos innecesarios** hacia la oficina de objetos
    perdidos.
7.  **Reducir la dependencia de mensajes directos** al encargado para
    consultas simples.
8.  **Mantener la consulta disponible fuera del horario de atención**,
    evitando que la disponibilidad de la información dependa de la
    presencia de una persona.
9.  **Aumentar la seguridad del proceso de reclamación**, incorporando
    una verificación básica de identidad antes de la entrega.
10. **Mantener una solución independiente** de los sistemas oficiales de
    la universidad dentro del alcance actual.

## 1.6 Objetivos de calidad prioritarios

Los documentos del proyecto declaran cuatro atributos de calidad:
**disponibilidad, usabilidad, seguridad y rendimiento**. La prioridad
establecida por el equipo coloca la disponibilidad en primer lugar,
seguida por usabilidad, seguridad y rendimiento.

### 1. Disponibilidad --- Prioridad máxima

La **disponibilidad** es el atributo de calidad prioritario de LostVault
porque responde directamente al problema que origina el proyecto.

El proceso actual depende de que la oficina esté abierta y de que una
persona pueda atender al estudiante. LostVault busca eliminar esa
dependencia para la consulta de información.

**Objetivo:** que la plataforma permita consultar el inventario sin
depender del horario de la oficina física ni de la presencia de un
encargado.

**Escenario de calidad definido:**

-   Fuente: estudiante.
-   Estímulo: consulta un objeto perdido fuera del horario de atención.
-   Artefacto: módulo de consulta/búsqueda.
-   Entorno: operación normal fuera del horario de oficina.
-   Respuesta: el sistema responde sin intervención humana.
-   Medida: **99 % de disponibilidad mensual**, con una inactividad no
    programada inferior a **7 horas por mes**.

### 2. Usabilidad

La **usabilidad** ocupa la segunda posición porque la plataforma está
dirigida principalmente a estudiantes y debe ofrecer una interacción
sencilla, familiar y sin necesidad de capacitación previa.

El proyecto utiliza como referencia conceptual la experiencia de
plataformas tipo Marketplace.

**Objetivo:** permitir que un usuario nuevo pueda publicar o consultar
información de forma intuitiva y con poca fricción.

**Escenario de calidad definido:**

-   Fuente: estudiante que utiliza la plataforma por primera vez.
-   Estímulo: intenta publicar un objeto encontrado.
-   Artefacto: formulario de publicación.
-   Entorno: uso normal y sin capacitación previa.
-   Respuesta: completa la publicación sin ayuda externa.
-   Medida: al menos **90 % de los usuarios nuevos** debe completar una
    publicación en menos de **3 minutos**.

### 3. Seguridad

La **seguridad** es prioritaria en el momento de reclamar y entregar un
objeto. El proyecto propone utilizar la fotografía del reclamante
sosteniendo su cédula y carné estudiantil como mecanismo básico de
verificación de identidad.

Este atributo también tiene una importancia especial porque el proyecto
identifica el tratamiento de datos personales como una restricción
legal. La documentación señala que el manejo de cédula y carné
estudiantil está sujeto a la **Ley 1581 de 2012 de Colombia**, por lo
que la información debe tratarse de manera adecuada, almacenarse de
forma segura y utilizarse de manera limitada.

**Objetivo:** evitar que una reclamación sin una verificación de
identidad válida permita la entrega del objeto.

**Escenario de calidad definido:**

-   Fuente: usuario no autorizado.
-   Estímulo: intenta reclamar un objeto que no le pertenece.
-   Artefacto: módulo de verificación de identidad.
-   Entorno: operación normal.
-   Respuesta: el sistema rechaza la entrega y marca el intento para
    revisión.
-   Medida: **100 % de los intentos sin verificación válida** deben ser
    bloqueados automáticamente.

### 4. Rendimiento

El **rendimiento** busca garantizar que las búsquedas sean
suficientemente rápidas, incluso durante periodos de alta concurrencia.

La rapidez es relevante porque uno de los objetivos del sistema es
reducir la fricción del proceso actual y ofrecer una consulta inmediata
del inventario.

**Objetivo:** responder rápidamente a las búsquedas aun bajo una carga
elevada de usuarios.

**Escenario de calidad definido:**

-   Fuente: estudiante.
-   Estímulo: realiza una búsqueda por palabra clave.
-   Artefacto: módulo de búsqueda.
-   Entorno: hora pico con aproximadamente 200 usuarios concurrentes.
-   Respuesta: el sistema retorna los resultados.
-   Medida: **95 % de las búsquedas** deben responder en **2 segundos o
    menos (p95)** con aproximadamente **200 usuarios concurrentes**.

### Resumen de prioridades

  -----------------------------------------------------------------------
  Prioridad               Atributo                Motivo
  ----------------------- ----------------------- -----------------------
  **1**                   **Disponibilidad**      Elimina la dependencia
                                                  del horario y presencia
                                                  física de la oficina,
                                                  que constituye el
                                                  problema central.

  **2**                   **Usabilidad**          La solución está
                                                  dirigida principalmente
                                                  a estudiantes y debe
                                                  poder utilizarse sin
                                                  capacitación.

  **3**                   **Seguridad**           Protege el proceso de
                                                  reclamación y el
                                                  tratamiento de
                                                  información personal.

  **4**                   **Rendimiento**         Permite que la consulta
                                                  del inventario sea
                                                  rápida incluso en horas
                                                  pico.
  -----------------------------------------------------------------------

## 1.7 Stakeholders y sus intereses

  -----------------------------------------------------------------------
  Stakeholder             Relación con LostVault  Intereses / necesidades
  ----------------------- ----------------------- -----------------------
  **Estudiante que perdió Usuario de consulta y   Encontrar rápidamente
  un objeto**             búsqueda.               su objeto, consultar el
                                                  inventario sin
                                                  desplazarse y no
                                                  depender de mensajes al
                                                  encargado.

  **Estudiante que        Usuario que puede       Reportar fácilmente el
  encontró un objeto**    publicar un objeto      objeto y facilitar que
                          encontrado.             su propietario lo
                                                  localice.

  **Encargado de la       Usuario que publica los Centralizar la
  oficina de objetos      objetos recibidos       información, reducir
  perdidos**              físicamente.            consultas repetitivas y
                                                  facilitar la gestión de
                                                  los objetos.

  **Propietario legítimo  Persona que finalmente  Recuperar su
  del objeto**            reclama el objeto.      pertenencia mediante un
                                                  proceso de
                                                  identificación que
                                                  reduzca el riesgo de
                                                  una entrega incorrecta.

  **Equipo de             Responsable de          Cumplir el alcance del
  desarrollo**            construir y mantener la proyecto, las
                          solución.               restricciones del
                                                  semestre y los
                                                  objetivos de calidad.

  **Universidad           Contexto institucional  Que la solución respete
  Tecnológica de Bolívar  del problema y          las restricciones
  (UTB)**                 referencia de identidad institucionales y
                          visual.                 legales aplicables,
                                                  especialmente si
                                                  llegara a desplegarse
                                                  públicamente.
  -----------------------------------------------------------------------

### Intereses compartidos

Los stakeholders tienen como intereses comunes:

-   **Accesibilidad:** poder consultar información sin depender de la
    atención presencial.
-   **Rapidez:** reducir el tiempo necesario para buscar o publicar un
    objeto.
-   **Confiabilidad:** disponer de un inventario centralizado y
    actualizado.
-   **Seguridad:** evitar entregas indebidas y proteger los datos
    utilizados para la verificación.
-   **Simplicidad:** que la plataforma pueda utilizarse sin
    conocimientos técnicos especializados.

## 1.8 Restricciones relevantes para los objetivos

Los objetivos de LostVault deben interpretarse dentro de las
restricciones identificadas en el proyecto:

-   El sistema se desarrolla como **aplicación independiente** con
    identidad visual UTB.
-   No se ha definido ni confirmado una integración con los sistemas
    oficiales de la universidad.
-   El equipo debe apoyarse en **servicios de nivel gratuito** para
    alojamiento e infraestructura, lo que limita los recursos
    disponibles.
-   El equipo está compuesto por **cuatro personas** con carga académica
    simultánea.
-   El proyecto tiene un **plazo fijo correspondiente al semestre
    académico**.
-   El repositorio debe alojarse en la organización institucional
    **ISCOUTB** de GitHub.
-   El sistema debe considerar las obligaciones asociadas al tratamiento
    de **datos personales**, especialmente cédula y carné estudiantil.
-   El uso de la identidad visual de la UTB en una aplicación que no es
    oficial puede requerir autorización antes de un despliegue público
    real.

Estas restricciones son importantes para la arquitectura porque
condicionan la infraestructura disponible, el alcance que puede
implementarse durante el semestre y las decisiones relacionadas con
seguridad y despliegue.

## 1.9 Resumen

LostVault tiene como objetivo **digitalizar y centralizar la gestión de
objetos perdidos dentro de la universidad**, proporcionando una
plataforma independiente en la que estudiantes y el encargado de la
oficina puedan publicar objetos encontrados y en la que los estudiantes
puedan buscarlos y filtrarlos.

El principal valor arquitectónico del sistema está en **desacoplar la
consulta de información del horario y disponibilidad de la oficina
física**. Por ello, la disponibilidad constituye el atributo de calidad
prioritario. A esta se suman usabilidad, seguridad y rendimiento, que
permiten que la solución sea práctica para los estudiantes, segura
durante la reclamación y suficientemente rápida durante la consulta.

En conjunto, LostVault busca transformar un proceso manual, dependiente
de personas y de la atención presencial, en un proceso **centralizado,
accesible, sencillo y seguro**, manteniendo actualmente una arquitectura
independiente de los sistemas oficiales de la universidad.
