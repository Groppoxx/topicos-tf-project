# **Universidad Peruana de Ciencias Aplicadas**  
**Carrera:** Ciencias de la Computación  
**Curso:** Tópicos en Ciencias de la Computación  
**Año:** 2025

**Integrantes del equipo:**

- Fabiana Nayeli Mallma Villanueva (u20211d574)  
- Iam Anthony Marcelo Alvarez Orellana (u2021118258)  
- Paula Jimena Mancilla Cienfuegos (u202115844)  
- Tomas Alonso Pastor Salazar (U201916314)

# Sistema Multiagente de Búsqueda de Niño Perdido con Drones

Este proyecto implementa un sistema multiagente distribuido para la búsqueda de un niño perdido mediante drones autónomos, coordinados mediante SPADE y comunicados por protocolo XMPP. Incluye visualización en tiempo real, restricciones de proximidad y despliegue distribuido.

---

## 🧠 Descripción

El sistema simula un entorno donde varios drones buscan de forma coordinada a un niño desaparecido en un mapa con obstáculos (bosque, río). Cada dron actúa como un agente inteligente y reporta su posición al coordinador central cuando detecta al niño cerca.

---

## 🎯 Objetivos

- Implementar un sistema multiagente para búsqueda autónoma con drones.
- Aplicar restricciones espaciales de proximidad mediante programación restrictiva (Constraint Programming).
- Visualizar en tiempo real la exploración y detección.

---

## 🧩 Arquitectura del Sistema

### Agentes Implementados

| Agente             | Función                                                                 |
|--------------------|-------------------------------------------------------------------------|
| `CoordinadorAgent` | Coordina posiciones, recibe reportes de drones y notifica detección.   |
| `DroneAgent`       | Explora aleatoriamente y detecta al niño si está cerca.                 |

### Componentes Internos y Externos

| Componente            | Tipo     | Función                                                                 |
|-----------------------|----------|-------------------------------------------------------------------------|
| `Python + SPADE`      | Interno  | Framework de agentes inteligentes.                                     |
| `Openfire`            | Externo  | Servidor XMPP para comunicación.                                       |
| `Matplotlib + threading` | Interno  | Visualización gráfica del mapa.                                        |
| `WSL/Ubuntu`          | Externo  | Sistema operativo de ejecución con soporte XMPP.                       |

---

## ⚙️ Comunicación y Conexiones

- Cada `DroneAgent` inicia en una posición aleatoria y explora su entorno.
- Si un dron detecta al niño (dentro de una región 5x5), envía el mensaje `OBJETIVO_ENCONTRADO`.
- El `CoordinadorAgent` notifica a todos los drones con la ubicación global del niño.

---

## 📏 Aplicación de Restricciones (Constraint Programming)

Aunque no se utilizó un solver formal como OR-Tools, se aplicaron restricciones manuales en el código, propias de la programación restrictiva:

```python
# Restricción de límites del mapa
nueva[0] = max(0, min(99, nueva[0]))
nueva[1] = max(0, min(99, nueva[1]))

# Restricción de detección de proximidad (distancia ≤ 5)
if dx <= 5 and dy <= 5:
```

> Para versiones futuras, se recomienda integrar OR-Tools para optimizar la planificación y cobertura total sin solapamientos.

---

## 🌐 Despliegue Distribuido

### Estado actual:
- Simulación en un solo host usando múltiples agentes SPADE.

### Recomendación:
- Ejecutar `DroneAgents` en distintos hosts conectados al mismo servidor XMPP (Openfire), validando el sistema en un entorno distribuido real.

---

## 🧪 Pruebas y Resultados

| Prueba               | Configuración                            | Resultado                                                                 |
|----------------------|-------------------------------------------|---------------------------------------------------------------------------|
| Prueba base          | 5 drones + coordinador, niño móvil        | Niño detectado en menos de 1 minuto simulado.                            |
| Obstáculos densos    | 300 árboles + río central                 | Drones evitaron celdas ocupadas.                                         |
| Escalado de agentes  | Hasta 20 drones                           | Consumo de CPU creció linealmente. Sin conflictos en la comunicación SPADE. |

### Visualización

- **Drones**: puntos azules  
- **Niño**: cruz roja  
- **Obstáculos**: árboles (verde), río (celeste)  

---

## ✅ Conclusiones

- SPADE es eficaz para modelar sistemas multiagente distribuidos.
- La estructura de coordinación centralizada permite escalabilidad y control global.
- Las restricciones aplicadas aseguraron límites seguros y eficiencia en la búsqueda.
- El sistema puede ser extendido para operar con drones físicos.

---

## 💡 Recomendaciones

- Integrar pathfinding con algoritmo A* para evitar obstáculos.
- Ejecutar agentes en múltiples máquinas remotas.
- Usar OR-Tools para optimizar rutas y zonas de búsqueda.
- Implementar visión artificial en drones reales para una detección más robusta.

---

## 🔗 Referencias

- 📚 SPADE: [https://spade-mas.readthedocs.io](https://spade-mas.readthedocs.io)  
- 🔗 Openfire: [https://www.igniterealtime.org/projects/openfire/](https://www.igniterealtime.org/projects/openfire/)  
- 🧮 OR-Tools CP-SAT Solver: [https://developers.google.com/optimization](https://developers.google.com/optimization)  

---

## 🤖 Uso de Inteligencia Artificial en el Proyecto

Durante el desarrollo, se aplicaron herramientas de IA generativa para:

- Resolver errores de configuración en SPADE y Openfire.
- Asistir en la instalación y configuración de entornos (conda, WSL).
- Identificar errores de ejecución en Python y SPADE.
- Depurar la comunicación entre agentes y sus comportamientos cíclicos.