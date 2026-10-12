"""Punto de entrada de Hot Potato Chip Bag.

Sigue el mismo patrón que los proyectos de gale-admin create-project:
un main.py mínimo que solo instancia el Game y lo ejecuta.
"""

import os
import pygame
import pygame._sdl2.controller as ext_controller  # Explicitly import the SDL2 extension
import importlib

# 1. Intentar cargar el archivo en el entorno
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "gamecontrollerdb.txt")

if os.path.exists(db_path):
    with open(db_path, "r", encoding="utf-8") as f:
        os.environ["SDL_GAMECONTROLLERCONFIG"] = f.read()
    #print("Archivo 'gamecontrollerdb.txt' leído e inyectado en el entorno.")
else:
    #print("ERROR: El archivo no existe en la ruta especificada.")
    pass

os.environ["PATH"] = "" 
pygame.init()
importlib.reload(os)
ext_controller.init()

# Lista global para mantener las referencias de AMBOS mandos vivas en memoria
mandos_activos = []

#print(f"\n🔍 Escaneando dispositivos... Encontrados: {ext_controller.get_count()}")

# 3. Recorrer y registrar cada mando de forma independiente
for i in range(ext_controller.get_count()):
    if ext_controller.is_controller(i):
        # Creamos la instancia del mando
        mando = ext_controller.Controller(i)
        # ⚠️ IMPORTANTE: Lo guardamos en una lista para que Python no destruya la conexión
        mandos_activos.append(mando)

        id_instancia = mando.as_joystick().get_instance_id()
        
        #print(f"\n🎮 [Mando #{i}] Detectado: {mando.name} (ID de Instancia: {id_instancia})")
        
        # Obtener el mapa de botones activo gracias a la base de datos
        mapeo_activo = mando.get_mapping()
        
        if mapeo_activo:
            #print(f"   ✅ ¡ÉXITO! Mapeado correctamente con la base de datos.")
            # Mostramos los primeros 3 botones para confirmar que el diccionario tiene datos
            botones_muestra = list(mapeo_activo.items())[:3]
            #print(f"   📋 Muestra de botones: {botones_muestra}...")
        else:
            #print("   ⚠️ ADVERTENCIA: SDL no encontró un mapeo específico en el archivo .txt (usa valores genéricos del OS).")
            pass
    else:
        #print(f"\n🔌 Dispositivo en índice {i} no es un gamepad compatible con SDL.")
        pass

if not mandos_activos:
    #print("\n💡 No se detectó ningún mando físico. Conecta tus gamepads y vuelve a ejecutar el script.")
    pass


from src.game import HotPotatoChipBagGame

if __name__ == "__main__":
    HotPotatoChipBagGame(title="Hot Potato Chip Bag").exec()
