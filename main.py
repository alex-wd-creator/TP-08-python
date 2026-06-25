# -*- coding: utf-8 -*-
import os
import pygame
import sys
import random

PANTALLA_ANCHO = 1180
PANTALLA_ALTO = 720
COLUMNAS = 12
FILAS = 8
TAMANO_CELDA = 64
GRILLA_OFFSET_X = 20
GRILLA_OFFSET_Y = 60
HUD_X = GRILLA_OFFSET_X + COLUMNAS * TAMANO_CELDA + 20
FPS = 60

COLOR_FONDO       = (28, 32, 42)
COLOR_CELDA       = (64, 72, 92)
COLOR_CELDA_BORDE = (40, 46, 60)
COLOR_SENDERO     = (240, 215, 90)
COLOR_MERENDERO   = (230, 130, 70)
COLOR_TEXTO       = (235, 235, 235)
COLOR_TEXTO_TENUE = (160, 165, 180)
COLOR_OK          = (90, 220, 130)
COLOR_HUD_BG      = (38, 44, 58)

COOLDOWN_MS = 140

def en_grilla(fila, columna):
    return 0 <= fila < FILAS and 0 <= columna < COLUMNAS


def celda_a_pixel(fila, columna):
    pixel_x = GRILLA_OFFSET_X + columna * TAMANO_CELDA
    pixel_y = GRILLA_OFFSET_Y + fila * TAMANO_CELDA
    return pixel_x, pixel_y

def mover_copernibot(estado, delta_fila, delta_columna):
    fila_actual, columna_actual = estado["cursor"]
    nueva_fila = fila_actual + delta_fila
    nueva_columna = columna_actual + delta_columna
    if not en_grilla(nueva_fila, nueva_columna):
        return
    estado["sendero"].append((nueva_fila, nueva_columna))
    estado["cursor"] = (nueva_fila, nueva_columna)
    if (nueva_fila, nueva_columna) == estado["merendero"]:
        estado["completado"] = True

def dibujar_grilla(pantalla, estado, fuente_chica, imagen_copernibot):
    celdas_sendero = set(estado["sendero"])

    for fila in range(FILAS):
        for columna in range(COLUMNAS):
            pixel_x, pixel_y = celda_a_pixel(fila, columna)
            rect_celda = pygame.Rect(pixel_x, pixel_y, TAMANO_CELDA, TAMANO_CELDA)
            color_celda = COLOR_CELDA
            if (fila, columna) in celdas_sendero:
                color_celda = COLOR_SENDERO
            pygame.draw.rect(pantalla, color_celda, rect_celda)
            pygame.draw.rect(pantalla, COLOR_CELDA_BORDE, rect_celda, 1)


    fila_merendero, columna_merendero = estado["merendero"]
    pixel_merendero_x, pixel_merendero_y = celda_a_pixel(fila_merendero, columna_merendero)
    pygame.draw.rect(pantalla, COLOR_MERENDERO,
                     (pixel_merendero_x + 6, pixel_merendero_y + 6,
                      TAMANO_CELDA - 12, TAMANO_CELDA - 12), 3)
    texto_merendero = fuente_chica.render("MERENDERO", True, COLOR_TEXTO)
    pantalla.blit(texto_merendero,
                  (pixel_merendero_x + TAMANO_CELDA // 2 - texto_merendero.get_width() // 2,
                   pixel_merendero_y + TAMANO_CELDA - 16))

    mitad = TAMANO_CELDA // 2
    sendero = estado["sendero"]
    for indice in range(1, len(sendero)):
        origen_x, origen_y = celda_a_pixel(*sendero[indice - 1])
        destino_x, destino_y = celda_a_pixel(*sendero[indice])
        pygame.draw.line(pantalla, (255, 255, 255),
                         (origen_x + mitad, origen_y + mitad),
                         (destino_x + mitad, destino_y + mitad), 4)

    fila_cursor, columna_cursor = estado["cursor"]
    pixel_cursor_x, pixel_cursor_y = celda_a_pixel(fila_cursor, columna_cursor)
    pantalla.blit(imagen_copernibot, (pixel_cursor_x + 2, pixel_cursor_y + 2))


def dibujar_hud(pantalla, fuente_mediana, fuente_chica):
    panel = pygame.Rect(HUD_X - 10, GRILLA_OFFSET_Y - 10,
                        PANTALLA_ANCHO - HUD_X, FILAS * TAMANO_CELDA + 20)
    pygame.draw.rect(pantalla, COLOR_HUD_BG, panel, border_radius=8)

    posicion_y = GRILLA_OFFSET_Y

    titulo_mision = fuente_mediana.render("Misión", True, COLOR_OK)
    pantalla.blit(titulo_mision, (HUD_X, posicion_y))
    posicion_y += titulo_mision.get_height() + 6

    lineas_mision = [
        "Acompaña a COPERNIBOT a dejar",
        "las donaciones en el merendero.",
    ]
    for linea in lineas_mision:
        texto_mision = fuente_chica.render(linea, True, COLOR_TEXTO)
        pantalla.blit(texto_mision, (HUD_X, posicion_y))
        posicion_y += texto_mision.get_height() + 2

    posicion_y += 18

    titulo_controles = fuente_mediana.render("Controles", True, COLOR_TEXTO)
    pantalla.blit(titulo_controles, (HUD_X, posicion_y))
    posicion_y += titulo_controles.get_height() + 10

    instrucciones = [
        "Flechas: Movimiento COPERNIBOT",
        "ESC    : Salir",
    ]
    for linea in instrucciones:
        texto_linea = fuente_chica.render(linea, True, COLOR_TEXTO_TENUE)
        pantalla.blit(texto_linea, (HUD_X, posicion_y))
        posicion_y += texto_linea.get_height() + 4


def dibujar_cartel_completado(pantalla, fuente_grande, fuente_mediana):
    overlay = pygame.Surface((PANTALLA_ANCHO, PANTALLA_ALTO), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    pantalla.blit(overlay, (0, 0))

    cartel_ancho = 520
    cartel_alto = 180
    cartel_x = PANTALLA_ANCHO // 2 - cartel_ancho // 2
    cartel_y = PANTALLA_ALTO // 2 - cartel_alto // 2
    pygame.draw.rect(pantalla, COLOR_HUD_BG,
                     (cartel_x, cartel_y, cartel_ancho, cartel_alto),
                     border_radius=12)
    pygame.draw.rect(pantalla, COLOR_OK,
                     (cartel_x, cartel_y, cartel_ancho, cartel_alto),
                     4, border_radius=12)

    texto_titulo = fuente_grande.render("NIVEL COMPLETADO", True, COLOR_OK)
    pantalla.blit(texto_titulo,
                  (PANTALLA_ANCHO // 2 - texto_titulo.get_width() // 2,
                   cartel_y + 50))

    texto_subtitulo = fuente_mediana.render("Llegaste al merendero", True, COLOR_TEXTO)
    pantalla.blit(texto_subtitulo,
                  (PANTALLA_ANCHO // 2 - texto_subtitulo.get_width() // 2,
                   cartel_y + 110))

def crear_estado_de_juego():
    entrada = (0, 0)
    merendero = (7, 11)
    estado_de_juego = {
        "merendero": merendero,
        "sendero": [entrada],
        "cursor": entrada,
        "ultimo_movimiento": 0,
        "completado": False,
    }
    return estado_de_juego

def cargar_imagen_copernibot():
    ruta_imagen_copernibot = os.path.join(os.path.dirname(__file__), "COPERNIBOT.png")
    imagen_copernibot = pygame.image.load(ruta_imagen_copernibot).convert_alpha()
    return pygame.transform.smoothscale(imagen_copernibot, (TAMANO_CELDA - 4, TAMANO_CELDA - 4))

def cargar_imagen_obstaculo():
    ruta_imagen_obstaculo = os.path.join(os.path.dirname(__file__), "obstaculo.jpg")
    imagen_obstaculo = pygame.image.load(ruta_imagen_obstaculo).convert_alpha()
    return pygame.transform.smoothscale(imagen_obstaculo, (TAMANO_CELDA - 4, TAMANO_CELDA - 4))


def main():
    pygame.init()
    pygame.display.set_caption("OFIRCA 2026 - Ronda 1: Inicio")
    pantalla = pygame.display.set_mode((PANTALLA_ANCHO, PANTALLA_ALTO))
    reloj = pygame.time.Clock()

    fuente_grande = pygame.font.SysFont("consolas", 28, bold=True)
    fuente_mediana = pygame.font.SysFont("consolas", 17)
    fuente_chica = pygame.font.SysFont("consolas", 14)

    imagen_copernibot = cargar_imagen_copernibot()
    imagen_obstaculos = cargar_imagen_obstaculo()

    estado = crear_estado_de_juego()

    juego_en_ejecucion = True

    while juego_en_ejecucion:
        ahora = pygame.time.get_ticks()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                juego_en_ejecucion = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    juego_en_ejecucion = False

        if not estado["completado"]:
            if ahora - estado["ultimo_movimiento"] >= COOLDOWN_MS:
                teclas = pygame.key.get_pressed()
                delta_fila, delta_columna = 0, 0
                ultima_fila, ultima_columna = delta_fila, delta_columna
                if teclas[pygame.K_UP]:
                        delta_fila = -1
                elif teclas[pygame.K_DOWN]:
                    delta_fila = 1
                elif teclas[pygame.K_LEFT]:
                    delta_columna = -1
                elif teclas[pygame.K_RIGHT]:
                    delta_columna = 1
                if delta_fila != 0 or delta_columna != 0 or COLOR_CELDA != COLOR_SENDERO:
                    mover_copernibot(estado, delta_fila, delta_columna)
                    estado["ultimo_movimiento"] = ahora

        pantalla.fill(COLOR_FONDO)
        dibujar_grilla(pantalla, estado, fuente_chica, imagen_copernibot)
        dibujar_hud(pantalla, fuente_mediana, fuente_chica)
        if estado["completado"]:
            dibujar_cartel_completado(pantalla, fuente_grande, fuente_mediana)

        pygame.display.flip()
        reloj.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()