from PIL import Image
import os
import sys
import pygame
import time

# Инициализация pygame
pygame.init()

def create_mosaic_texture(base_texture, output_size=(1920, 1080), reverse_direction=False):
    """
    Создает мозаику из текстуры с возможностью размножения в разных направлениях
    """
    # Получаем размеры исходной текстуры
    tex_width, tex_height = base_texture.size
    
    # Создаем холст для мозаики
    mosaic = Image.new('RGB', output_size)
    
    if not reverse_direction:
        # Классическое размножение: сверху вниз, слева направо
        for y in range(0, output_size[1], tex_height):
            for x in range(0, output_size[0], tex_width):
                mosaic.paste(base_texture, (x, y))
    else:
        # Обратное размножение: снизу вверх, справа налево
        for y in range(output_size[1] - tex_height, -tex_height, -tex_height):
            for x in range(output_size[0] - tex_width, -tex_width, -tex_width):
                mosaic.paste(base_texture, (x, y))
    
    return mosaic

def apply_mask_correct(mosaic, mask):
    """
    Применяет маску к мозаичной текстуре
    """
    # Изменяем размер маски под размер мозаики
    mask_resized = mask.resize(mosaic.size, Image.Resampling.LANCZOS)
    
    # Конвертируем мозаику в RGBA
    mosaic_rgba = mosaic.convert('RGBA')
    
    # Создаем временное изображение для композиции
    if mask_resized.mode == 'RGBA':
        # Если маска уже в RGBA, используем ее альфа-канал
        _, _, _, mask_alpha = mask_resized.split()
        result = Image.merge('RGBA', (*mosaic_rgba.split()[:3], mask_alpha))
    else:
        # Если маска в оттенках серого, используем ее как альфа-канал
        mask_gray = mask_resized.convert('L')
        result = Image.merge('RGBA', (*mosaic_rgba.split()[:3], mask_gray))
    
    return result

def pil_to_pygame(pil_image):
    """Конвертирует изображение PIL в поверхность Pygame"""
    mode = pil_image.mode
    size = pil_image.size
    data = pil_image.tobytes()
    
    if mode == 'RGB':
        return pygame.image.fromstring(data, size, mode)
    elif mode == 'RGBA':
        return pygame.image.fromstring(data, size, mode)
    else:
        # Конвертируем в RGB если другой режим
        pil_image = pil_image.convert('RGB')
        return pygame.image.fromstring(pil_image.tobytes(), size, 'RGB')

class TextureDemo:
    def __init__(self, width=1280, height=720):
        self.screen_width = width
        self.screen_height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Демонстрация текстур")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.textures = []
        self.current_background = 0
        self.last_switch_time = time.time()
        self.switch_interval = 0.1  # 0.1 секунды
        self.animation_paused = False
        
    def add_texture(self, texture_surface, name):
        """Добавляет текстуру в демонстрацию"""
        # Масштабируем текстуру под размер окна
        scaled_texture = pygame.transform.scale(texture_surface, (self.screen_width, self.screen_height))
        self.textures.append((scaled_texture, name))
    
    def toggle_animation(self):
        """Включает/выключает анимацию"""
        self.animation_paused = not self.animation_paused
        return self.animation_paused
    
    def run_demo(self):
        """Запускает демонстрационный цикл"""
        print("\n🎬 Запуск демонстрации...")
        print("   Управление: ПРОБЕЛ - пауза, ESC - выход")
        
        while self.running:
            current_time = time.time()
            
            # Переключаем фоновую текстуру каждые 0.1 секунды если анимация не на паузе
            if not self.animation_paused and current_time - self.last_switch_time > self.switch_interval:
                self.current_background = (self.current_background + 1) % 2
                self.last_switch_time = current_time
            
            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        # Пауза/продолжение анимации
                        self.toggle_animation()
            
            # Отрисовка
            self.screen.fill((0, 0, 0))
            
            # Рисуем текущую фоновую текстуру (нормальную или обратную)
            if len(self.textures) >= 3:
                # Фоновая текстура (0 или 1 индекс)
                bg_texture, bg_name = self.textures[self.current_background]
                self.screen.blit(bg_texture, (0, 0))
                
                # Поверхностная текстура с маской (2 индекс)
                overlay_texture, overlay_name = self.textures[2]
                self.screen.blit(overlay_texture, (0, 0))
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

def main():
    """
    Основная функция скрипта
    """
    print("=== Генератор мозаичных текстур 1920x1080 ===\n")
    print("Создает три варианта размножения текстуры + демонстрация")
    print("=" * 60)
    
    # Запрашиваем пути к файлам
    if len(sys.argv) > 2:
        texture_path = sys.argv[1]
        mask_path = sys.argv[2]
    else:
        texture_path = input("Введите путь к файлу текстуры: ")
        mask_path = input("Введите путь к файлу маски (PNG): ")
    
    # Проверяем существование файлов
    if not os.path.exists(texture_path):
        print(f"\n❌ Ошибка: Файл текстуры '{texture_path}' не найден!")
        input("Нажмите Enter для выхода...")
        return
    
    if not os.path.exists(mask_path):
        print(f"\n❌ Ошибка: Файл маски '{mask_path}' не найден!")
        input("Нажмите Enter для выхода...")
        return
    
    try:
        # Загружаем текстуру и маску
        base_texture = Image.open(texture_path)
        mask = Image.open(mask_path)
        
        print(f"\n✅ Файлы загружены:")
        print(f"   Текстура: {os.path.basename(texture_path)}")
        print(f"   Размер текстуры: {base_texture.size}")
        print(f"   Маска: {os.path.basename(mask_path)}")
        print(f"   Размер маски: {mask.size}")
        print(f"\n🎯 Создание текстур 1920x1080...")
        
    except Exception as e:
        print(f"\n❌ Ошибка загрузки файлов: {e}")
        input("Нажмите Enter для выхода...")
        return
    
    # Создаем папку для результатов
    output_dir = 'mosaic_textures'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Создаем текстуры
    print("\n1. Создание мозаичной текстуры...", end=" ")
    mosaic_normal = create_mosaic_texture(base_texture, (1920, 1080), reverse_direction=False)
    mosaic_normal.save(f'{output_dir}/mosaic_normal_1920x1080.png', 'PNG')
    print("готово!")
    
    print("2. Создание текстуры с маской...", end=" ")
    mosaic_with_mask = apply_mask_correct(mosaic_normal, mask)
    mosaic_with_mask.save(f'{output_dir}/mosaic_with_mask_1920x1080.png', 'PNG')
    print("готово!")
    
    print("3. Создание обратной мозаики...", end=" ")
    mosaic_reverse = create_mosaic_texture(base_texture, (1920, 1080), reverse_direction=True)
    mosaic_reverse.save(f'{output_dir}/mosaic_reverse_1920x1080.png', 'PNG')
    print("готово!")
    
    # Сохраняем информацию о файлах
    print(f"\n✅ Все текстуры успешно созданы!")
    print(f"📁 Результаты сохранены в папку: '{output_dir}'")
    
    # Запускаем демонстрацию
    demo = TextureDemo(1280, 720)
    
    # Добавляем текстуры в демонстрацию
    demo.add_texture(pil_to_pygame(mosaic_normal), "Обычная мозаика")
    demo.add_texture(pil_to_pygame(mosaic_reverse), "Обратная мозаика")
    demo.add_texture(pil_to_pygame(mosaic_with_mask), "Текстура с маской")
    
    # Запускаем демонстрационный цикл
    demo.run_demo()
    
    print("\n🎬 Демонстрация завершена!")
    print(f"\nСозданные файлы (1920x1080):")
    print(f"  • mosaic_normal_1920x1080.png - обычная мозаика")
    print(f"  • mosaic_with_mask_1920x1080.png - мозаика с вырезанной маской")
    print(f"  • mosaic_reverse_1920x1080.png - обратная мозаика")
    
    print(f"\n📂 Расположение результатов:")
    print(f"  {os.path.abspath(output_dir)}")
    
    input("\nНажмите Enter для завершения...")

if __name__ == "__main__":
    main()
