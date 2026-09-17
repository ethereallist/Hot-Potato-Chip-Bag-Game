import sys
import pygame

pygame.init()
pygame.joystick.init()

# Diccionario para llevar el registro de todos los mandos conectados,
# indexados por su instance_id (el identificador estable que usan los
# eventos, y el mismo concepto que gamepad_id en Gale).
mandos = {}


def registrar_mando(indice_dispositivo: int) -> None:
    mando = pygame.joystick.Joystick(indice_dispositivo)
    mando.init()
    mandos[mando.get_instance_id()] = mando
    print(f"✅ Mando conectado -> instance_id={mando.get_instance_id()}  nombre='{mando.get_name()}'")
    print(f"   Botones: {mando.get_numbuttons()}  Ejes: {mando.get_numaxes()}")


# 1. Inicializar todos los mandos ya conectados al arrancar
cantidad_mandos = pygame.joystick.get_count()

if cantidad_mandos == 0:
    print("❌ No se detectó ningún mando. Conéctalo y vuelve a ejecutar.")
    sys.exit()

print("==========================================")
for i in range(cantidad_mandos):
    registrar_mando(i)
print("==========================================")
print("Presiona botones o mueve los sticks para probar.")
print("Fíjate en 'instance_id' para saber CUÁL mando generó el evento.")
print("(Cierra la ventana para salir)\n")

pantalla = pygame.display.set_mode((400, 200))
pygame.display.set_caption("Prueba de Mando")

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Un mando nuevo se conectó DESPUÉS de arrancar el script
        elif event.type == pygame.JOYDEVICEADDED:
            registrar_mando(event.device_index)

        # Un mando se desconectó
        elif event.type == pygame.JOYDEVICEREMOVED:
            nombre = mandos.get(event.instance_id)
            nombre = nombre.get_name() if nombre else "?"
            print(f"🔌 Mando desconectado -> instance_id={event.instance_id} ('{nombre}')")
            mandos.pop(event.instance_id, None)

        elif event.type == pygame.JOYBUTTONDOWN:
            print(f"🔘 [mando {event.instance_id}] Botón presionado: ID {event.button}")

        elif event.type == pygame.JOYBUTTONUP:
            print(f"⚪ [mando {event.instance_id}] Botón soltado: ID {event.button}")

        elif event.type == pygame.JOYAXISMOTION:
            if abs(event.value) > 0.2:
                print(f"🕹️  [mando {event.instance_id}] Eje {event.axis} movido a: {event.value:.2f}")

        elif event.type == pygame.JOYHATMOTION:
            print(f"🎯 [mando {event.instance_id}] Cruceta (Hat) movida a: {event.value}")

    pantalla.fill((30, 30, 30))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()