# Orbit --- Personal Intelligence Agent

> Un agente personal que busca información útil en la web, la filtra
> según los intereses del usuario y publica un briefing periódico en
> Discord.

**Estado:** definición del MVP\
**Objetivo de hoy:** completar un flujo funcional de búsqueda →
selección/resumen → publicación en Discord y dejarlo ejecutándose
mediante un schedule gratuito.\
**Idioma inicial:** español\
**Zona horaria:** `America/Bogota`

------------------------------------------------------------------------

## 1. Visión del producto

Orbit no debe quedarse en un simple agregador de enlaces. Su objetivo es
reducir el tiempo que una persona invierte buscando información y
ayudarla a detectar oportunidades relevantes.

### Categorías previstas

-   **Tech Radar:** noticias de IA, programación, software, APIs y
    agentes.
-   **Scholarships:** becas, intercambios, pasantías y convocatorias
    académicas.
-   **Hackathons:** hackatones, competencias y eventos para
    desarrolladores.
-   **Opportunities:** proyectos, convocatorias y otras oportunidades
    relevantes.

### Diferenciadores a desarrollar gradualmente

1.  Personalización por intereses, nivel académico, país y objetivos.
2.  Enlaces a las fuentes originales y fechas visibles.
3.  Deduplicación para no publicar la misma noticia repetidamente.
4.  Extracción de fechas límite y requisitos cuando sean verificables.
5.  Priorización de oportunidades según la elegibilidad del usuario.
6.  Historial de publicaciones y posibilidad de marcar elementos como
    relevantes.

No se debe afirmar que una persona es elegible para una beca sin
comprobar los requisitos de la fuente. Si no hay suficiente información,
Orbit debe indicar que la elegibilidad está pendiente de verificación.

------------------------------------------------------------------------

## 2. Alcance del MVP

### Meta de la primera versión

Cada cierto tiempo, un proceso automático debe:

1.  Consultar la web en busca de información reciente.
2.  Normalizar los resultados.
3.  Eliminar duplicados.
4.  Filtrar los resultados relacionados con los intereses configurados.
5.  Usar un modelo de lenguaje para seleccionar y resumir los
    resultados.
6.  Publicar un briefing con enlaces a las fuentes en un canal de
    Discord.
7.  Terminar la ejecución sin requerir que el usuario abra el proyecto o
    escriba un comando.

### Fuera del alcance de hoy

-   Sistema multiusuario con perfiles individuales.
-   Base de datos y panel web.
-   Comandos slash como `/briefing` o `/preferences`.
-   Verificación automática completa de requisitos de becas.
-   Agentes múltiples, RAG, vector database o LangGraph.
-   Scraping indiscriminado de sitios web.
-   Garantía de que cada convocatoria sigue abierta.

El MVP debe demostrar primero que la automatización funciona de extremo
a extremo.

------------------------------------------------------------------------

## 3. Decisión importante: cómo publicar en Discord

Hay dos alternativas. No conviene mezclarlas en la primera
implementación.

### Opción recomendada hoy: GitHub Actions + Discord Webhook

GitHub Actions inicia un proceso en el horario definido. El script hace
la búsqueda, genera el briefing, publica en un canal de Discord mediante
un webhook y termina.

**Ventajas:**

-   No hay que mantener un bot conectado las 24 horas.
-   No se necesita contratar un servidor para ejecutar el schedule.
-   GitHub Actions permite ejecutar workflows programados.
-   Discord aloja el webhook; el proyecto solo realiza una petición
    HTTP.
-   Es una forma simple de validar el valor del producto.

**Limitaciones:**

-   El webhook solo publica en el canal configurado; no escucha mensajes
    ni ofrece comandos.
-   GitHub Actions puede retrasar ejecuciones programadas cuando hay
    mucha carga.
-   En repositorios públicos, GitHub desactiva automáticamente los
    schedules si no hay actividad durante 60 días.
-   Las ejecuciones programadas solo se ejecutan desde la rama por
    defecto.

### Opción posterior: bot persistente con `discord.py`

Un bot conectado a Discord permite comandos como `/briefing`,
preferencias y respuestas interactivas. Para recibir comandos e
interactuar en tiempo real, el proceso debe mantenerse activo en un
servicio de hosting.

Puede añadirse más adelante sin reescribir la lógica de búsqueda si esta
queda separada del mecanismo de publicación.

**Decisión del MVP:** implementar el generador de briefing como servicio
independiente y utilizar GitHub Actions + webhook para programarlo.
Posponer los comandos slash.

Referencias: - [GitHub Actions: eventos que activan
workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows) -
[Discord: uso de
webhooks](https://discord.com/safety/using-webhooks-and-embeds)

------------------------------------------------------------------------

## 4. Herramientas y servicios

  -----------------------------------------------------------------------
  Necesidad               Elección inicial        Motivo
  ----------------------- ----------------------- -----------------------
  Lenguaje                Python 3.12 o versión   Desarrollo rápido e
                          estable disponible en   integración con APIs
                          el runner               

  Cliente HTTP            `httpx`                 Llamadas a APIs con
                                                  timeout y manejo de
                                                  errores

  Validación de datos     `pydantic`              Normalizar resultados y
                                                  validar la salida del
                                                  modelo

  Búsqueda web            Brave Search API        Resultados con URL,
                                                  título, snippet y datos
                                                  de noticias

  Modelo de lenguaje      Proveedor               Evita acoplar la
                          intercambiable mediante aplicación a un único
                          una interfaz propia     proveedor

  Acceso a LLM            API compatible con      Permite seleccionar un
                          OpenAI, por ejemplo     modelo según calidad,
                          OpenRouter, o el        disponibilidad y coste
                          proveedor elegido       

  Publicación en Discord  Discord Webhook +       No requiere un bot
                          `httpx`                 persistente para
                                                  publicar

  Programación            GitHub Actions          Ejecuta el proceso de
                          (`schedule`)            forma periódica

  Pruebas                 `pytest` + mocks        Probar el flujo sin
                                                  gastar llamadas ni
                                                  publicar mensajes
                                                  reales

  Configuración           Variables de entorno y  No guardar claves en el
                          GitHub Actions Secrets  repositorio

  Control de versiones    Git + GitHub            Código, historial y
                                                  automatización
  -----------------------------------------------------------------------

### Búsqueda web: Brave Search API

Brave Search API es la opción inicial recomendada para el MVP porque
devuelve resultados web que el código puede procesar. La página de
precios consultada indica créditos gratuitos mensuales de USD 5 y un
precio de USD 5 por cada 1.000 solicitudes para el plan Search. La
cuenta puede requerir verificación mediante tarjeta; revisa los términos
y límites actuales antes de activarla.

-   [Brave Search API](https://brave.com/search/api/)
-   [Precios y
    créditos](https://api-dashboard.search.brave.com/documentation/pricing)

No asumas que una API es ilimitada o permanentemente gratuita. Configura
límites de resultados, evita búsquedas redundantes y registra el número
de solicitudes.

**Alternativa complementaria:** feeds RSS de fuentes seleccionadas.
Pueden ayudar a obtener contenido de sitios conocidos, pero no
sustituyen una búsqueda general. Añadir RSS después de que el primer
flujo funcione.

### Modelo de lenguaje

El LLM no debería inventar noticias ni buscar por sí solo sin
trazabilidad. El código obtiene primero resultados de búsqueda y le
entrega al modelo los títulos, snippets, URLs y fechas disponibles. El
modelo debe devolver una estructura validable con los resultados
seleccionados y sus resúmenes.

Define una interfaz interna, por ejemplo `AIProvider`, para poder
cambiar de proveedor sin modificar el servicio de briefing. Verifica los
precios, límites y disponibilidad del modelo elegido; los planes
gratuitos pueden tener restricciones o cambiar.

### Discord Webhook

Crear un webhook en el canal destino y guardar su URL como secreto. El
programa envía una petición HTTP `POST` con el contenido del briefing.

Un webhook puede publicar mensajes, pero no recibe comandos ni permite
consultar mensajes. La URL contiene un token secreto: nunca debe
aparecer en el código, los logs o el README.

-   [Introducción a los webhooks de
    Discord](https://support.discord.com/hc/es/articles/228383668-Introducci%C3%B3n-a-los-webhooks)
-   [Documentación de webhooks de
    Discord](https://discord.com/developers/docs/resources/webhook)

------------------------------------------------------------------------

## 5. Hosting gratuito y schedule

### Recomendación: GitHub Actions

Para el objetivo de hoy, **GitHub Actions es la opción más sencilla**.
No es un servidor permanentemente encendido: inicia el runner a la hora
programada, ejecuta el script y finaliza.

Es apropiado para una tarea periódica de duración limitada. Consulta los
límites de minutos de Actions que correspondan a tu cuenta y
repositorio. Para evitar sorpresas, limita la frecuencia y el número de
consultas.

### Ejemplo de schedule

Crear `.github/workflows/orbit-briefing.yml`:

``` yaml
name: Orbit Briefing

on:
  workflow_dispatch:
  schedule:
    - cron: "17 8 * * *"
      timezone: "America/Bogota"

permissions:
  contents: read

jobs:
  briefing:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Generate and publish briefing
        env:
          BRAVE_SEARCH_API_KEY: ${{ secrets.BRAVE_SEARCH_API_KEY }}
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
          LLM_BASE_URL: ${{ secrets.LLM_BASE_URL }}
          LLM_MODEL: ${{ vars.LLM_MODEL }}
          DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
        run: python -m src.main
```

Este ejemplo programa la ejecución para las **8:17 a. m. en
`America/Bogota`**, todos los días, y permite ejecutarla manualmente
desde la pestaña Actions. Si la configuración de timezone no está
disponible en el entorno o esquema que utilices, expresa la hora en UTC
y verifica la conversión antes de desplegar.

Las acciones `checkout` y `setup-python` están fijadas a versiones
mayores por legibilidad del ejemplo. Para un proyecto más sensible,
considera fijar las acciones a SHA verificado y mantenerlas
actualizadas.

**Importante:** la hora programada no es una garantía de ejecución al
segundo. GitHub documenta posibles retrasos durante periodos de carga
elevada. El flujo también debe funcionar con `workflow_dispatch` para
probarlo manualmente.

### ¿Qué ocurre con un repositorio privado?

GitHub Actions ofrece minutos incluidos según el plan y el tipo de
repositorio. Consulta el consumo y los límites actuales de tu cuenta. No
conviertas el repositorio en público solo por el schedule si contiene
información privada.

-   [Eventos de GitHub
    Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
-   [Precios de GitHub Actions](https://github.com/pricing)

### Otras opciones

-   **Render Cron Jobs:** diseñado para ejecutar tareas y terminar;
    revisa disponibilidad, límites y costes actuales antes de elegirlo.
-   **Un VPS o servicio siempre activo:** más apropiado cuando Orbit
    necesite un bot conectado continuamente, pero no es necesario para
    este primer hito.
-   **Render Free Web Service:** no es la mejor elección para un bot que
    requiere conexión permanente; los servicios web gratuitos pueden
    suspenderse tras inactividad.

Referencias: - [Tipos de servicios en
Render](https://render.com/docs/service-types) - [Limitaciones del plan
gratuito de Render](https://render.com/docs/free)

------------------------------------------------------------------------

## 6. Arquitectura propuesta

``` text
GitHub Actions (schedule)
        |
        v
src.main
        |
        v
BriefingService
        |
        +--> SearchProvider (Brave Search API)
        |
        +--> ResultNormalizer
        |
        +--> Deduplicator
        |
        +--> AIProvider (selección y resumen)
        |
        +--> BriefingFormatter
        |
        v
DiscordWebhookPublisher
        |
        v
Canal #daily-briefing
```

Cada componente tiene una responsabilidad definida. No hace falta crear
microservicios: todo puede vivir en una aplicación Python pequeña.

------------------------------------------------------------------------

## 7. Estructura sugerida del repositorio

``` text
orbit/
├── .github/
│   └── workflows/
│       └── orbit-briefing.yml
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── services/
│   │   └── briefing_service.py
│   ├── providers/
│   │   ├── search_provider.py
│   │   └── ai_provider.py
│   ├── publishers/
│   │   └── discord_webhook.py
│   └── utils/
│       ├── deduplication.py
│       └── formatting.py
├── tests/
│   ├── test_deduplication.py
│   ├── test_briefing_service.py
│   └── test_discord_webhook.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

No es obligatorio crear todos los archivos antes de necesitarlos. Mantén
la estructura mínima que permita separar proveedores, lógica de negocio
y publicación.

------------------------------------------------------------------------

## 8. Variables de entorno y secretos

`.env.example` debe mostrar los nombres, nunca los valores reales:

``` dotenv
BRAVE_SEARCH_API_KEY=
LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL=
DISCORD_WEBHOOK_URL=
BRIEFING_LANGUAGE=es
BRIEFING_MAX_RESULTS=5
SEARCH_MAX_RESULTS=10
```

En local, carga las variables con una librería como `python-dotenv`. En
GitHub, configura:

-   `BRAVE_SEARCH_API_KEY` como **Repository Secret**.
-   `LLM_API_KEY` como **Repository Secret**.
-   `LLM_BASE_URL` como secreto o variable, según si contiene
    información sensible.
-   `LLM_MODEL` como **Repository Variable** si no es confidencial.
-   `DISCORD_WEBHOOK_URL` como **Repository Secret**.

Añade `.env` a `.gitignore`. No imprimas las claves ni URLs completas de
webhooks en los logs. Si una clave se sube accidentalmente a GitHub,
revócala y genera otra; borrar el archivo en un commit posterior no
invalida el secreto expuesto.

------------------------------------------------------------------------

## 9. Flujo de procesamiento

1.  **Cargar configuración.** Fallar pronto si falta una variable
    obligatoria.
2.  **Construir consultas.** Para el primer MVP, limitarse a noticias
    recientes de IA y programación.
3.  **Buscar.** Consultar Brave Search API con timeout y límites.
4.  **Normalizar.** Convertir cada resultado a un esquema común: título,
    URL, snippet, fuente y fecha disponible.
5.  **Validar URLs y deduplicar.** Normalizar URLs con cuidado; no
    eliminar parámetros que sean necesarios para acceder al recurso.
6.  **Filtrar y seleccionar.** Usar reglas básicas y el LLM para escoger
    los mejores resultados.
7.  **Resumir.** El resumen debe basarse solo en la información recibida
    y conservar el enlace a la fuente.
8.  **Formatear.** Crear un mensaje corto, legible y dentro de los
    límites de Discord. Si hay muchos resultados, dividirlo en varios
    mensajes.
9.  **Publicar.** Enviar el briefing mediante el webhook y comprobar el
    código de respuesta.
10. **Registrar resultado.** Guardar logs de éxito/error sin secretos.

Si la búsqueda o el LLM falla, registra el error y termina con un estado
de ejecución fallido. No publiques como si el briefing estuviera
completo cuando no lo está.

------------------------------------------------------------------------

## 10. Formato del briefing

Ejemplo de formato esperado:

``` text
ORBIT — TECH RADAR
Miércoles, 21 de octubre

1. Título de la noticia
Resumen breve y útil, sin afirmar detalles que no estén respaldados.
Fuente: Nombre de la fuente · Fecha disponible
Leer original: https://...

2. Otro título
Resumen breve...
Fuente: ...
Leer original: https://...

Generado automáticamente. Revisa la fuente original para detalles y contexto.
```

Priorizar entre 3 y 5 resultados relevantes en lugar de llenar Discord
con enlaces de poco valor. Incluir la fecha si la fuente la proporciona;
si no, no inventarla.

------------------------------------------------------------------------

## 11. Plan de trabajo para hoy

### Hito 1 --- Preparación

-   [ ] Crear el repositorio y entorno virtual.
-   [ ] Añadir `requirements.txt`, `.gitignore` y `.env.example`.
-   [ ] Crear un webhook de Discord y probar un mensaje fijo.
-   [ ] Obtener una clave de Brave Search API.
-   [ ] Elegir un proveedor/modelo LLM y confirmar que la API funciona.

### Hito 2 --- Búsqueda

-   [ ] Implementar `SearchProvider`.
-   [ ] Consultar noticias de IA y programación.
-   [ ] Normalizar resultados.
-   [ ] Limitar el número de consultas y resultados.
-   [ ] Añadir timeout y errores claros.

### Hito 3 --- Briefing

-   [ ] Definir los esquemas Pydantic.
-   [ ] Implementar deduplicación por URL.
-   [ ] Implementar selección y resumen mediante el LLM.
-   [ ] Validar la respuesta del modelo.
-   [ ] Formatear el mensaje de Discord.

### Hito 4 --- Schedule

-   [ ] Ejecutar el programa localmente de extremo a extremo.
-   [ ] Crear el workflow `.github/workflows/orbit-briefing.yml`.
-   [ ] Configurar los Secrets y Variables en GitHub.
-   [ ] Ejecutar `workflow_dispatch` manualmente.
-   [ ] Revisar logs y confirmar que el mensaje llega al canal correcto.
-   [ ] Confirmar el schedule diario y la zona horaria.
-   [ ] Revisar el workflow después de la primera ejecución programada.

**Criterio de terminado hoy:** GitHub Actions puede ejecutar el flujo
bajo demanda y tiene configurada la ejecución automática; el proceso
publica en Discord resultados reales con enlaces a sus fuentes.

------------------------------------------------------------------------

## 12. Pruebas mínimas y criterios de aceptación

-   Una búsqueda sin resultados no debe romper el proceso.
-   Un error de API debe producir un log útil y un estado de fallo.
-   Los resultados repetidos deben deduplicarse.
-   El modelo no debe poder inventar URLs: el código debe publicar
    únicamente URLs que llegaron desde el proveedor de búsqueda.
-   La salida del LLM debe validarse antes de publicar.
-   Un fallo de Discord debe hacer fallar la ejecución.
-   Los mensajes deben respetar los límites de Discord.
-   Las claves y el webhook no deben aparecer en el repositorio ni en
    logs.
-   Las pruebas unitarias deben usar respuestas simuladas y no gastar
    créditos.
-   El workflow debe poder ejecutarse manualmente.
-   La ejecución programada debe estar en la rama por defecto.

------------------------------------------------------------------------

## 13. Prompt inicial para Cursor

Usa este prompt en Cursor después de crear el repositorio:

> Implementa el MVP de Orbit descrito en `README.md`. El objetivo de
> esta primera iteración es un proceso Python ejecutable con
> `python -m src.main` que busque noticias recientes de IA y
> programación mediante Brave Search API, normalice y deduplique
> resultados, use un proveedor LLM configurable para seleccionar y
> resumir entre 3 y 5 elementos, y publique un briefing con enlaces de
> fuentes mediante Discord Webhook.
>
> Requisitos:
>
> -   Separa `SearchProvider`, `AIProvider`, la lógica `BriefingService`
>     y `DiscordWebhookPublisher`.
> -   Usa `httpx`, Pydantic y configuración por variables de entorno.
> -   Usa timeout, manejo de errores y logs que no filtren secretos.
> -   Valida la respuesta del LLM y no permitas que invente URLs: solo
>     acepta URLs de los resultados de búsqueda.
> -   Limita consultas, resultados y longitud de mensajes.
> -   Añade pruebas con mocks; las pruebas no deben realizar llamadas
>     reales a APIs.
> -   Crea `.github/workflows/orbit-briefing.yml` con
>     `workflow_dispatch` y un schedule diario en `America/Bogota`.
> -   Documenta cómo configurar GitHub Secrets y ejecutar el workflow
>     manualmente.
> -   No agregues FastAPI, base de datos, Redis, vector database,
>     LangGraph ni múltiples agentes en esta fase.
> -   Primero inspecciona los archivos existentes y propone un plan
>     breve; después implementa el flujo mínimo de extremo a extremo.
> -   No declares que las pruebas pasaron si no las ejecutaste.

------------------------------------------------------------------------

## 14. Evolución después del MVP

1.  **Personalización:** guardar un perfil configurable con intereses y
    objetivos.
2.  **Becas y hackatones:** añadir consultas y fuentes específicas,
    fechas límite y requisitos.
3.  **Historial y deduplicación persistente:** usar SQLite inicialmente
    o PostgreSQL cuando exista una necesidad real de persistencia
    multiusuario.
4.  **Bot interactivo:** añadir `discord.py` y comandos slash,
    manteniendo el servicio de briefing independiente.
5.  **Preferencias y feedback:** permitir marcar resultados como
    útiles/no útiles y ajustar la selección.
6.  **Seguimiento:** volver a comprobar convocatorias y notificar
    cambios, siempre con fecha y fuente verificables.

No se debe añadir complejidad hasta que el flujo básico publique
información útil de manera estable.

------------------------------------------------------------------------

## Fuentes principales

-   [Brave Search API --- página oficial](https://brave.com/search/api/)
-   [Brave Search API --- precios y
    créditos](https://api-dashboard.search.brave.com/documentation/pricing)
-   [GitHub Actions --- eventos y
    schedules](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
-   [GitHub Actions --- precios](https://github.com/pricing)
-   [Discord ---
    webhooks](https://discord.com/safety/using-webhooks-and-embeds)
-   [Render --- tipos de
    servicio](https://render.com/docs/service-types)
-   [Render --- plan gratuito y
    limitaciones](https://render.com/docs/free)
