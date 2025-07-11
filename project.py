from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import asyncio
import random
import matplotlib.pyplot as plt
import threading
import numpy as np

# ==================== MAPA Y OBSTÁCULOS ====================
TAMANO_MAPA = 100
obstaculos = np.zeros((TAMANO_MAPA, TAMANO_MAPA))

# Árboles
for _ in range(300):
    x, y = random.randint(0, 99), random.randint(0, 99)
    obstaculos[x][y] = 1 

# Río
for x in range(20, 80):
    obstaculos[x][50] = 2  

def es_obstaculo(pos):
    x, y = pos
    return obstaculos[x][y] != 0


# ==================== NIÑO MÓVIL ====================
class NinoPerdido:
    def __init__(self):
        self.posicion = [random.randint(10, 90), random.randint(10, 90)]
        self.detenerse = False

    def moverse(self):
        if self.detenerse:
            return

        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])
        nueva = [self.posicion[0] + dx, self.posicion[1] + dy]
        nueva[0] = max(0, min(99, nueva[0]))
        nueva[1] = max(0, min(99, nueva[1]))
        if not es_obstaculo(nueva):
            self.posicion = nueva


nino = NinoPerdido()


# ==================== AGENTE DRONE ====================
class DroneAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.cuadrante = (0, 99, 0, 99)  # Todo el mapa

    class BuscarBehaviour(CyclicBehaviour):
        async def run(self):
            if not hasattr(self.agent, "posicion"):
                self.agent.posicion = [random.randint(0, 99), random.randint(0, 99)]
                self.agent.objetivo = None
                self.agent.estacionado = False
                self.agent.encontrado = False

            if not self.agent.estacionado and not self.agent.encontrado:
                dx = random.choice([-2, -1, 0, 1, 2])
                dy = random.choice([-2, -1, 0, 1, 2])
                nueva = [self.agent.posicion[0] + dx, self.agent.posicion[1] + dy]
                nueva[0] = max(0, min(99, nueva[0]))
                nueva[1] = max(0, min(99, nueva[1]))
                self.agent.posicion = nueva  # Ignora obstáculos

                print(f"[{self.agent.name}] Buscando en {self.agent.posicion}")

                dx = abs(self.agent.posicion[0] - nino.posicion[0])
                dy = abs(self.agent.posicion[1] - nino.posicion[1])
                if dx <= 5 and dy <= 5 and not self.agent.encontrado:
                    self.agent.encontrado = True
                    self.agent.estacionado = True
                    nino.detenerse = True
                    print(f"[{self.agent.name}] ¡NIÑO DETECTADO en {nino.posicion}!")
                    msg = Message(to=self.agent.coordinador)
                    msg.body = f"OBJETIVO_ENCONTRADO:{self.agent.name}:{nino.posicion}"
                    await self.send(msg)

            msg = await self.receive(timeout=0.1)
            if msg and msg.body.startswith("OBJETIVO_GLOBAL"):
                pos_nino = eval(msg.body.split(":")[1])
                self.agent.objetivo = pos_nino
                self.agent.estacionado = False

            if self.agent.objetivo and not self.agent.estacionado:
                dx = self.agent.objetivo[0] - self.agent.posicion[0]
                dy = self.agent.objetivo[1] - self.agent.posicion[1]
                nueva = self.agent.posicion.copy()
                if abs(dx) > 0:
                    nueva[0] += 1 if dx > 0 else -1
                if abs(dy) > 0:
                    nueva[1] += 1 if dy > 0 else -1
                nueva[0] = max(0, min(99, nueva[0]))
                nueva[1] = max(0, min(99, nueva[1]))
                self.agent.posicion = nueva

                print(f"[{self.agent.name}] Yendo al niño en {self.agent.objetivo} - Pos: {self.agent.posicion}")

                if self.agent.posicion == self.agent.objetivo:
                    print(f"[{self.agent.name}] Llegó al niño.")
                    self.agent.estacionado = True

            msg_pos = Message(to=self.agent.coordinador)
            msg_pos.body = f"POS:{self.agent.name}:{self.agent.posicion}"
            await self.send(msg_pos)

            await asyncio.sleep(0.4)

    async def setup(self):
        self.coordinador = "coordinador@localhost"
        self.add_behaviour(self.BuscarBehaviour())


# ==================== AGENTE COORDINADOR ====================
class CoordinadorAgent(Agent):
    class CoordinarBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if msg:
                if msg.body.startswith("POS"):
                    nombre, pos = msg.body.split(":")[1:]
                    self.agent.posiciones[nombre] = eval(pos)
                elif msg.body.startswith("OBJETIVO_ENCONTRADO"):
                    partes = msg.body.split(":")
                    pos_nino = eval(partes[2])
                    print(f"[COORDINADOR] Niño encontrado por {partes[1]} en {pos_nino}")
                    for drone in self.agent.lista_drones:
                        aviso = Message(to=drone)
                        aviso.body = f"OBJETIVO_GLOBAL:{pos_nino}"
                        await self.send(aviso)

    def mostrar_drones(self):
        plt.ion()
        fig, ax = plt.subplots()
        while True:
            nino.moverse()
            ax.clear()

            for nombre, pos in self.posiciones.items():
                ax.plot(pos[0], pos[1], "bo")
                ax.text(pos[0]+1, pos[1]+1, nombre, fontsize=8)
            ax.plot(nino.posicion[0], nino.posicion[1], "rx", label="Niño (móvil)" if not nino.detenerse else "Niño (encontrado)")

            for x in range(TAMANO_MAPA):
                for y in range(TAMANO_MAPA):
                    if obstaculos[x][y] == 1:
                        ax.plot(x, y, "g.", markersize=1)
                    elif obstaculos[x][y] == 2:
                        ax.plot(x, y, "c.", markersize=1)

            ax.set_xlim(0, 100)
            ax.set_ylim(0, 100)
            ax.set_title("Simulación: Búsqueda de Niño Perdido")
            plt.legend()
            plt.pause(0.3)

    async def setup(self):
        self.posiciones = {}
        self.lista_drones = []
        self.add_behaviour(self.CoordinarBehaviour())
        threading.Thread(target=self.mostrar_drones, daemon=True).start()


# ==================== MAIN ====================
async def main():
    print(f"[MAIN] Niño inicialmente en: {nino.posicion}")
    coord = CoordinadorAgent("coordinador@localhost", "1234")
    await coord.start(auto_register=False)

    for i in range(5):  
        jid = f"drone{i}@localhost"
        drone = DroneAgent(jid, "1234")
        await drone.start(auto_register=False)
        coord.lista_drones.append(jid)
        await asyncio.sleep(0.3)

    print("[MAIN] Búsqueda iniciada...")
    while True:
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
