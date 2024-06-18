import pygame
import random
import sys

pygame.init()

# Configuración del tamaño de cada celda y colores
cell_size = 100
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Cargar imágenes para el gato, el ratón y la cueva
gato_img = pygame.image.load("gato.jpeg")
# Cargar la imagen del gato desde el archivo "gato.jpeg"
gato_img = pygame.transform.scale(gato_img, (cell_size, cell_size))
#Redimensionar la imagen del gato al tamaño de una celda del tablero
raton_img = pygame.image.load("raton.jpeg")
# Cargar la imagen del ratón desde el archivo "raton.jpeg"
raton_img = pygame.transform.scale(raton_img, (cell_size, cell_size))
# Redimensionar la imagen del ratón al tamaño de una celda del tablero
cuevita_img = pygame.image.load("escape raton.jpg")
# Cargar la imagen de la cueva desde el archivo "escape raton.jpg"
cuevita_img = pygame.transform.scale(cuevita_img, (cell_size, cell_size))
# Redimensionar la imagen de la cueva al tamaño de una celda del tablero


# Clase principal del juego
class JuegoGatoRaton:
    def __init__(self, n):
        self.n = n
        #Guarda el tamaño del tablero (n) en el atributo de instancia self.n.
        self.width, self.height = n * cell_size, n * cell_size
        #Calcula el ancho y alto de la ventana en píxeles
        self.window = pygame.display.set_mode((self.width, self.height))
        #Ventana de pygame
        pygame.display.set_caption("Juego del Gato y el Ratón")
        #Título de la ventana
        self.reset_game() 
        #se encarga de inicializar o reiniciar el estado del juego, configurando las posiciones iniciales de los personajes

    def reset_game(self):
        # Inicialización de variables del juego
        self.turno_gato = True
        self.paused = False
        self.gato_pos = (self.n - 1, self.n - 1)  # Gato en la esquina inferior derecha
        self.raton_pos = (0, 0)  # Ratón en la esquina superior izquierda
        self.cuevita_pos = self.generar_cueva()  # Generar posición aleatoria para la cueva
        self.juego_activo = True
        self.historial_movimientos = {'gato': [], 'raton': []}  # Historial de movimientos de gato y ratón
        self.victoria_mostrada = False  # Control si ya se mostró el mensaje de victoria

    def generar_cueva(self):
        # Generar una posición aleatoria para la cueva, evitando posiciones del gato y el ratón
        while True:
            x = random.randint(1, self.n - 2)
            y = random.randint(1, self.n - 2)
            if (x, y) != self.gato_pos and (x, y) != self.raton_pos:
                return (x, y)

    def draw_board(self):
        # Dibujar el tablero y las piezas en la ventana pygame
        self.window.fill(WHITE)  # Llenar la ventana de blanco
        for i in range(self.n):
            for j in range(self.n):
                color = WHITE if (i + j) % 2 == 0 else GRAY
                pygame.draw.rect(self.window, color, (j * cell_size, i * cell_size, cell_size, cell_size))
        # Dibujar las imágenes del gato, el ratón y la cueva en sus posiciones correspondientes
        self.window.blit(gato_img, (self.gato_pos[1] * cell_size, self.gato_pos[0] * cell_size))
        self.window.blit(raton_img, (self.raton_pos[1] * cell_size, self.raton_pos[0] * cell_size))
        self.window.blit(cuevita_img, (self.cuevita_pos[1] * cell_size, self.cuevita_pos[0] * cell_size))

        # Resaltar cuando el ratón está al lado de la cueva
        if self.check_victory(self.gato_pos, self.raton_pos, self.cuevita_pos) == "Ratón":
            pygame.draw.rect(self.window, GREEN, (self.cuevita_pos[1] * cell_size, self.cuevita_pos[0] * cell_size, cell_size, cell_size), 3)

        # Resaltar cuando el gato atrapa al ratón
        if self.check_victory(self.gato_pos, self.raton_pos, self.cuevita_pos) == "Gato":
            pygame.draw.rect(self.window, RED, (self.raton_pos[1] * cell_size, self.raton_pos[0] * cell_size, cell_size, cell_size), 3)

    def obtener_movimientos(self, pos):
        # Obtener todos los movimientos posibles desde una posición dada en el tablero
        fila, columna = pos
        posibles_movimientos = [
            (fila - 1, columna),
            (fila + 1, columna),
            (fila, columna - 1),
            (fila, columna + 1)
        ]
        return [mov for mov in posibles_movimientos if 0 <= mov[0] < self.n and 0 <= mov[1] < self.n]

    def distancia_manhattan(self, pos1, pos2):
        #Calcular y devolver la distancia de Manhattan entre dos posiciones en el tablero
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) 
        #Esta medida es útil para determinar las posiciones más ventajosas y realizar movimientos óptimos en el juego.
        
    def mover_un_cuadro(self, pos_actual, pos_objetivo):
        # Mover una posición una celda hacia pos_objetivo desde pos_actual
        fila_actual, columna_actual = pos_actual
        fila_objetivo, columna_objetivo = pos_objetivo
        if fila_actual < fila_objetivo:
            nueva_fila = fila_actual + 1
        elif fila_actual > fila_objetivo:
            nueva_fila = fila_actual - 1
        else:
            nueva_fila = fila_actual

        if columna_actual < columna_objetivo:
            nueva_columna = columna_actual + 1
        elif columna_actual > columna_objetivo:
            nueva_columna = columna_actual - 1
        else:
            nueva_columna = columna_actual

        return nueva_fila, nueva_columna

    def minimax(self, raton_pos, gato_pos, cuevita_pos, maximizando, profundidad):
        # Algoritmo Minimax para tomar decisiones óptimas en el movimiento del ratón
        
        if profundidad == 0 or raton_pos == cuevita_pos or raton_pos == gato_pos:
            return self.evaluar_estado(raton_pos, gato_pos, cuevita_pos), raton_pos
            # Si se alcanza la profundidad máxima o el ratón ha llegado a la cueva o ha sido atrapado,
            # se evalúa el estado actual y se devuelve la evaluación y la posición del ratón

        if maximizando:
            max_eval = float('-inf')  # Inicializa la mejor evaluación posible como menos infinito
            mejor_movimiento = raton_pos  # Inicializa el mejor movimiento con la posición actual del ratón
            for movimiento in self.obtener_movimientos(raton_pos):
                # Itera sobre todos los movimientos posibles del ratón
                eval, _ = self.minimax(movimiento, gato_pos, cuevita_pos, False, profundidad - 1)
                # Llama recursivamente a minimax con el siguiente movimiento del ratón y cambia a minimizar
                if eval > max_eval:
                    max_eval = eval  # Actualiza la mejor evaluación si la evaluación actual es mayor
                    mejor_movimiento = movimiento  # Actualiza el mejor movimiento
            return max_eval, mejor_movimiento  # Devuelve la mejor evaluación y el mejor movimiento
        else:
            min_eval = float('inf')  # Inicializa la peor evaluación posible como infinito
            mejor_movimiento = gato_pos  # Inicializa el mejor movimiento con la posición actual del gato
            for movimiento in self.obtener_movimientos(gato_pos):
                # Itera sobre todos los movimientos posibles del gato
                eval, _ = self.minimax(raton_pos, movimiento, cuevita_pos, True, profundidad - 1)
                # Llama recursivamente a minimax con el siguiente movimiento del gato y cambia a maximizar
                if eval < min_eval:
                    min_eval = eval  # Actualiza la peor evaluación si la evaluación actual es menor
                    mejor_movimiento = movimiento  # Actualiza el mejor movimiento
            return min_eval, mejor_movimiento  # Devuelve la peor evaluación y el mejor movimiento

    def evaluar_estado(self, raton_pos, gato_pos, cuevita_pos):
        # Evaluar el estado actual del juego y devolver una puntuación basada en las posiciones
        if raton_pos == cuevita_pos:
            return 100  # Ratón gana
        elif raton_pos == gato_pos:
            return -100  # Gato gana
        return -self.distancia_manhattan(raton_pos, cuevita_pos) + self.distancia_manhattan(raton_pos, gato_pos)

    def mover_jugador(self, jugador):
        # Mover al jugador (gato o ratón) según el turno actual
        if jugador == "gato":
            siguiente_movimiento = self.mover_un_cuadro(self.gato_pos, self.raton_pos)
            if siguiente_movimiento != self.gato_pos:
                self.gato_pos = siguiente_movimiento
                self.historial_movimientos['gato'].append(self.gato_pos)
            if self.gato_pos == self.raton_pos:
                self.victoria("Gato")  # Verificar si el gato atrapa al ratón
        else:
            _, mejor_movimiento = self.minimax(self.raton_pos, self.gato_pos, self.cuevita_pos, True, 3)
            siguiente_movimiento = self.mover_un_cuadro(self.raton_pos, mejor_movimiento)
            if siguiente_movimiento != self.raton_pos:
                self.raton_pos = siguiente_movimiento
                self.historial_movimientos['raton'].append(self.raton_pos)
            ganador = self.check_victory(self.gato_pos, self.raton_pos, self.cuevita_pos)
            if ganador == "Ratón":
                self.victoria("Ratón")  # Verificar si el ratón llega a la cueva

    def victoria(self, ganador):
        # Mostrar mensaje de victoria y reiniciar el juego después de un tiempo
        font = pygame.font.SysFont(None, 36)  #Fuente para el texto en la ventana
        if ganador == "Gato":
            texto = font.render("¡El gato ha atrapado al ratón!", True, (255, 0, 0))
        else:
            texto = font.render("¡El ratón ha llegado a la cueva!", True, (255, 0, 0))
        self.window.blit(texto, (50, 250))  # Mostrar el texto en la ventana
        pygame.display.flip()
        pygame.time.wait(3000)  # Esperar 3 segundos antes de reiniciar el juego

        pygame.time.wait(2000)  # Esperar un poco más antes de reiniciar el juego

        self.reset_game()  # Reiniciar el juego

    def toggle_pause(self):
        # Alternar entre pausar y reanudar el juego
        self.paused = not self.paused

    def jugar(self):
        # Método principal para ejecutar el juego
        clock = pygame.time.Clock()  # Inicializar el reloj de pygame
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    pygame.quit()
                    #Limpia e inicializa el entorno de Pygame y cierra todas las ventanas de Pygame.
                    sys.exit() 
                    #Llama a la función sys.exit(),detiene la ejecución de manera ordenada.
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.toggle_pause()  # Pausar o reanudar con la tecla Espacio

            if not self.paused and self.juego_activo:
                if self.turno_gato:
                    self.mover_jugador("gato")  # Turno del gato
                else:
                    self.mover_jugador("raton")  # Turno del ratón

                # Verificar si algún jugador ha ganado
                if self.check_victory(self.gato_pos, self.raton_pos, self.cuevita_pos):
                    self.victoria(self.check_victory(self.gato_pos, self.raton_pos, self.cuevita_pos))
                    # Mostrar mensaje de victoria
                    self.juego_activo = False  # Finalizar el juego

                self.turno_gato = not self.turno_gato  # Cambiar el turno

            self.draw_board()  # Dibujar el tablero en cada iteración
            pygame.display.update()  # Actualizar la pantalla
            clock.tick(1)  # Reducir la tasa de refresco para una mejor visualización

    def check_victory(self, gato_pos, raton_pos, cuevita_pos):
        # Verificar si hay un ganador basado en las posiciones actuales
        if gato_pos == raton_pos:
            return "Gato"  # Gato atrapa al ratón
        elif raton_pos == cuevita_pos:
            return "Ratón"  # Ratón llega a la cueva
        
        x, y = cuevita_pos
        rx, ry = raton_pos
        # Estas líneas son fundamentales para determinar si el ratón ha alcanzado su objetivo (la cueva)
        # y para manejar la lógica de victoria en el juego
        
        # Verificar si el ratón está adyacente a la cueva (sin diagonales)
        if (rx == x and abs(ry - y) == 1) or (ry == y and abs(rx - x) == 1):
            return "Ratón"  # Ratón está adyacente a la cueva

        return None

# Crear e iniciar el juego
juego = JuegoGatoRaton(6)
juego.jugar()